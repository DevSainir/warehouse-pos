import uuid
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime


class CurrencyBase(BaseModel):
    name: str = Field(min_length=1, max_length=50)


class CurrencyCreate(CurrencyBase):
    pass


class CurrencyUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=50)


class CurrencyOut(CurrencyBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
