from datetime import date

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import AppError
from app.models.membership import Membership
from app.models.user import User
from app.repositories import membership_repo, user_repo


async def list_memberships(db: AsyncSession, current_user: User) -> list[Membership]:
    if current_user.role == "admin":
        return await membership_repo.get_all(db)
    return await membership_repo.get_by_user(db, current_user.id)


async def create_membership(
    db: AsyncSession,
    user_id: int,
    start_date: date,
    end_date: date,
) -> Membership:
    user = await user_repo.get_by_id(db, user_id)
    if not user:
        raise AppError("not_found", "Korisnik nije pronaden", 404)

    existing = await membership_repo.get_active_for_user(db, user_id)
    if existing:
        raise AppError("conflict", "Korisnik vec ima aktivnu clanarinu", 409)

    return await membership_repo.create(db, user_id, start_date, end_date)


async def get_membership(db: AsyncSession, membership_id: int, current_user: User) -> Membership:
    membership = await membership_repo.get_by_id(db, membership_id)
    if not membership:
        raise AppError("not_found", "Clanarina nije pronadena", 404)
    if current_user.role != "admin" and membership.user_id != current_user.id:
        raise AppError("forbidden", "Nemate dozvolu za ovu akciju", 403)
    return membership


async def cancel_membership(db: AsyncSession, membership_id: int, current_user: User) -> Membership:
    membership = await membership_repo.get_by_id(db, membership_id)
    if not membership:
        raise AppError("not_found", "Clanarina nije pronadena", 404)
    if current_user.role != "admin" and membership.user_id != current_user.id:
        raise AppError("forbidden", "Nemate dozvolu za ovu akciju", 403)
    if membership.status == "cancelled":
        raise AppError("invalid_status", "Clanarina je vec otkazana", 400)

    membership.status = "cancelled"
    await db.flush()
    await db.refresh(membership)
    return membership
