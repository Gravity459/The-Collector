import pytest


async def _auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
async def user_token(client, admin_token):
    await client.post(
        "/api/v1/users",
        headers=_auth(admin_token),
        json={
            "name": "Resident",
            "email": "resident@test.local",
            "password": "resident-123",
            "role": "user",
        },
    )
    login = await client.post(
        "/api/v1/auth/login",
        json={"email": "resident@test.local", "password": "resident-123"},
    )
    return login.json()["access_token"]


async def test_submit_creates_house_and_pending_collection(client, user_token):
    resp = await client.post(
        "/api/v1/collections",
        headers=_auth(user_token),
        json={"house_number": 12, "amount": 500},
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["house_number"] == 12
    assert body["amount"] == 500
    assert body["approved"] is False


async def test_one_entry_per_house_per_month(client, user_token):
    first = await client.post(
        "/api/v1/collections",
        headers=_auth(user_token),
        json={"house_number": 42, "amount": 500},
    )
    assert first.status_code == 201

    # second submit for same house this month -> 409
    second = await client.post(
        "/api/v1/collections",
        headers=_auth(user_token),
        json={"house_number": 42, "amount": 300},
    )
    assert second.status_code == 409

    # a different house still works
    other = await client.post(
        "/api/v1/collections",
        headers=_auth(user_token),
        json={"house_number": 43, "amount": 300},
    )
    assert other.status_code == 201


async def test_approve_flow(client, admin_token, user_token):
    created = await client.post(
        "/api/v1/collections",
        headers=_auth(user_token),
        json={"house_number": 7, "amount": 300},
    )
    collection_id = created.json()["id"]

    # user cannot approve
    forbidden = await client.patch(
        f"/api/v1/collections/{collection_id}/approve",
        headers=_auth(user_token),
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


async def test_admin_approved_filter_sections(client, admin_token, user_token):
    # two pending
    for hn in (1, 2):
        await client.post(
            "/api/v1/collections",
            headers=_auth(user_token),
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


async def test_delete_approved_collection(client, admin_token, user_token):
    created = await client.post(
        "/api/v1/collections",
        headers=_auth(user_token),
        json={"house_number": 5, "amount": 250},
    )
    collection_id = created.json()["id"]
    await client.patch(
        f"/api/v1/collections/{collection_id}/approve", headers=_auth(admin_token)
    )

    # user cannot delete
    forbidden = await client.delete(
        f"/api/v1/collections/{collection_id}", headers=_auth(user_token)
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


async def test_reject_deletes_pending_collection(client, admin_token, user_token):
    created = await client.post(
        "/api/v1/collections",
        headers=_auth(user_token),
        json={"house_number": 8, "amount": 400},
    )
    collection_id = created.json()["id"]

    # user cannot reject/delete
    forbidden = await client.delete(
        f"/api/v1/collections/{collection_id}", headers=_auth(user_token)
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
    client, admin_token, user_token
):
    ids = []
    for hn, amount in ((61, 100), (62, 250), (63, 400)):
        created = await client.post(
            "/api/v1/collections",
            headers=_auth(user_token),
            json={"house_number": hn, "amount": amount},
        )
        ids.append(created.json()["id"])

    # user cannot read the total
    forbidden = await client.get(
        "/api/v1/collections/total", headers=_auth(user_token)
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


async def test_house_number_filter(client, admin_token, user_token):
    for hn in (10, 20, 30):
        await client.post(
            "/api/v1/collections",
            headers=_auth(user_token),
            json={"house_number": hn, "amount": 50},
        )
    resp = await client.get(
        "/api/v1/collections?house_number=10", headers=_auth(admin_token)
    )
    assert resp.json()["total"] == 1


async def test_pagination_envelope(client, admin_token, user_token):
    for i in range(1, 16):
        await client.post(
            "/api/v1/collections",
            headers=_auth(user_token),
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


async def test_user_sees_current_month_only(client, user_token):
    await client.post(
        "/api/v1/collections",
        headers=_auth(user_token),
        json={"house_number": 99, "amount": 500},
    )
    resp = await client.get("/api/v1/collections", headers=_auth(user_token))
    body = resp.json()
    assert body["total"] == 1
    assert body["items"][0]["house_number"] == 99
