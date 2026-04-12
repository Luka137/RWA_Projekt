from httpx import AsyncClient

from tests.conftest import auth_header


async def test_register_ok(client: AsyncClient):
    resp = await client.post(
        "/users/register",
        json={"username": "newuser", "password": "secret123"},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["username"] == "newuser"
    assert data["role"] == "member"
    assert data["is_active"] is True


async def test_register_duplicate(client: AsyncClient, member_user):
    resp = await client.post(
        "/users/register",
        json={"username": "member1", "password": "secret123"},
    )
    assert resp.status_code == 409
    assert resp.json()["code"] == "username_taken"


async def test_register_short_username(client: AsyncClient):
    resp = await client.post(
        "/users/register",
        json={"username": "ab", "password": "secret123"},
    )
    assert resp.status_code == 422


async def test_register_short_password(client: AsyncClient):
    resp = await client.post(
        "/users/register",
        json={"username": "validuser", "password": "123"},
    )
    assert resp.status_code == 422


async def test_list_users_admin(client: AsyncClient, admin_user, member_user):
    headers = await auth_header(client, "testadmin", "admin123")
    resp = await client.get("/users", headers=headers)
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)
    assert len(resp.json()) >= 2


async def test_list_users_forbidden_for_member(client: AsyncClient, member_user):
    headers = await auth_header(client, "member1", "pass123")
    resp = await client.get("/users", headers=headers)
    assert resp.status_code == 403


async def test_list_users_no_auth(client: AsyncClient):
    resp = await client.get("/users")
    assert resp.status_code == 401


async def test_get_user_self(client: AsyncClient, member_user):
    headers = await auth_header(client, "member1", "pass123")
    resp = await client.get(f"/users/{member_user.id}", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["username"] == "member1"


async def test_get_user_admin_any(client: AsyncClient, admin_user, member_user):
    headers = await auth_header(client, "testadmin", "admin123")
    resp = await client.get(f"/users/{member_user.id}", headers=headers)
    assert resp.status_code == 200


async def test_get_user_other_forbidden(client: AsyncClient, member_user, other_member):
    headers = await auth_header(client, "member1", "pass123")
    resp = await client.get(f"/users/{other_member.id}", headers=headers)
    assert resp.status_code == 403


async def test_get_user_not_found(client: AsyncClient, admin_user):
    headers = await auth_header(client, "testadmin", "admin123")
    resp = await client.get("/users/9999", headers=headers)
    assert resp.status_code == 404
