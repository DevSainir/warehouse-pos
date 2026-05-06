from datetime import datetime
from pydantic import BaseModel, Field
from app.models.user import UserRole
import uuid

class UserBase(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    role: UserRole
    is_active: bool = True

class UserCreate(UserBase):
    password: str = Field(min_length=6, max_length=128)

class UserUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=200)
    role: UserRole | None = None
    is_active: bool | None = None
    password: str | None = Field(default=None, min_length=6, max_length=128)

class UserOut(BaseModel):
    id: uuid.UUID
    name: str
    role: UserRole
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
