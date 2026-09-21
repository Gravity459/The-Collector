async def _auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


async def test_login_bad_credentials(client, seeded_admin):
    resp = await client.post(
        "/api/v1/auth/login",
        json={"email": "admin@test.local", "password": "wrong"},
    )
    assert resp.status_code == 401


async def test_me(client, admin_token):
    resp = await client.get("/api/v1/auth/me", headers=_auth(admin_token))
    assert resp.status_code == 200
    body = resp.json()
    assert body["email"] == "admin@test.local"
    assert body["role"] == "admin"
    assert "password" not in body


async def test_admin_creates_user_then_user_logs_in(client, admin_token):
    resp = await client.post(
        "/api/v1/users",
        headers=_auth(admin_token),
        json={
            "name": "Resident",
            "email": "resident@test.local",
            "password": "resident-123",
            "role": "user",
        },
    )
    assert resp.status_code == 201

    login = await client.post(
        "/api/v1/auth/login",
        json={"email": "resident@test.local", "password": "resident-123"},
    )
    assert login.status_code == 200


async def test_user_cannot_create_user(client, admin_token):
    # create a normal user first
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
    user_token = login.json()["access_token"]

    resp = await client.post(
        "/api/v1/users",
        headers=_auth(user_token),
        json={
            "name": "X",
            "email": "x@test.local",
            "password": "password-123",
            "role": "user",
        },
    )
    assert resp.status_code == 403


async def test_no_token_rejected(client):
    resp = await client.get("/api/v1/auth/me")
    assert resp.status_code in (401, 403)
