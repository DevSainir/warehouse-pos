import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field, ConfigDict


class SaleItemCreateIn(BaseModel):
    barcode: str
    quantity: int = Field(..., gt=0)
    price: Decimal
    amount: Decimal | None = None


class SaleCreateIn(BaseModel):
    partner_id: uuid.UUID
    total_amount: Decimal | None = None
    items: list[SaleItemCreateIn]


class SaleItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    product_id: uuid.UUID
    quantity: int
    price: Decimal
    amount: Decimal


class SaleOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    partner_id: uuid.UUID
    total_amount: Decimal
    created_by_id: uuid.UUID | None
    created_at: datetime
    items: list[SaleItemOut]