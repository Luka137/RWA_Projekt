from datetime import date

from pydantic import BaseModel, Field, model_validator


class MembershipCreate(BaseModel):
    user_id: int
    start_date: date
    end_date: date

    @model_validator(mode="after")
    def end_after_start(self) -> "MembershipCreate":
        if self.end_date <= self.start_date:
            raise ValueError("end_date must be after start_date")
        return self


class MembershipResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    user_id: int
    start_date: date
    end_date: date
    status: str
