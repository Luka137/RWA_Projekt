from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import AppError
from app.core.security import hash_password
from app.models.user import User
from app.repositories import user_repo


async def register(db: AsyncSession, username: str, password: str) -> User:
    existing = await user_repo.get_by_username(db, username)
    if existing:
        raise AppError("username_taken", "Korisnicko ime je vec zauzeto", 409)
    password_hash = hash_password(password)
    return await user_repo.create(db, username, password_hash, role="member")


async def get_all(db: AsyncSession) -> list[User]:
    return await user_repo.get_all(db)


async def get_by_id(db: AsyncSession, user_id: int) -> User:
    user = await user_repo.get_by_id(db, user_id)
    if not user:
        raise AppError("not_found", "Korisnik nije pronaden", 404)
    return user
