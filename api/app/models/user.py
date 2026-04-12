from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False, default="member")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    memberships: Mapped[list["Membership"]] = relationship(
        "Membership", back_populates="user", lazy="noload"
    )
    reservations: Mapped[list["Reservation"]] = relationship(
        "Reservation", back_populates="user", lazy="noload"
    )
    trainer_sessions: Mapped[list["Training"]] = relationship(
        "Training", back_populates="trainer", lazy="noload"
    )
