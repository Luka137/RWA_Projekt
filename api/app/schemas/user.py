from pydantic import BaseModel, Field


class UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)


class UserResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    username: str
    role: str
    is_active: bool
