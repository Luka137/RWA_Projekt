from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, get_db, require_role
from app.models.user import User
from app.schemas.training import TrainingCreate, TrainingResponse, TrainingUpdate
from app.services import training_service

router = APIRouter(prefix="/trainings", tags=["trainings"])


@router.get("", response_model=list[TrainingResponse])
async def list_trainings(
    _: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await training_service.list_trainings(db)


@router.post("", response_model=TrainingResponse, status_code=201)
async def create_training(
    body: TrainingCreate,
    current_user: User = Depends(require_role("admin", "trainer")),
    db: AsyncSession = Depends(get_db),
):
    return await training_service.create_training(
        db,
        current_user,
        body.title,
        body.scheduled_at,
        body.duration_minutes,
        body.max_capacity,
    )


@router.get("/{training_id}", response_model=TrainingResponse)
async def get_training(
    training_id: int,
    _: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await training_service.get_training(db, training_id)


@router.patch("/{training_id}", response_model=TrainingResponse)
async def update_training(
    training_id: int,
    body: TrainingUpdate,
    current_user: User = Depends(require_role("admin", "trainer")),
    db: AsyncSession = Depends(get_db),
):
    return await training_service.update_training(
        db,
        training_id,
        current_user,
        **body.model_dump(exclude_none=True),
    )


@router.patch("/{training_id}/start", response_model=TrainingResponse)
async def start_training(
    training_id: int,
    current_user: User = Depends(require_role("admin", "trainer")),
    db: AsyncSession = Depends(get_db),
):
    return await training_service.change_status(db, training_id, "in_progress", current_user)


@router.patch("/{training_id}/complete", response_model=TrainingResponse)
async def complete_training(
    training_id: int,
    current_user: User = Depends(require_role("admin", "trainer")),
    db: AsyncSession = Depends(get_db),
):
    return await training_service.change_status(db, training_id, "completed", current_user)


@router.patch("/{training_id}/cancel", response_model=TrainingResponse)
async def cancel_training(
    training_id: int,
    current_user: User = Depends(require_role("admin", "trainer")),
    db: AsyncSession = Depends(get_db),
):
    return await training_service.change_status(db, training_id, "cancelled", current_user)
