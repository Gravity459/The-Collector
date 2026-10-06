import uuid


def _auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


async def _create(client, admin_token, *, email: str, role: str) -> str:
    resp = await client.post(
        "/api/v1/users",
        headers=_auth(admin_token),
        json={
            "name": "Someone",
            "email": email,
            "password": "secret-123",
            "role": role,
        },
    )
    assert resp.status_code == 201
    return resp.json()["id"]


async def _login(client, email: str, password: str):
    return await client.post(
        "/api/v1/auth/login", json={"email": email, "password": password}
    )


async def test_admin_updates_password(client, admin_token):
    user_id = await _create(client, admin_token, email="u@example.com", role="user")

    resp = await client.patch(
        f"/api/v1/users/{user_id}/password",
        headers=_auth(admin_token),
        json={"password": "new-secret-456"},
    )
    assert resp.status_code == 204

    assert (await _login(client, "u@example.com", "secret-123")).status_code == 401
    assert (await _login(client, "u@example.com", "new-secret-456")).status_code == 200


async def test_password_too_short(client, admin_token):
    user_id = await _create(client, admin_token, email="u@example.com", role="user")
    resp = await client.patch(
        f"/api/v1/users/{user_id}/password",
        headers=_auth(admin_token),
        json={"password": "short"},
    )
    assert resp.status_code == 422


async def test_delete_collector_keeps_collections(client, admin_token):
    collector_id = await _create(
        client, admin_token, email="c@example.com", role="collector"
    )
    login = await _login(client, "c@example.com", "secret-123")
    token = login.json()["access_token"]
    await client.post(
        "/api/v1/collections",
        headers=_auth(token),
        json={"house_number": 5, "amount": 100},
    )

    resp = await client.delete(
        f"/api/v1/users/{collector_id}", headers=_auth(admin_token)
    )
    assert resp.status_code == 204

    listing = await client.get("/api/v1/collections", headers=_auth(admin_token))
    items = listing.json()["items"]
    assert len(items) == 1
    assert items[0]["collector_name"] is None

    # removed user's token no longer works
    me = await client.get("/api/v1/auth/me", headers=_auth(token))
    assert me.status_code == 401


async def test_admin_cannot_delete_self(client, admin_token):
    me = await client.get("/api/v1/auth/me", headers=_auth(admin_token))
    admin_id = me.json()["id"]
    resp = await client.delete(f"/api/v1/users/{admin_id}", headers=_auth(admin_token))
    assert resp.status_code == 400


async def test_unknown_user_404(client, admin_token):
    missing = uuid.uuid4()
    resp = await client.delete(f"/api/v1/users/{missing}", headers=_auth(admin_token))
    assert resp.status_code == 404
    resp = await client.patch(
        f"/api/v1/users/{missing}/password",
        headers=_auth(admin_token),
        json={"password": "new-secret-456"},
    )
    assert resp.status_code == 404


async def test_non_admin_forbidden(client, admin_token):
    target = await _create(client, admin_token, email="t@example.com", role="user")
    for role in ("user", "collector"):
        email = f"{role}@example.com"
        await _create(client, admin_token, email=email, role=role)
        login = await _login(client, email, "secret-123")
        token = login.json()["access_token"]

        resp = await client.delete(f"/api/v1/users/{target}", headers=_auth(token))
        assert resp.status_code == 403
        resp = await client.patch(
            f"/api/v1/users/{target}/password",
            headers=_auth(token),
            json={"password": "new-secret-456"},
        )
        assert resp.status_code == 403
