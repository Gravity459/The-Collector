"""Mirror approved collections into the Google Sheet.

Approval is the source of truth; the sheet is a mirror. A job records one
write per approved collection. Processing it:

    lock -> read grid -> resolve Layout Map -> find house row x month column
         -> (append missing month columns) -> refuse non-empty cells -> write

Writes only ever land on a house row x month column cell, or on the header
row of a month column this service just created. Nothing else is written,
so total and summary rows are never touched.
"""
from __future__ import annotations

import asyncio
import uuid
from collections import Counter
from typing import Literal

from fastapi import HTTPException, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings
from app.integrations.ai.planner import LayoutPlanner, PlannerError
from app.integrations.ai.schemas import LayoutMap, MonthColumn
from app.integrations.google_sheets import SheetsClient, SheetsError
from app.integrations.sheet_grid import (
    Grid,
    a1,
    cell,
    col_to_index,
    fingerprint,
    index_to_col,
    next_month,
    redact_for_ai,
    render_header,
    validate_layout,
)
from app.models.sheet_layout import SheetLayout
from app.models.sheet_sync_job import SheetSyncJob
from app.repositories.sheet_layout_repo import SheetLayoutRepository
from app.repositories.sheet_sync_repo import SheetSyncRepository
from app.schemas.common import Page, PageParams
from app.schemas.sheet_sync import SheetSyncJobOut, SweepResult
from app.utils.pagination import build_page

# one sheet writer at a time, across requests and the cron sweep
SHEET_LOCK_KEY = 7_340_211_905
# planner answers are checked; a failed check gets one corrected retry
_PLANNER_ATTEMPTS = 2
_MAX_ERROR_CHARS = 1000

Mode = Literal["auto", "retry", "overwrite"]
ATTENTION_STATUSES = ("needs_review", "failed")


class LayoutUnreadable(Exception):
    def __init__(self, errors: list[str]) -> None:
        super().__init__("; ".join(errors))
        self.errors = errors


def _job_out(job: SheetSyncJob) -> SheetSyncJobOut:
    c = job.collection
    return SheetSyncJobOut(
        id=job.id,
        collection_id=job.collection_id,
        house_number=c.house.house_number,
        period_month=c.period_month.strftime("%Y-%m"),
        amount=c.amount,
        status=job.status,  # type: ignore[arg-type]
        reason=job.reason,  # type: ignore[arg-type]
        target_cell=job.target_cell,
        existing_value=job.existing_value,
        error=job.error,
        attempts=job.attempts,
        updated_at=job.updated_at,
    )


