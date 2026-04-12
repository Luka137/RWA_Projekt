from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.training import Training


async def get_by_id(db: AsyncSession, training_id: int) -> Training | None:
    result = await db.execute(select(Training).where(Training.id == training_id))
    return result.scalar_one_or_none()


async def get_by_id_with_trainer(db: AsyncSession, training_id: int) -> Training | None:
    result = await db.execute(
        select(Training)
        .options(selectinload(Training.trainer))
        .where(Training.id == training_id)
    )
    return result.scalar_one_or_none()


async def get_all(db: AsyncSession) -> list[Training]:
    result = await db.execute(
        select(Training).options(selectinload(Training.trainer)).order_by(Training.scheduled_at)
    )
    return list(result.scalars().all())


async def create(
    db: AsyncSession,
    trainer_id: int,
    title: str,
    scheduled_at,
    duration_minutes: int,
    max_capacity: int,
) -> Training:
    training = Training(
        trainer_id=trainer_id,
        title=title,
        scheduled_at=scheduled_at,
        duration_minutes=duration_minutes,
        max_capacity=max_capacity,
        status="scheduled",
    )
    db.add(training)
    await db.flush()
    await db.refresh(training)
    return training
