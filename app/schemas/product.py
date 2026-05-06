import uuid
from decimal import Decimal
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict, condecimal
from typing import List, Optional
from typing import Annotated


Money = condecimal(max_digits=18, decimal_places=4, ge=0)
Qty = condecimal(max_digits=18, decimal_places=3, ge=0)
Percent = condecimal(max_digits=7, decimal_places=4, ge=0, le=100)
Images3 = Annotated[list[str], Field(max_length=3)]


class ProductBase(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=2000)
    barcode: str = Field(min_length=1, max_length=64)

    quantity: int = 0

    images: Images3 | None = None

    price_wo_vat: Money = 0
    purchase_price: Money = 0
    last_purchase_price: Money = 0

    sale_price: Money = 0
    markup_percent: Percent = 0
    discount_percent: Percent = 0

    currency_id: uuid.UUID
    is_active: bool = True

    category_ids: list[uuid.UUID] = []


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=2000)
    barcode: str | None = Field(default=None, min_length=1, max_length=64)

    quantity: int | None = None

    images: Images3 | None = None

    price_wo_vat: Money | None = None
    purchase_price: Money | None = None
    last_purchase_price: Money | None = None

    sale_price: Money | None = None
    markup_percent: Percent | None = None
    discount_percent: Percent | None = None

    currency_id: uuid.UUID | None = None
    is_active: bool | None = None

    category_ids: list[uuid.UUID] | None = None


class CategoryRef(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    name: str


class CurrencyRef(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    name: str


class ProductRef(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    name: str
    barcode: str


class ProductOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    description: str | None = Field(default=None, max_length=2000)
    barcode: str
    serial_number: int

    quantity: int

    image_urls: Optional[List[str]] = None  # presigned URLs

    price_wo_vat: Decimal
    purchase_price: Decimal
    last_purchase_price: Decimal

    sale_price: Decimal
    markup_percent: Decimal
    discount_percent: Decimal

    currency: CurrencyRef
    categories: list[CategoryRef]

    final_customer_price: Decimal

    is_active: bool
    created_at: datetime
    updated_at: datetime
