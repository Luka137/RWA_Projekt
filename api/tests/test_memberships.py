from datetime import date, timedelta

from httpx import AsyncClient

from tests.conftest import auth_header


async def test_list_memberships_member_sees_own(
    client: AsyncClient, member_with_membership, admin_user
):
    headers = await auth_header(client, "member1", "pass123")
    resp = await client.get("/memberships", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert all(m["user_id"] == member_with_membership.id for m in data)


async def test_list_memberships_admin_sees_all(
    client: AsyncClient, admin_user, member_with_membership, other_member
):
    headers = await auth_header(client, "testadmin", "admin123")
    resp = await client.get("/memberships", headers=headers)
    assert resp.status_code == 200
    assert len(resp.json()) >= 2


async def test_create_membership_admin(client: AsyncClient, admin_user, member_no_membership):
    headers = await auth_header(client, "testadmin", "admin123")
    today = date.today()
    resp = await client.post(
        "/memberships",
        headers=headers,
        json={
            "user_id": member_no_membership.id,
            "start_date": str(today),
            "end_date": str(today + timedelta(days=30)),
        },
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["user_id"] == member_no_membership.id
    assert data["status"] == "active"


async def test_create_membership_forbidden_for_member(
    client: AsyncClient, member_user, member_no_membership
):
    headers = await auth_header(client, "member1", "pass123")
    today = date.today()
    resp = await client.post(
        "/memberships",
        headers=headers,
        json={
            "user_id": member_no_membership.id,
            "start_date": str(today),
            "end_date": str(today + timedelta(days=30)),
        },
    )
    assert resp.status_code == 403


async def test_create_membership_duplicate_active(
    client: AsyncClient, admin_user, member_with_membership
):
    headers = await auth_header(client, "testadmin", "admin123")
    today = date.today()
    resp = await client.post(
        "/memberships",
        headers=headers,
        json={
            "user_id": member_with_membership.id,
            "start_date": str(today),
            "end_date": str(today + timedelta(days=30)),
        },
    )
    assert resp.status_code == 409


async def test_create_membership_end_before_start(client: AsyncClient, admin_user, member_no_membership):
    headers = await auth_header(client, "testadmin", "admin123")
    today = date.today()
    resp = await client.post(
        "/memberships",
        headers=headers,
        json={
            "user_id": member_no_membership.id,
            "start_date": str(today + timedelta(days=10)),
            "end_date": str(today),
        },
    )
    assert resp.status_code == 422


async def test_cancel_membership_by_member(client: AsyncClient, member_with_membership):
    headers = await auth_header(client, "member1", "pass123")
    list_resp = await client.get("/memberships", headers=headers)
    membership_id = list_resp.json()[0]["id"]

    resp = await client.patch(f"/memberships/{membership_id}/cancel", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["status"] == "cancelled"


async def test_cancel_membership_by_admin(client: AsyncClient, admin_user, member_with_membership):
    admin_headers = await auth_header(client, "testadmin", "admin123")
    member_headers = await auth_header(client, "member1", "pass123")

    list_resp = await client.get("/memberships", headers=member_headers)
    membership_id = list_resp.json()[0]["id"]

    resp = await client.patch(f"/memberships/{membership_id}/cancel", headers=admin_headers)
    assert resp.status_code == 200
    assert resp.json()["status"] == "cancelled"


async def test_cancel_already_cancelled(client: AsyncClient, member_with_membership):
    headers = await auth_header(client, "member1", "pass123")
    list_resp = await client.get("/memberships", headers=headers)
    membership_id = list_resp.json()[0]["id"]

    await client.patch(f"/memberships/{membership_id}/cancel", headers=headers)
    resp = await client.patch(f"/memberships/{membership_id}/cancel", headers=headers)
    assert resp.status_code == 400


async def test_cancel_other_membership_forbidden(
    client: AsyncClient, member_user, other_member
):
    admin_headers = None
    from app.core.security import hash_password
    # Get other_member's membership id via admin first
    # Use other_member directly from fixture — their membership was created in fixture
    member1_headers = await auth_header(client, "member1", "pass123")
    member2_headers = await auth_header(client, "member2", "pass123")

    list_resp = await client.get("/memberships", headers=member2_headers)
    membership_id = list_resp.json()[0]["id"]

    resp = await client.patch(f"/memberships/{membership_id}/cancel", headers=member1_headers)
    assert resp.status_code == 403
