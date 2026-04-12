from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import AppError
from app.models.training import Training
from app.models.user import User
from app.repositories import training_repo

_VALID_TRANSITIONS: dict[str, list[str]] = {
    "scheduled": ["in_progress", "cancelled"],
    "in_progress": ["completed", "cancelled"],
    "completed": [],
    "cancelled": [],
}


def _check_training_ownership_or_403(training: Training, current_user: User) -> None:
    if current_user.role == "admin":
        return
    if current_user.role == "trainer" and training.trainer_id == current_user.id:
        return
    raise AppError("forbidden", "Nemate dozvolu za ovu akciju", 403)


async def list_trainings(db: AsyncSession) -> list[Training]:
    return await training_repo.get_all(db)


async def create_training(
    db: AsyncSession,
    current_user: User,
    title: str,
    scheduled_at: datetime,
    duration_minutes: int,
    max_capacity: int,
) -> Training:
    training = await training_repo.create(
        db,
        trainer_id=current_user.id,
        title=title,
        scheduled_at=scheduled_at,
        duration_minutes=duration_minutes,
        max_capacity=max_capacity,
    )
    return await training_repo.get_by_id_with_trainer(db, training.id)


async def get_training(db: AsyncSession, training_id: int) -> Training:
    training = await training_repo.get_by_id_with_trainer(db, training_id)
    if not training:
        raise AppError("not_found", "Trening nije pronaden", 404)
    return training


async def update_training(
    db: AsyncSession,
    training_id: int,
    current_user: User,
    **kwargs,
) -> Training:
    training = await training_repo.get_by_id(db, training_id)
    if not training:
        raise AppError("not_found", "Trening nije pronaden", 404)
    _check_training_ownership_or_403(training, current_user)

    for key, value in kwargs.items():
        if value is not None:
            setattr(training, key, value)

    await db.flush()
    return await training_repo.get_by_id_with_trainer(db, training_id)


async def change_status(
    db: AsyncSession, training_id: int, new_status: str, current_user: User
) -> Training:
    training = await training_repo.get_by_id(db, training_id)
    if not training:
        raise AppError("not_found", "Trening nije pronaden", 404)
    _check_training_ownership_or_403(training, current_user)

    allowed = _VALID_TRANSITIONS.get(training.status, [])
    if new_status not in allowed:
        raise AppError(
            "invalid_transition",
            f"Ne mozete promijeniti status iz '{training.status}' u '{new_status}'",
            400,
        )

    training.status = new_status
    await db.flush()
    return await training_repo.get_by_id_with_trainer(db, training_id)
