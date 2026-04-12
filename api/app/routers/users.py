from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, get_db, require_role
from app.models.user import User
from app.schemas.user import UserRegister, UserResponse
from app.services import user_service

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/register", response_model=UserResponse, status_code=201)
async def register(body: UserRegister, db: AsyncSession = Depends(get_db)):
    return await user_service.register(db, body.username, body.password)


@router.get("", response_model=list[UserResponse])
async def list_users(_: User = Depends(require_role("admin")), db: AsyncSession = Depends(get_db)):
    return await user_service.get_all(db)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if current_user.role != "admin" and current_user.id != user_id:
        from app.core.errors import AppError
        raise AppError("forbidden", "Nemate dozvolu za ovu akciju", 403)
    return await user_service.get_by_id(db, user_id)
