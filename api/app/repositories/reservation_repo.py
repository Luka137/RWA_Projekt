from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.reservation import Reservation


async def get_by_id(db: AsyncSession, reservation_id: int) -> Reservation | None:
    result = await db.execute(select(Reservation).where(Reservation.id == reservation_id))
    return result.scalar_one_or_none()


async def get_by_id_with_user(db: AsyncSession, reservation_id: int) -> Reservation | None:
    result = await db.execute(
        select(Reservation)
        .options(selectinload(Reservation.user))
        .where(Reservation.id == reservation_id)
    )
    return result.scalar_one_or_none()


async def get_by_training(
    db: AsyncSession, training_id: int, user_id: int | None = None
) -> list[Reservation]:
    stmt = (
        select(Reservation)
        .options(selectinload(Reservation.user))
        .where(Reservation.training_id == training_id)
    )
    if user_id is not None:
        stmt = stmt.where(Reservation.user_id == user_id)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_by_training_and_user(
    db: AsyncSession, training_id: int, user_id: int
) -> Reservation | None:
    result = await db.execute(
        select(Reservation).where(
            Reservation.training_id == training_id,
            Reservation.user_id == user_id,
        )
    )
    return result.scalar_one_or_none()


async def get_active_count(db: AsyncSession, training_id: int) -> int:
    result = await db.execute(
        select(func.count()).where(
            Reservation.training_id == training_id,
            Reservation.status == "confirmed",
        )
    )
    return result.scalar_one()


async def create(db: AsyncSession, training_id: int, user_id: int) -> Reservation:
    reservation = Reservation(training_id=training_id, user_id=user_id, status="confirmed")
    db.add(reservation)
    await db.flush()
    await db.refresh(reservation)
    return reservation