class SheetSyncService:
    def __init__(
        self,
        db: AsyncSession,
        *,
        sheets: SheetsClient,
        planner: LayoutPlanner,
        settings: Settings,
    ) -> None:
        self.db = db
        self.sheets = sheets
        self.planner = planner
        self.settings = settings
        self.jobs = SheetSyncRepository(db)
        self.layouts = SheetLayoutRepository(db)

    # --- entry points ------------------------------------------------------

    async def run_for_collection(self, collection_id: uuid.UUID) -> SheetSyncJobOut:
        """Sync one approved collection now (fired by the UI right after approve)."""
        self._ensure_enabled()
        job = await self.jobs.get_by_collection(collection_id)
        if job is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No sheet sync for this collection",
            )
        return await self.process(job.id, mode="auto")

    async def retry(self, job_id: uuid.UUID) -> SheetSyncJobOut:
        self._ensure_enabled()
        return await self.process(job_id, mode="retry")

    async def overwrite(self, job_id: uuid.UUID) -> SheetSyncJobOut:
        self._ensure_enabled()
        return await self.process(job_id, mode="overwrite")

    async def sweep(self) -> SweepResult:
        """Cron: process pending jobs and retry failed ones with attempts left."""
        self._ensure_enabled()
        ids = await self.jobs.list_retryable_ids(
            max_attempts=self.settings.sheet_sync_max_attempts
        )
        # sequential on purpose: one writer at a time, and column inserts must not race
        outcomes = Counter()
        for job_id in ids:
            outcomes[(await self.process(job_id, mode="auto")).status] += 1
        return SweepResult(
            processed=len(ids),
            done=outcomes["done"],
            needs_review=outcomes["needs_review"],
            failed=outcomes["failed"],
        )

    async def list_jobs(
        self, params: PageParams, *, statuses: tuple[str, ...] = ATTENTION_STATUSES
    ) -> Page[SheetSyncJobOut]:
        rows, total = await self.jobs.list(
            statuses=statuses, offset=params.offset, limit=params.size
        )
        return build_page(
            [_job_out(j) for j in rows], total=total, page=params.page, size=params.size
        )

    # --- processing --------------------------------------------------------

    async def process(self, job_id: uuid.UUID, *, mode: Mode) -> SheetSyncJobOut:
        """Run one job under the sheet lock. Commits its own transaction(s)."""
        try:
            await self.db.execute(
                text("SELECT pg_advisory_xact_lock(:key)"), {"key": SHEET_LOCK_KEY}
            )
            job = await self.jobs.get(job_id)
            if job is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Sheet sync job not found"
                )
            if self._should_run(job, mode):
                await self._sync(job, overwrite=mode == "overwrite")
            await self.db.commit()  # also releases the lock
        except (SheetsError, PlannerError) as exc:
            # whatever half-finished state the attempt left is discarded;
            # record the failure on its own so the cron can retry it
            await self.db.rollback()
            job = await self.jobs.get(job_id)
            if job is None:
                raise
            job.status = "failed"
            job.reason = None
            job.attempts += 1
            job.error = str(exc)[:_MAX_ERROR_CHARS]
            await self.db.commit()
        job = await self.jobs.get(job_id)
        assert job is not None
        return _job_out(job)

    def _should_run(self, job: SheetSyncJob, mode: Mode) -> bool:
        if mode == "auto":
            # done needs nothing; needs_review waits for the admin
            return job.status in ("pending", "failed")
        if mode == "retry":
            if job.status == "done":
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="This payment is already in the sheet",
                )
            return True
        # overwrite: only ever to resolve a conflict the admin has looked at
        if job.status != "needs_review" or job.reason != "conflict":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Overwrite is only for a cell that already had a value",
            )
        return True

    async def _sync(self, job: SheetSyncJob, *, overwrite: bool) -> None:
        collection = job.collection
        house = collection.house.house_number
        month = collection.period_month.strftime("%Y-%m")
        job.attempts += 1

        # one HTTP read and one DB read in parallel; both settle before any
        # error propagates, so the session is idle if we roll back
        grid, saved = await asyncio.gather(
            self.sheets.read_grid(),
            self.layouts.get_latest(self.settings.google_sheet_id, self.settings.google_sheet_tab),
            return_exceptions=True,
        )
        for result in (grid, saved):
            if isinstance(result, BaseException):
                raise result
        try:
            layout = await self._resolve_layout(grid, saved)
        except LayoutUnreadable as exc:
            return self._review(
                job, "layout_unreadable", error="; ".join(exc.errors[:10])
            )

        row = layout.row_for(house)
        if row is None:
            return self._review(
                job, "house_not_in_sheet", error=f"S-{house} is not in the sheet's house column"
            )

        column = layout.column_for(month)
        if column is None:
            newest = layout.latest_month()
            if newest is None or month < newest:
                return self._review(
                    job,
                    "month_column_missing",
                    error=f"No column for {month}, and it is older than the newest "
                    f"month column ({newest})",
                )
            layout = await self._append_month_columns(layout, grid, through=month)
            column = layout.column_for(month)
            assert column is not None

        target = a1(row, column)
        existing = cell(grid, row, column).strip()
        if existing and not overwrite:
            return self._review(job, "conflict", target_cell=target, existing_value=existing)

        await self.sheets.write_cell(target, collection.amount)
        job.status = "done"
        job.reason = None
        job.error = None
        job.target_cell = target
        job.existing_value = existing or None

    @staticmethod
    def _review(
        job: SheetSyncJob,
        reason: str,
        *,
        error: str | None = None,
        target_cell: str | None = None,
        existing_value: str | None = None,
    ) -> None:
        job.status = "needs_review"
        job.reason = reason
        job.error = error[:_MAX_ERROR_CHARS] if error else None
        job.target_cell = target_cell
        job.existing_value = existing_value[:255] if existing_value else None

    # --- layout ------------------------------------------------------------

    async def _resolve_layout(self, grid: Grid, saved: SheetLayout | None) -> LayoutMap:
        """The saved map while the sheet's structure is unchanged; otherwise
        ask the AI for a new one, check it, and save it."""
        if saved is not None:
            layout = LayoutMap.model_validate(saved.layout)
            if fingerprint(grid, layout.header_row, layout.house_column) == saved.fingerprint:
                return layout

        grid_text = redact_for_ai(grid)
        feedback: str | None = None
        errors: list[str] = []
        for _ in range(_PLANNER_ATTEMPTS):
            layout = await self.planner.build_layout(grid_text, feedback)
            errors = validate_layout(layout, grid)
            if not errors:
                await self._save_layout(layout, grid, source="ai")
                return layout
            feedback = "\n".join(f"- {e}" for e in errors[:20])
        raise LayoutUnreadable(errors)

    async def _append_month_columns(
        self, layout: LayoutMap, grid: Grid, *, through: str
    ) -> LayoutMap:
        """Create every month column after the newest one up to `through`,
        right after the last month column, and update the map in code."""
        newest = layout.latest_month()
        last_col = layout.column_for(newest) if newest else None
        assert newest is not None and last_col is not None
        months: list[str] = []
        m = next_month(newest)
        while m <= through:
            months.append(m)
            m = next_month(m)

        start = col_to_index(last_col) + 1
        await self.sheets.insert_columns(start, len(months))
        # mirror the insert in our copy of the grid
        for r in grid:
            r[start:start] = [""] * len(months)

        new_columns = []
        for offset, month in enumerate(months):
            col = index_to_col(start + offset)
            heading = render_header(layout.month_header_template, month)
            await self.sheets.write_cell(a1(layout.header_row, col), heading)
            grid[layout.header_row - 1][start + offset] = heading
            new_columns.append(MonthColumn(month=month, column=col))

        def shifted(col: str) -> str:
            i = col_to_index(col)
            return index_to_col(i + len(months)) if i >= start else col

        updated = layout.model_copy(
            update={
                "house_column": shifted(layout.house_column),
                "month_columns": [
                    MonthColumn(month=mc.month, column=shifted(mc.column))
                    for mc in layout.month_columns
                ]
                + new_columns,
            }
        )
        await self._save_layout(updated, grid, source="code")
        return updated

    async def _save_layout(self, layout: LayoutMap, grid: Grid, *, source: str) -> None:
        await self.layouts.save(
            spreadsheet_id=self.settings.google_sheet_id,
            tab_name=self.settings.google_sheet_tab,
            fingerprint=fingerprint(grid, layout.header_row, layout.house_column),
            layout=layout.model_dump(),
            source=source,
        )

    def _ensure_enabled(self) -> None:
        if not self.settings.sheet_sync_enabled:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Sheet sync is disabled"
            )
