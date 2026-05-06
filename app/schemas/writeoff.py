import datetime
from decimal import Decimal
from typing import List

from pydantic import BaseModel, Field
import uuid


class ProductUpsertIn(BaseModel):
    barcode: str
    purchase_price: Decimal
    sale_price: Decimal


class WriteOffItemIn(BaseModel):
    quantity: int = Field(..., ge=1)
    product: ProductUpsertIn


class WriteOffCreateIn(BaseModel):
    partner_id: uuid.UUID
    items: List[WriteOffItemIn]


class WriteOffItemOut(BaseModel):
    product_id: uuid.UUID
    quantity: int
    purchase_price: Decimal
    sale_price: Decimal


class WriteOffOut(BaseModel):
    id: uuid.UUID
    partner_id: uuid.UUID
    created_by_id: uuid.UUID | None
    created_at: datetime.datetime
    items: list[WriteOffItemOut]