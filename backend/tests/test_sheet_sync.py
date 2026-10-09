"""Sheet sync: approve -> job -> write into the (fake) Google Sheet."""
from datetime import datetime, timezone

import pytest
from fastapi import Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.deps import get_sheet_sync_service
from app.db.session import get_db
from app.integrations.ai.planner import PlannerError
from app.integrations.google_sheets import SheetsError
from app.integrations.sheet_grid import next_month
from app.main import app
from app.models.sheet_layout import SheetLayout
from app.services.sheet_sync_service import SheetSyncService
from tests.sheet_fakes import FakePlanner, FakeSheets, correct_layout

CRON = {"X-Cron-Secret": "cron-test-secret"}
# house rows of the fixture: 3..33; header row 2; totals/summary below
HOUSE_ROWS = range(3, 34)


def _auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _this_month() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m")


@pytest.fixture
def sync_on(monkeypatch):
    settings = get_settings()
    monkeypatch.setattr(settings, "sheet_sync_enabled", True)
    monkeypatch.setattr(settings, "google_sheet_id", "test-sheet")
    monkeypatch.setattr(settings, "google_sheet_tab", "Sheet1")
    monkeypatch.setattr(settings, "cron_secret", "cron-test-secret")
    monkeypatch.setattr(settings, "sheet_sync_max_attempts", 2)
    return settings


@pytest.fixture
def sheets():
    return FakeSheets()


@pytest.fixture
def planner(sheets):
    return FakePlanner(sheets)


@pytest.fixture(autouse=True)
def _fake_service(sheets, planner):
    def _build(db: AsyncSession = Depends(get_db)) -> SheetSyncService:
        return SheetSyncService(db, sheets=sheets, planner=planner, settings=get_settings())

    app.dependency_overrides[get_sheet_sync_service] = _build
    yield
    app.dependency_overrides.pop(get_sheet_sync_service, None)


async def _approved(client, admin_token, collector_token, *, house, amount, month=None):
    body = {"house_number": house, "amount": amount}
    if month:
        body["period_month"] = month
    created = await client.post(
        "/api/v1/collections", headers=_auth(collector_token), json=body
    )
    assert created.status_code == 201, created.text
    cid = created.json()["id"]
    approved = await client.patch(
        f"/api/v1/collections/{cid}/approve", headers=_auth(admin_token)
    )
    assert approved.status_code == 200
    return cid, approved.json()


async def _sync(client, admin_token, cid):
    resp = await client.post(
        f"/api/v1/collections/{cid}/sheet-sync", headers=_auth(admin_token)
    )
    assert resp.status_code == 200, resp.text
    return resp.json()


def _assert_only_safe_writes(sheets: FakeSheets, header_row: int = 2) -> None:
    """The core promise: writes land on house rows, or a new month header."""
    for a1, _value in sheets.writes:
        row = int("".join(ch for ch in a1 if ch.isdigit()))
        assert row in HOUSE_ROWS or row == header_row, a1


async def _layout_rows(db_session) -> list[SheetLayout]:
    result = await db_session.execute(select(SheetLayout).order_by(SheetLayout.created_at))
    return list(result.scalars().all())


# --- approve ------------------------------------------------------------------


async def test_approve_creates_job_only_when_enabled(
    client, admin_token, collector_token, monkeypatch
):
    _, off = await _approved(client, admin_token, collector_token, house=15, amount=4200)
    assert off["sheet_sync"] is None

    monkeypatch.setattr(get_settings(), "sheet_sync_enabled", True)
    cid, on = await _approved(
        client, admin_token, collector_token, house=24, amount=4600, month="2026-08"
    )
    assert on["sheet_sync"] == {"status": "pending", "reason": None, "target_cell": None}

    listing = await client.get(
        "/api/v1/collections?approved=true&month=2026-08", headers=_auth(admin_token)
    )
    assert listing.json()["items"][0]["sheet_sync"]["status"] == "pending"


async def test_disabled_endpoints_refuse(client, admin_token, collector_token):
    cid, _ = await _approved(client, admin_token, collector_token, house=15, amount=4200)
    resp = await client.post(
        f"/api/v1/collections/{cid}/sheet-sync", headers=_auth(admin_token)
    )
    assert resp.status_code == 409


