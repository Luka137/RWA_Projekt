from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, get_db, require_role
from app.models.user import User
from app.schemas.membership import MembershipCreate, MembershipResponse
from app.services import membership_service

router = APIRouter(prefix="/memberships", tags=["memberships"])


@router.get("", response_model=list[MembershipResponse])
async def list_memberships(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await membership_service.list_memberships(db, current_user)


@router.post("", response_model=MembershipResponse, status_code=201)
async def create_membership(
    body: MembershipCreate,
    _: User = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
):
    return await membership_service.create_membership(
        db, body.user_id, body.start_date, body.end_date
    )


@router.get("/{membership_id}", response_model=MembershipResponse)
async def get_membership(
    membership_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await membership_service.get_membership(db, membership_id, current_user)


@router.patch("/{membership_id}/cancel", response_model=MembershipResponse)
async def cancel_membership(
    membership_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await membership_service.cancel_membership(db, membership_id, current_user)
