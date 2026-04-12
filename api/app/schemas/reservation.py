from pydantic import BaseModel

from app.models.reservation import Reservation
from app.schemas.user import UserResponse


class ReservationResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    training_id: int
    status: str
    user: UserResponse | None = None

    @classmethod
    def from_orm_with_user(cls, reservation: Reservation) -> "ReservationResponse":
        return cls(
            id=reservation.id,
            training_id=reservation.training_id,
            status=reservation.status,
            user=UserResponse.model_validate(reservation.user) if reservation.user else None,
        )
