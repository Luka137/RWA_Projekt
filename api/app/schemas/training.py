from datetime import datetime, timezone

from pydantic import BaseModel, Field, field_validator


class TrainingCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=100)
    scheduled_at: datetime
    duration_minutes: int = Field(..., gt=0)
    max_capacity: int = Field(..., gt=0)

    @field_validator("scheduled_at")
    @classmethod
    def must_be_future(cls, v: datetime) -> datetime:
        if v.tzinfo is None:
            v = v.replace(tzinfo=timezone.utc)
        if v <= datetime.now(timezone.utc):
            raise ValueError("scheduled_at must be in the future")
        return v


class TrainingUpdate(BaseModel):
    title: str | None = Field(None, min_length=3, max_length=100)
    scheduled_at: datetime | None = None
    duration_minutes: int | None = Field(None, gt=0)
    max_capacity: int | None = Field(None, gt=0)

    @field_validator("scheduled_at")
    @classmethod
    def must_be_future(cls, v: datetime | None) -> datetime | None:
        if v is None:
            return v
        if v.tzinfo is None:
            v = v.replace(tzinfo=timezone.utc)
        if v <= datetime.now(timezone.utc):
            raise ValueError("scheduled_at must be in the future")
        return v


class TrainerInfo(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    username: str


class TrainingResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    title: str
    scheduled_at: datetime
    duration_minutes: int
    max_capacity: int
    status: str
    trainer: TrainerInfo | None
