from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import AppError
from app.models.reservation import Reservation
from app.models.user import User
from app.repositories import membership_repo, reservation_repo, training_repo
from app.schemas.reservation import ReservationResponse


async def list_reservations(
    db: AsyncSession, training_id: int, current_user: User
) -> list[ReservationResponse]:
    training = await training_repo.get_by_id(db, training_id)
    if not training:
        raise AppError("not_found", "Trening nije pronaden", 404)

    filter_user_id = None if current_user.role in ("admin", "trainer") else current_user.id
    reservations = await reservation_repo.get_by_training(db, training_id, user_id=filter_user_id)
    return [ReservationResponse.from_orm_with_user(r) for r in reservations]


async def make_reservation(
    db: AsyncSession, training_id: int, current_user: User
) -> ReservationResponse:
    training = await training_repo.get_by_id(db, training_id)
    if not training:
        raise AppError("not_found", "Trening nije pronaden", 404)

    if training.status != "scheduled":
        raise AppError("invalid_status", "Rezervacija je moguca samo za zakazane treninge", 400)

    active_membership = await membership_repo.get_active_for_user(db, current_user.id)
    if not active_membership:
        raise AppError("no_membership", "Nemate aktivnu clanarinu", 403)

    active_count = await reservation_repo.get_active_count(db, training_id)
    if active_count >= training.max_capacity:
        raise AppError("full", "Trening je popunjen", 400)

    try:
        reservation = await reservation_repo.create(db, training_id, current_user.id)
    except IntegrityError:
        await db.rollback()
        raise AppError("conflict", "Vec ste rezervirali ovaj trening", 409)

    return ReservationResponse.from_orm_with_user(
        await reservation_repo.get_by_id_with_user(db, reservation.id)
    )


async def cancel_reservation(
    db: AsyncSession, training_id: int, reservation_id: int, current_user: User
) -> Reservation:
    reservation = await reservation_repo.get_by_id(db, reservation_id)
    if not reservation or reservation.training_id != training_id:
        raise AppError("not_found", "Rezervacija nije pronadena", 404)

    is_own = reservation.user_id == current_user.id
    is_privileged = current_user.role in ("admin", "trainer")
    if not is_own and not is_privileged:
        raise AppError("forbidden", "Nemate dozvolu za ovu akciju", 403)

    if reservation.status == "cancelled":
        raise AppError("invalid_status", "Rezervacija je vec otkazana", 400)

    reservation.status = "cancelled"
    await db.flush()
    await db.refresh(reservation)
    return reservation
