from datetime import datetime, timezone

import pytest
from sqlalchemy import update

from app.models.collection import Collection


def _auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


async def _make_user(client, admin_token, *, email: str, role: str) -> str:
    await client.post(
        "/api/v1/users",
        headers=_auth(admin_token),
        json={
            "name": role.title(),
            "email": email,
            "password": "secret-123",
            "role": role,
        },
    )
    login = await client.post(
        "/api/v1/auth/login", json={"email": email, "password": "secret-123"}
    )
    return login.json()["access_token"]


@pytest.fixture
async def collector_token(client, admin_token):
    return await _make_user(
        client, admin_token, email="collector@example.com", role="collector"
    )


@pytest.fixture
async def user_token(client, admin_token):
    return await _make_user(
        client, admin_token, email="resident@example.com", role="user"
    )


async def test_submit_creates_house_and_pending_collection(client, collector_token):
    resp = await client.post(
        "/api/v1/collections",
        headers=_auth(collector_token),
        json={"house_number": 12, "amount": 500},
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["house_number"] == 12
    assert body["amount"] == 500
    assert body["approved"] is False


async def test_one_entry_per_house_per_month(client, collector_token):
    first = await client.post(
        "/api/v1/collections",
        headers=_auth(collector_token),
        json={"house_number": 42, "amount": 500},
    )
    assert first.status_code == 201

    # second submit for same house this month -> 409
    second = await client.post(
        "/api/v1/collections",
        headers=_auth(collector_token),
        json={"house_number": 42, "amount": 300},
    )
    assert second.status_code == 409

    # a different house still works
    other = await client.post(
        "/api/v1/collections",
        headers=_auth(collector_token),
        json={"house_number": 43, "amount": 300},
    )
    assert other.status_code == 201


async def test_approve_flow(client, admin_token, collector_token):
    created = await client.post(
        "/api/v1/collections",
        headers=_auth(collector_token),
        json={"house_number": 7, "amount": 300},
    )
    collection_id = created.json()["id"]

    # user cannot approve
    forbidden = await client.patch(
        f"/api/v1/collections/{collection_id}/approve",
        headers=_auth(collector_token),
    )
    assert forbidden.status_code == 403

    # admin approves
    approved = await client.patch(
        f"/api/v1/collections/{collection_id}/approve",
        headers=_auth(admin_token),
    )
    assert approved.status_code == 200
    assert approved.json()["approved"] is True

    # double approve -> 409
    again = await client.patch(
        f"/api/v1/collections/{collection_id}/approve",
        headers=_auth(admin_token),
    )
    assert again.status_code == 409


async def test_admin_approved_filter_sections(client, admin_token, collector_token):
    # two pending
    for hn in (1, 2):
        await client.post(
            "/api/v1/collections",
            headers=_auth(collector_token),
            json={"house_number": hn, "amount": 100},
        )
    # approve one
    listing = await client.get(
        "/api/v1/collections?approved=false", headers=_auth(admin_token)
    )
    first_id = listing.json()["items"][0]["id"]
    await client.patch(
        f"/api/v1/collections/{first_id}/approve", headers=_auth(admin_token)
    )

    pending = await client.get(
        "/api/v1/collections?approved=false", headers=_auth(admin_token)
    )
    approved = await client.get(
        "/api/v1/collections?approved=true", headers=_auth(admin_token)
    )
    assert pending.json()["total"] == 1
    assert approved.json()["total"] == 1


async def test_delete_approved_collection(client, admin_token, collector_token):
    created = await client.post(
        "/api/v1/collections",
        headers=_auth(collector_token),
        json={"house_number": 5, "amount": 250},
    )
    collection_id = created.json()["id"]
    await client.patch(
        f"/api/v1/collections/{collection_id}/approve", headers=_auth(admin_token)
    )

    # user cannot delete
    forbidden = await client.delete(
        f"/api/v1/collections/{collection_id}", headers=_auth(collector_token)
    )
    assert forbidden.status_code == 403

    # admin deletes
    removed = await client.delete(
        f"/api/v1/collections/{collection_id}", headers=_auth(admin_token)
    )
    assert removed.status_code == 204

    # gone
    listing = await client.get(
        "/api/v1/collections?approved=true", headers=_auth(admin_token)
    )
    assert listing.json()["total"] == 0


async def test_reject_deletes_pending_collection(client, admin_token, collector_token):
    created = await client.post(
        "/api/v1/collections",
        headers=_auth(collector_token),
        json={"house_number": 8, "amount": 400},
    )
    collection_id = created.json()["id"]

    # user cannot reject/delete
    forbidden = await client.delete(
        f"/api/v1/collections/{collection_id}", headers=_auth(collector_token)
    )
    assert forbidden.status_code == 403

    # admin rejects the pending collection
    rejected = await client.delete(
        f"/api/v1/collections/{collection_id}", headers=_auth(admin_token)
    )
    assert rejected.status_code == 204

    # gone from pending
    pending = await client.get(
        "/api/v1/collections?approved=false", headers=_auth(admin_token)
    )
    assert pending.json()["total"] == 0


async def test_current_month_total_counts_approved_only(
    client, admin_token, collector_token
):
    ids = []
    for hn, amount in ((61, 100), (62, 250), (63, 400)):
        created = await client.post(
            "/api/v1/collections",
            headers=_auth(collector_token),
            json={"house_number": hn, "amount": amount},
        )
        ids.append(created.json()["id"])

    # user cannot read the total
    forbidden = await client.get(
        "/api/v1/collections/total", headers=_auth(collector_token)
    )
    assert forbidden.status_code == 403

    # nothing approved yet -> 0
    zero = await client.get("/api/v1/collections/total", headers=_auth(admin_token))
    assert zero.status_code == 200
    assert zero.json()["total"] == 0

    # approve two of the three -> total is their sum, pending excluded
    for cid in ids[:2]:
        await client.patch(
            f"/api/v1/collections/{cid}/approve", headers=_auth(admin_token)
        )
    resp = await client.get("/api/v1/collections/total", headers=_auth(admin_token))
    assert resp.json()["total"] == 350


async def test_house_number_filter(client, admin_token, collector_token):
    for hn in (10, 20, 30):
        await client.post(
            "/api/v1/collections",
            headers=_auth(collector_token),
            json={"house_number": hn, "amount": 50},
        )
    resp = await client.get(
        "/api/v1/collections?house_number=10", headers=_auth(admin_token)
    )
    assert resp.json()["total"] == 1


async def test_pagination_envelope(client, admin_token, collector_token):
    for i in range(1, 16):
        await client.post(
            "/api/v1/collections",
            headers=_auth(collector_token),
            json={"house_number": i, "amount": 10},
        )
    resp = await client.get(
        "/api/v1/collections?page=2&size=10", headers=_auth(admin_token)
    )
    body = resp.json()
    assert body["page"] == 2
    assert body["size"] == 10
    assert body["total"] == 15
    assert body["total_pages"] == 2
    assert len(body["items"]) == 5


async def test_collector_sees_current_month_only(client, collector_token):
    await client.post(
        "/api/v1/collections",
        headers=_auth(collector_token),
        json={"house_number": 99, "amount": 500},
    )
    resp = await client.get("/api/v1/collections", headers=_auth(collector_token))
    body = resp.json()
    assert body["total"] == 1
    assert body["items"][0]["house_number"] == 99


async def test_only_collector_can_submit(client, admin_token, user_token):
    for token in (user_token, admin_token):
        resp = await client.post(
            "/api/v1/collections",
            headers=_auth(token),
            json={"house_number": 1, "amount": 100},
        )
        assert resp.status_code == 403


async def test_submit_records_collector_name(client, admin_token, collector_token):
    created = await client.post(
        "/api/v1/collections",
        headers=_auth(collector_token),
        json={"house_number": 3, "amount": 100},
    )
    assert created.json()["collector_name"] == "Collector"

    listing = await client.get(
        "/api/v1/collections?approved=false", headers=_auth(admin_token)
    )
    assert listing.json()["items"][0]["collector_name"] == "Collector"


async def test_user_sees_approved_only(
    client, admin_token, collector_token, user_token
):
    ids = []
    for hn in (1, 2):
        created = await client.post(
            "/api/v1/collections",
            headers=_auth(collector_token),
            json={"house_number": hn, "amount": 100},
        )
        ids.append(created.json()["id"])
    await client.patch(
        f"/api/v1/collections/{ids[0]}/approve", headers=_auth(admin_token)
    )

    # `approved=false` from the client is ignored for users
    resp = await client.get(
        "/api/v1/collections?approved=false", headers=_auth(user_token)
    )
    body = resp.json()
    assert body["total"] == 1
    assert body["items"][0]["approved"] is True


async def test_list_sorted_by_house_number(client, admin_token, collector_token):
    for hn in (30, 4, 17):
        await client.post(
            "/api/v1/collections",
            headers=_auth(collector_token),
            json={"house_number": hn, "amount": 10},
        )
    resp = await client.get("/api/v1/collections", headers=_auth(admin_token))
    assert [c["house_number"] for c in resp.json()["items"]] == [4, 17, 30]


async def _backdate(db_session, collection_id: str) -> None:
    """Move a collection into January 2025."""
    await db_session.execute(
        update(Collection)
        .where(Collection.id == collection_id)
        .values(created_at=datetime(2025, 1, 15, tzinfo=timezone.utc))
    )
    await db_session.commit()


async def test_month_filter_and_total(
    client, db_session, admin_token, collector_token, user_token
):
    ids = []
    for hn, amount in ((1, 100), (2, 200)):
        created = await client.post(
            "/api/v1/collections",
            headers=_auth(collector_token),
            json={"house_number": hn, "amount": amount},
        )
        ids.append(created.json()["id"])
        await client.patch(
            f"/api/v1/collections/{ids[-1]}/approve", headers=_auth(admin_token)
        )
    await _backdate(db_session, ids[0])

    for token in (admin_token, user_token):
        jan = await client.get(
            "/api/v1/collections?approved=true&month=2025-01", headers=_auth(token)
        )
        assert [c["house_number"] for c in jan.json()["items"]] == [1]

    # no month -> users get the current month
    current = await client.get("/api/v1/collections", headers=_auth(user_token))
    assert [c["house_number"] for c in current.json()["items"]] == [2]

    jan_total = await client.get(
        "/api/v1/collections/total?month=2025-01", headers=_auth(admin_token)
    )
    assert jan_total.json()["total"] == 100
    current_total = await client.get(
        "/api/v1/collections/total", headers=_auth(admin_token)
    )
    assert current_total.json()["total"] == 200

    bad = await client.get(
        "/api/v1/collections?month=2025-13", headers=_auth(admin_token)
    )
    assert bad.status_code == 422


async def test_pending_total_is_all_time(
    client, db_session, admin_token, collector_token
):
    ids = []
    for hn, amount in ((1, 100), (2, 250), (3, 400)):
        created = await client.post(
            "/api/v1/collections",
            headers=_auth(collector_token),
            json={"house_number": hn, "amount": amount},
        )
        ids.append(created.json()["id"])
    await client.patch(
        f"/api/v1/collections/{ids[2]}/approve", headers=_auth(admin_token)
    )
    await _backdate(db_session, ids[0])  # older pending rows still count

    resp = await client.get(
        "/api/v1/collections/total?approved=false", headers=_auth(admin_token)
    )
    assert resp.json()["total"] == 350