# --- happy path & layout reuse ------------------------------------------------


async def test_writes_empty_cell_and_reuses_layout(
    client, db_session, admin_token, collector_token, sync_on, sheets, planner
):
    # S-15 has no September amount yet: row 9, column M
    cid, _ = await _approved(
        client, admin_token, collector_token, house=15, amount=4600, month="2026-09"
    )
    job = await _sync(client, admin_token, cid)
    assert job["status"] == "done"
    assert job["target_cell"] == "M9"
    assert sheets.writes == [("M9", 4600)]
    assert len(planner.calls) == 1
    assert [row.source for row in await _layout_rows(db_session)] == ["ai"]

    # the collection now reports where it landed
    listing = await client.get(
        "/api/v1/collections?approved=true&month=2026-09", headers=_auth(admin_token)
    )
    assert listing.json()["items"][0]["sheet_sync"] == {
        "status": "done",
        "reason": None,
        "target_cell": "M9",
    }

    # amounts typed into the sheet don't change its structure: saved map reused
    sheets.grid[8][11] = "4200"  # someone fills S-15 August by hand
    cid2, _ = await _approved(
        client, admin_token, collector_token, house=1, amount=3000, month="2026-07"
    )
    sheets.grid[2][10] = ""  # make S-1 July empty so the write can land
    job2 = await _sync(client, admin_token, cid2)
    assert job2["status"] == "done" and job2["target_cell"] == "K3"
    assert len(planner.calls) == 1

    # syncing again is a no-op
    again = await _sync(client, admin_token, cid)
    assert again["status"] == "done"
    assert len(sheets.writes) == 2
    _assert_only_safe_writes(sheets)


# --- conflicts ------------------------------------------------------------------


async def test_conflict_waits_for_overwrite(
    client, admin_token, collector_token, sync_on, sheets
):
    # S-24 September already says 4600
    cid, _ = await _approved(
        client, admin_token, collector_token, house=24, amount=4800, month="2026-09"
    )
    job = await _sync(client, admin_token, cid)
    assert job["status"] == "needs_review"
    assert job["reason"] == "conflict"
    assert job["target_cell"] == "M13"
    assert job["existing_value"] == "4600"
    assert sheets.writes == []

    # auto runs never touch a job waiting for review
    assert (await _sync(client, admin_token, cid))["status"] == "needs_review"

    review = await client.get("/api/v1/sheet-sync/jobs", headers=_auth(admin_token))
    assert [j["id"] for j in review.json()["items"]] == [job["id"]]

    done = await client.post(
        f"/api/v1/sheet-sync/jobs/{job['id']}/overwrite", headers=_auth(admin_token)
    )
    assert done.status_code == 200
    assert done.json()["status"] == "done"
    assert sheets.value("M13") == "4800"
    assert sheets.writes == [("M13", 4800)]

    # overwrite is only for conflicts awaiting review
    twice = await client.post(
        f"/api/v1/sheet-sync/jobs/{job['id']}/overwrite", headers=_auth(admin_token)
    )
    assert twice.status_code == 409
    review = await client.get("/api/v1/sheet-sync/jobs", headers=_auth(admin_token))
    assert review.json()["total"] == 0


@pytest.mark.parametrize("house, existing", [(41, "HOUSE EMPTY"), (37, "-")])
async def test_placeholder_text_is_a_conflict(
    client, admin_token, collector_token, sync_on, sheets, house, existing
):
    cid, _ = await _approved(
        client, admin_token, collector_token, house=house, amount=4600, month="2026-09"
    )
    job = await _sync(client, admin_token, cid)
    assert (job["status"], job["reason"], job["existing_value"]) == (
        "needs_review",
        "conflict",
        existing,
    )
    assert sheets.writes == []


# --- month columns ----------------------------------------------------------------


