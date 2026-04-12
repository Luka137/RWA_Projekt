from httpx import AsyncClient

from tests.conftest import auth_header


async def test_list_reservations_member_sees_own(
    client: AsyncClient, member_with_membership, training, other_member
):
    # other_member also makes a reservation
    other_headers = await auth_header(client, "member2", "pass123")
    await client.post(
        f"/trainings/{training.id}/reservations",
        headers=other_headers,
    )

    member_headers = await auth_header(client, "member1", "pass123")
    await client.post(
        f"/trainings/{training.id}/reservations",
        headers=member_headers,
    )

    resp = await client.get(
        f"/trainings/{training.id}/reservations",
        headers=member_headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert all(r["user"]["id"] == member_with_membership.id for r in data)


async def test_list_reservations_trainer_sees_all(
    client: AsyncClient, trainer_user, training, member_with_membership, other_member
):
    m1_headers = await auth_header(client, "member1", "pass123")
    m2_headers = await auth_header(client, "member2", "pass123")
    await client.post(f"/trainings/{training.id}/reservations", headers=m1_headers)
    await client.post(f"/trainings/{training.id}/reservations", headers=m2_headers)

    trainer_headers = await auth_header(client, "trainer1", "pass123")
    resp = await client.get(f"/trainings/{training.id}/reservations", headers=trainer_headers)
    assert resp.status_code == 200
    assert len(resp.json()) >= 2


async def test_make_reservation_ok(client: AsyncClient, member_with_membership, training):
    headers = await auth_header(client, "member1", "pass123")
    resp = await client.post(
        f"/trainings/{training.id}/reservations",
        headers=headers,
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["training_id"] == training.id
    assert data["status"] == "confirmed"
    assert data["user"]["username"] == "member1"


async def test_make_reservation_no_membership(
    client: AsyncClient, member_no_membership, training
):
    headers = await auth_header(client, "member3", "pass123")
    resp = await client.post(
        f"/trainings/{training.id}/reservations",
        headers=headers,
    )
    assert resp.status_code == 403
    assert resp.json()["code"] == "no_membership"


async def test_make_reservation_training_full(
    client: AsyncClient, member_with_membership, full_training
):
    headers = await auth_header(client, "member1", "pass123")
    resp = await client.post(
        f"/trainings/{full_training.id}/reservations",
        headers=headers,
    )
    assert resp.status_code == 400
    assert resp.json()["code"] == "full"


async def test_make_reservation_duplicate(client: AsyncClient, member_with_membership, training):
    headers = await auth_header(client, "member1", "pass123")
    await client.post(f"/trainings/{training.id}/reservations", headers=headers)
    resp = await client.post(f"/trainings/{training.id}/reservations", headers=headers)
    assert resp.status_code == 409
    assert resp.json()["code"] == "conflict"


async def test_make_reservation_cancelled_training(
    client: AsyncClient, member_with_membership, training, trainer_user
):
    trainer_headers = await auth_header(client, "trainer1", "pass123")
    await client.patch(f"/trainings/{training.id}/cancel", headers=trainer_headers)

    member_headers = await auth_header(client, "member1", "pass123")
    resp = await client.post(
        f"/trainings/{training.id}/reservations",
        headers=member_headers,
    )
    assert resp.status_code == 400
    assert resp.json()["code"] == "invalid_status"


async def test_make_reservation_trainer_forbidden(
    client: AsyncClient, trainer_user, training
):
    headers = await auth_header(client, "trainer1", "pass123")
    resp = await client.post(
        f"/trainings/{training.id}/reservations",
        headers=headers,
    )
    assert resp.status_code == 403


async def test_cancel_reservation_by_member(
    client: AsyncClient, member_with_membership, training
):
    headers = await auth_header(client, "member1", "pass123")
    make_resp = await client.post(f"/trainings/{training.id}/reservations", headers=headers)
    reservation_id = make_resp.json()["id"]

    resp = await client.delete(
        f"/trainings/{training.id}/reservations/{reservation_id}",
        headers=headers,
    )
    assert resp.status_code == 204


async def test_cancel_reservation_by_trainer(
    client: AsyncClient, trainer_user, member_with_membership, training
):
    member_headers = await auth_header(client, "member1", "pass123")
    make_resp = await client.post(f"/trainings/{training.id}/reservations", headers=member_headers)
    reservation_id = make_resp.json()["id"]

    trainer_headers = await auth_header(client, "trainer1", "pass123")
    resp = await client.delete(
        f"/trainings/{training.id}/reservations/{reservation_id}",
        headers=trainer_headers,
    )
    assert resp.status_code == 204


async def test_cancel_reservation_other_member_forbidden(
    client: AsyncClient, member_with_membership, other_member, training
):
    m1_headers = await auth_header(client, "member1", "pass123")
    make_resp = await client.post(f"/trainings/{training.id}/reservations", headers=m1_headers)
    reservation_id = make_resp.json()["id"]

    m2_headers = await auth_header(client, "member2", "pass123")
    resp = await client.delete(
        f"/trainings/{training.id}/reservations/{reservation_id}",
        headers=m2_headers,
    )
    assert resp.status_code == 403


async def test_cancel_reservation_not_found(
    client: AsyncClient, member_with_membership, training
):
    headers = await auth_header(client, "member1", "pass123")
    resp = await client.delete(
        f"/trainings/{training.id}/reservations/9999",
        headers=headers,
    )
    assert resp.status_code == 404
