from sqlalchemy import ForeignKey, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Reservation(Base):
    __tablename__ = "reservations"
    __table_args__ = (UniqueConstraint("training_id", "user_id", name="uq_training_user"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    training_id: Mapped[int] = mapped_column(ForeignKey("trainings.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="confirmed")
    reserved_at: Mapped[str] = mapped_column(server_default=func.now(), nullable=False)

    training: Mapped["Training"] = relationship("Training", back_populates="reservations", lazy="noload")
    user: Mapped["User"] = relationship("User", back_populates="reservations", lazy="noload")