async def test_creates_missing_future_month_columns(
    client, db_session, admin_token, collector_token, sync_on, sheets, planner
):
    month = _this_month()  # the fixture's newest column is Sep 26
    cid, _ = await _approved(client, admin_token, collector_token, house=5, amount=4600)
    job = await _sync(client, admin_token, cid)
    assert job["status"] == "done"

    expected = []
    m = next_month("2026-09")
    while m <= month:
        expected.append(m)
        m = next_month(m)
    assert sheets.inserts == [(13, len(expected))]  # right after column M
    headers = sheets.grid[1][13 : 13 + len(expected)]
    assert headers == [
        f"Amount ({datetime.strptime(x, '%Y-%m'):%b %y})" for x in expected
    ]
    target_col = chr(ord("N") + len(expected) - 1)
    assert job["target_cell"] == f"{target_col}4"
    # totals and summaries under the new columns stay empty
    for r in range(34, len(sheets.grid)):
        assert sheets.grid[r][13 : 13 + len(expected)] == [""] * len(expected)
    _assert_only_safe_writes(sheets)

    layouts = await _layout_rows(db_session)
    assert [row.source for row in layouts] == ["ai", "code"]

    # the code-made map matches the new structure: no AI call for the next one
    cid2, _ = await _approved(client, admin_token, collector_token, house=6, amount=4600)
    job2 = await _sync(client, admin_token, cid2)
    assert job2["status"] == "done" and job2["target_cell"] == f"{target_col}5"
    assert len(planner.calls) == 1
    assert len(sheets.inserts) == 1


async def test_missing_past_month_needs_review(
    client, admin_token, collector_token, sync_on, sheets
):
    cid, _ = await _approved(
        client, admin_token, collector_token, house=5, amount=4000, month="2025-12"
    )
    job = await _sync(client, admin_token, cid)
    assert (job["status"], job["reason"]) == ("needs_review", "month_column_missing")
    assert sheets.writes == [] and sheets.inserts == []


# --- house not in sheet ---------------------------------------------------------


async def test_unknown_house_then_retry_after_fixing_sheet(
    client, admin_token, collector_token, sync_on, sheets, planner
):
    cid, _ = await _approved(
        client, admin_token, collector_token, house=99, amount=4600, month="2026-09"
    )
    job = await _sync(client, admin_token, cid)
    assert (job["status"], job["reason"]) == ("needs_review", "house_not_in_sheet")

    # admin adds S-99 in the blank row under the house table
    sheets.grid[33][:4] = ["32", "New resident", "S-99", ""]
    retried = await client.post(
        f"/api/v1/sheet-sync/jobs/{job['id']}/retry", headers=_auth(admin_token)
    )
    assert retried.json()["status"] == "done"
    assert retried.json()["target_cell"] == "M34"
    # the house column changed, so the layout was read again
    assert len(planner.calls) == 2

    done_retry = await client.post(
        f"/api/v1/sheet-sync/jobs/{job['id']}/retry", headers=_auth(admin_token)
    )
    assert done_retry.status_code == 409


# --- the AI's answer is checked ---------------------------------------------------


async def test_bad_layout_gets_one_corrected_retry(
    client, admin_token, collector_token, sync_on, sheets, planner
):
    wrong = correct_layout(sheets.grid)
    wrong.house_rows[0].row = 4  # claims S-1 sits on S-5's row
    planner.queued = [wrong]
    cid, _ = await _approved(
        client, admin_token, collector_token, house=15, amount=4600, month="2026-09"
    )
    job = await _sync(client, admin_token, cid)
    assert job["status"] == "done"
    assert len(planner.calls) == 2
    first_feedback, second_feedback = planner.calls[0][1], planner.calls[1][1]
    assert first_feedback is None
    assert "row 4" in second_feedback and "S-1" in second_feedback


async def test_layout_unreadable_after_two_bad_answers(
    client, admin_token, collector_token, sync_on, sheets, planner
):
    wrong = correct_layout(sheets.grid)
    wrong.month_columns[0].month = "2025-01"
    planner.queued = [wrong, wrong]
    cid, _ = await _approved(
        client, admin_token, collector_token, house=15, amount=4600, month="2026-09"
    )
    job = await _sync(client, admin_token, cid)
    assert (job["status"], job["reason"]) == ("needs_review", "layout_unreadable")
    assert "2025-01" in job["error"]
    assert sheets.writes == []


async def test_ai_never_sees_names_or_phones(
    client, admin_token, collector_token, sync_on, planner
):
    cid, _ = await _approved(
        client, admin_token, collector_token, house=15, amount=4600, month="2026-09"
    )
    await _sync(client, admin_token, cid)
    sent = planner.calls[0][0]
    assert "Resident" not in sent
    assert "0300000" not in sent
    assert "S-24" in sent and "Amount (Sep 26)" in sent and "Total Collection" in sent


