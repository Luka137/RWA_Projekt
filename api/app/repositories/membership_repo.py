from datetime import date

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.membership import Membership


async def get_by_id(db: AsyncSession, membership_id: int) -> Membership | None:
    result = await db.execute(select(Membership).where(Membership.id == membership_id))
    return result.scalar_one_or_none()


async def get_by_user(db: AsyncSession, user_id: int) -> list[Membership]:
    result = await db.execute(
        select(Membership).where(Membership.user_id == user_id).order_by(Membership.id.desc())
    )
    return list(result.scalars().all())


async def get_all(db: AsyncSession) -> list[Membership]:
    result = await db.execute(select(Membership).order_by(Membership.id.desc()))
    return list(result.scalars().all())


async def get_active_for_user(db: AsyncSession, user_id: int) -> Membership | None:
    today = date.today()
    result = await db.execute(
        select(Membership).where(
            and_(
                Membership.user_id == user_id,
                Membership.status == "active",
                Membership.end_date >= today,
            )
        )
    )
    return result.scalar_one_or_none()


async def create(db: AsyncSession, user_id: int, start_date: date, end_date: date) -> Membership:
    membership = Membership(user_id=user_id, start_date=start_date, end_date=end_date, status="active")
    db.add(membership)
    await db.flush()
    await db.refresh(membership)
    return membership
