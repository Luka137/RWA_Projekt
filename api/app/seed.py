import asyncio
from datetime import date, timedelta

from app.core.database import AsyncSessionLocal
from app.core.security import hash_password
from app.models.membership import Membership
from app.models.user import User


async def seed() -> None:
    async with AsyncSessionLocal() as db:
        from sqlalchemy import select

        users_data = [
            {"username": "admin", "password": "admin123", "role": "admin"},
            {"username": "trainer1", "password": "pass123", "role": "trainer"},
            {"username": "member1", "password": "pass123", "role": "member"},
            {"username": "member2", "password": "pass123", "role": "member"},
        ]

        created_users: dict[str, User] = {}
        for data in users_data:
            result = await db.execute(select(User).where(User.username == data["username"]))
            user = result.scalar_one_or_none()
            if not user:
                user = User(
                    username=data["username"],
                    password_hash=hash_password(data["password"]),
                    role=data["role"],
                )
                db.add(user)
                await db.flush()
                print(f"Created user: {data['username']} ({data['role']})")
            else:
                print(f"User already exists: {data['username']}")
            created_users[data["username"]] = user

        member1 = created_users["member1"]
        result = await db.execute(
            select(Membership).where(
                Membership.user_id == member1.id,
                Membership.status == "active",
            )
        )
        existing_membership = result.scalar_one_or_none()
        if not existing_membership:
            today = date.today()
            membership = Membership(
                user_id=member1.id,
                start_date=today,
                end_date=today + timedelta(days=30),
                status="active",
            )
            db.add(membership)
            print(f"Created active membership for member1 (30 days)")
        else:
            print("member1 already has an active membership")

        await db.commit()
        print("Seed completed.")


if __name__ == "__main__":
    asyncio.run(seed())
