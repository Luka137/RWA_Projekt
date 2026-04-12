from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, get_db, require_role
from app.models.user import User
from app.schemas.reservation import ReservationResponse
from app.services import reservation_service

router = APIRouter(tags=["reservations"])


@router.get("", response_model=list[ReservationResponse])
async def list_reservations(
    training_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await reservation_service.list_reservations(db, training_id, current_user)


@router.post("", response_model=ReservationResponse, status_code=201)
async def make_reservation(
    training_id: int,
    current_user: User = Depends(require_role("member")),
    db: AsyncSession = Depends(get_db),
):
    return await reservation_service.make_reservation(db, training_id, current_user)


@router.delete("/{reservation_id}", status_code=204)
async def cancel_reservation(
    training_id: int,
    reservation_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await reservation_service.cancel_reservation(db, training_id, reservation_id, current_user)
