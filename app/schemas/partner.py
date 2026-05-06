import uuid
from datetime import datetime

from pydantic import BaseModel, Field, field_validator, ConfigDict


class PartnerBase(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    comment: str | None = Field(default=None, max_length=5000)
    is_active: bool = True

    @field_validator("name")
    @classmethod
    def strip_name(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("name is required")
        return v

    @field_validator("comment")
    @classmethod
    def normalize_comment(cls, v: str | None) -> str | None:
        if v is None:
            return None
        v = v.strip()
        return v if v else None


class PartnerCreate(PartnerBase):
    pass


class PartnerUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=200)
    comment: str | None = Field(default=None, max_length=5000)
    is_active: bool | None = None

    @field_validator("name")
    @classmethod
    def strip_name(cls, v: str | None) -> str | None:
        if v is None:
            return None
        v = v.strip()
        if not v:
            raise ValueError("name is required")
        return v

    @field_validator("comment")
    @classmethod
    def normalize_comment(cls, v: str | None) -> str | None:
        if v is None:
            return None
        v = v.strip()
        return v if v else None


class PartnerRef(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    name: str


class PartnerOut(BaseModel):
    id: uuid.UUID
    name: str
    comment: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
