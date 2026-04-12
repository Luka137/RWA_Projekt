from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import AppError
from app.core.jwt import create_access_token, create_refresh_token, decode_token
from app.core.security import verify_password
from app.repositories import user_repo
from app.schemas.auth import TokenResponse


async def login(db: AsyncSession, username: str, password: str) -> TokenResponse:
    user = await user_repo.get_by_username(db, username)
    if not user or not verify_password(password, user.password_hash):
        raise AppError("invalid_credentials", "Pogresno korisnicko ime ili lozinka", 401)
    if not user.is_active:
        raise AppError("inactive_user", "Korisnicki racun je deaktiviran", 403)

    return TokenResponse(
        access_token=create_access_token(user.id, user.role),
        refresh_token=create_refresh_token(user.id),
    )


async def refresh(db: AsyncSession, refresh_token: str) -> TokenResponse:
    from jose import JWTError

    try:
        payload = decode_token(refresh_token)
    except JWTError:
        raise AppError("token_expired", "Token je istekao ili nije valjan", 401)

    if payload.get("type") != "refresh":
        raise AppError("invalid_credentials", "Token nije refresh tipa", 401)

    user = await user_repo.get_by_id(db, int(payload["sub"]))
    if not user or not user.is_active:
        raise AppError("invalid_credentials", "Korisnik ne postoji ili je deaktiviran", 401)

    return TokenResponse(
        access_token=create_access_token(user.id, user.role),
        refresh_token=create_refresh_token(user.id),
    )
