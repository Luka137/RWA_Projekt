from datetime import date, datetime, timedelta, timezone
from typing import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.core.database import Base
from app.core.deps import get_db
from app.core.security import hash_password
from app.main import app as fastapi_app
from app.models.membership import Membership
from app.models.training import Training
from app.models.user import User

engine_test = create_async_engine(
    "sqlite+aiosqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestSessionLocal = async_sessionmaker(
    bind=engine_test, class_=AsyncSession, expire_on_commit=False
)


async def _override_get_db() -> AsyncGenerator[AsyncSession, None]:
    async with TestSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


fastapi_app.dependency_overrides[get_db] = _override_get_db


@pytest.fixture(autouse=True)
async def setup_database():
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def db() -> AsyncGenerator[AsyncSession, None]:
    async with TestSessionLocal() as session:
        yield session


@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    transport = ASGITransport(app=fastapi_app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def admin_user(db: AsyncSession) -> User:
    user = User(
        username="testadmin",
        password_hash=hash_password("admin123"),
        role="admin",
        is_active=True,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@pytest.fixture
async def trainer_user(db: AsyncSession) -> User:
    user = User(
        username="trainer1",
        password_hash=hash_password("pass123"),
        role="trainer",
        is_active=True,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@pytest.fixture
async def member_user(db: AsyncSession) -> User:
    user = User(
        username="member1",
        password_hash=hash_password("pass123"),
        role="member",
        is_active=True,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@pytest.fixture
async def member_with_membership(db: AsyncSession, member_user: User) -> User:
    today = date.today()
    membership = Membership(
        user_id=member_user.id,
        start_date=today,
        end_date=today + timedelta(days=30),
        status="active",
    )
    db.add(membership)
    await db.commit()
    return member_user


@pytest.fixture
async def other_member(db: AsyncSession) -> User:
    user = User(
        username="member2",
        password_hash=hash_password("pass123"),
        role="member",
        is_active=True,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    today = date.today()
    membership = Membership(
        user_id=user.id,
        start_date=today,
        end_date=today + timedelta(days=30),
        status="active",
    )
    db.add(membership)
    await db.commit()
    return user


@pytest.fixture
async def member_no_membership(db: AsyncSession) -> User:
    user = User(
        username="member3",
        password_hash=hash_password("pass123"),
        role="member",
        is_active=True,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@pytest.fixture
async def inactive_user(db: AsyncSession) -> User:
    user = User(
        username="inactive",
        password_hash=hash_password("pass123"),
        role="member",
        is_active=False,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@pytest.fixture
async def training(db: AsyncSession, trainer_user: User) -> Training:
    t = Training(
        trainer_id=trainer_user.id,
        title="Morning Yoga",
        scheduled_at=datetime.now(timezone.utc) + timedelta(days=1),
        duration_minutes=60,
        max_capacity=10,
        status="scheduled",
    )
    db.add(t)
    await db.commit()
    await db.refresh(t)
    return t


@pytest.fixture
async def full_training(db: AsyncSession, trainer_user: User, other_member: User) -> Training:
    from app.models.reservation import Reservation

    t = Training(
        trainer_id=trainer_user.id,
        title="Full Class",
        scheduled_at=datetime.now(timezone.utc) + timedelta(days=1),
        duration_minutes=45,
        max_capacity=1,
        status="scheduled",
    )
    db.add(t)
    await db.flush()

    r = Reservation(training_id=t.id, user_id=other_member.id, status="confirmed")
    db.add(r)
    await db.commit()
    await db.refresh(t)
    return t


async def auth_header(client: AsyncClient, username: str, password: str) -> dict:
    resp = await client.post("/auth/login", json={"username": username, "password": password})
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
