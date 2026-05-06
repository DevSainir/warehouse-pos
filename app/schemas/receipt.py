from __future__ import annotations

import uuid
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, Field, ConfigDict


class ProductUpsertIn(BaseModel):
    barcode: str

    name: str
    description: Optional[str] = None

    price_wo_vat: Decimal
    purchase_price: Decimal
    sale_price: Decimal
    markup_percent: Decimal
    discount_percent: Decimal

    currency_id: uuid.UUID
    is_active: bool = True

    category_ids: List[uuid.UUID] = Field(default_factory=list)


class ReceiptItemIn(BaseModel):
    quantity: int = Field(..., ge=1)
    product: ProductUpsertIn


class ReceiptCreateIn(BaseModel):
    partner_id: uuid.UUID
    items: List[ReceiptItemIn]


class ReceiptItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    product_id: uuid.UUID
    quantity: int


class ReceiptOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    partner_id: uuid.UUID
    created_by_id: uuid.UUID | None
    items: List[ReceiptItemOut]