# --- failures & the cron sweep ----------------------------------------------------


async def test_failures_retry_via_sweep_until_max_attempts(
    client, admin_token, collector_token, sync_on, sheets
):
    cid, _ = await _approved(
        client, admin_token, collector_token, house=15, amount=4600, month="2026-09"
    )
    sheets.fail = SheetsError("Google Sheets unreachable: boom")
    job = await _sync(client, admin_token, cid)
    assert (job["status"], job["attempts"]) == ("failed", 1)
    assert "boom" in job["error"]

    swept = await client.post("/api/v1/sheet-sync/sweep", headers=CRON)
    assert swept.json() == {"processed": 1, "done": 0, "needs_review": 0, "failed": 1}

    # max_attempts=2 reached: the sweep leaves it alone, it stays visible for review
    swept = await client.post("/api/v1/sheet-sync/sweep", headers=CRON)
    assert swept.json()["processed"] == 0
    review = await client.get("/api/v1/sheet-sync/jobs", headers=_auth(admin_token))
    assert review.json()["items"][0]["status"] == "failed"

    # the admin's Retry still works once Google is back
    sheets.fail = None
    retried = await client.post(
        f"/api/v1/sheet-sync/jobs/{job['id']}/retry", headers=_auth(admin_token)
    )
    assert retried.json()["status"] == "done"
    assert sheets.writes == [("M9", 4600)]


async def test_sweep_processes_pending_jobs(
    client, admin_token, collector_token, sync_on, sheets, planner
):
    for house in (15, 24):
        await _approved(
            client, admin_token, collector_token, house=house, amount=4600, month="2026-09"
        )
    swept = await client.post("/api/v1/sheet-sync/sweep", headers=CRON)
    assert swept.json() == {"processed": 2, "done": 1, "needs_review": 1, "failed": 0}
    assert len(planner.calls) == 1


async def test_planner_error_marks_failed(
    client, admin_token, collector_token, sync_on, planner
):
    planner.queued = [PlannerError("Gemini did not answer within 30s")]
    cid, _ = await _approved(
        client, admin_token, collector_token, house=15, amount=4600, month="2026-09"
    )
    job = await _sync(client, admin_token, cid)
    assert job["status"] == "failed" and "30s" in job["error"]


# --- access -------------------------------------------------------------------------


async def test_sync_endpoints_are_admin_only(
    client, admin_token, collector_token, user_token, sync_on
):
    cid, _ = await _approved(
        client, admin_token, collector_token, house=15, amount=4600, month="2026-09"
    )
    job_id = "00000000-0000-0000-0000-000000000000"
    for token in (collector_token, user_token):
        h = _auth(token)
        assert (await client.post(f"/api/v1/collections/{cid}/sheet-sync", headers=h)).status_code == 403
        assert (await client.get("/api/v1/sheet-sync/jobs", headers=h)).status_code == 403
        assert (await client.post(f"/api/v1/sheet-sync/jobs/{job_id}/retry", headers=h)).status_code == 403
        assert (await client.post(f"/api/v1/sheet-sync/jobs/{job_id}/overwrite", headers=h)).status_code == 403

    assert (await client.post("/api/v1/sheet-sync/sweep")).status_code == 401
    wrong = await client.post("/api/v1/sheet-sync/sweep", headers={"X-Cron-Secret": "nope"})
    assert wrong.status_code == 401
    # an admin JWT is not a cron secret
    as_admin = await client.post("/api/v1/sheet-sync/sweep", headers=_auth(admin_token))
    assert as_admin.status_code == 401


async def test_deleting_collection_removes_its_job(
    client, db_session, admin_token, collector_token, sync_on
):
    cid, _ = await _approved(
        client, admin_token, collector_token, house=15, amount=4600, month="2026-09"
    )
    await _sync(client, admin_token, cid)
    removed = await client.delete(f"/api/v1/collections/{cid}", headers=_auth(admin_token))
    assert removed.status_code == 204
    from app.models.sheet_sync_job import SheetSyncJob

    count = await db_session.scalar(select(func.count()).select_from(SheetSyncJob))
    assert count == 0
