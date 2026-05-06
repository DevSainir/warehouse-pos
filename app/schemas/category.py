import uuid
from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class CategoryCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)

    @field_validator("name")
    @classmethod
    def strip_name(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("name is required")
        return v


class CategoryUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=200)

    @field_validator("name")
    @classmethod
    def strip_name(cls, v: str | None) -> str | None:
        if v is None:
            return None
        v = v.strip()
        if not v:
            raise ValueError("name is required")
        return v


class CategoryOut(BaseModel):
    id: uuid.UUID
    name: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
