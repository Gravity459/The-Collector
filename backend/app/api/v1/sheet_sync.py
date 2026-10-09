"""Google Sheet sync routes (admin, plus one cron-only sweep)."""
from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query

from app.core.deps import get_sheet_sync_service, require_cron_secret, require_role
from app.models.users import User
from app.schemas.common import Page, PageParams
from app.schemas.sheet_sync import JobStatus, SheetSyncJobOut, SweepResult
from app.services.sheet_sync_service import ATTENTION_STATUSES, SheetSyncService

router = APIRouter(tags=["sheet-sync"])


@router.post("/collections/{collection_id}/sheet-sync", response_model=SheetSyncJobOut)
async def run_collection_sync(
    collection_id: uuid.UUID,
    _admin: User = Depends(require_role("admin")),
    service: SheetSyncService = Depends(get_sheet_sync_service),
) -> SheetSyncJobOut:
    return await service.run_for_collection(collection_id)


@router.get("/sheet-sync/jobs", response_model=Page[SheetSyncJobOut])
async def list_sync_jobs(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    status: list[JobStatus] | None = Query(default=None),
    _admin: User = Depends(require_role("admin")),
    service: SheetSyncService = Depends(get_sheet_sync_service),
) -> Page[SheetSyncJobOut]:
    return await service.list_jobs(
        PageParams(page=page, size=size),
        statuses=tuple(status) if status else ATTENTION_STATUSES,
    )


@router.post("/sheet-sync/jobs/{job_id}/overwrite", response_model=SheetSyncJobOut)
async def overwrite_sync_job(
    job_id: uuid.UUID,
    _admin: User = Depends(require_role("admin")),
    service: SheetSyncService = Depends(get_sheet_sync_service),
) -> SheetSyncJobOut:
    return await service.overwrite(job_id)


@router.post("/sheet-sync/jobs/{job_id}/retry", response_model=SheetSyncJobOut)
async def retry_sync_job(
    job_id: uuid.UUID,
    _admin: User = Depends(require_role("admin")),
    service: SheetSyncService = Depends(get_sheet_sync_service),
) -> SheetSyncJobOut:
    return await service.retry(job_id)


@router.post(
    "/sheet-sync/sweep",
    response_model=SweepResult,
    dependencies=[Depends(require_cron_secret)],
)
async def sweep_sync_jobs(
    service: SheetSyncService = Depends(get_sheet_sync_service),
) -> SweepResult:
    return await service.sweep()
