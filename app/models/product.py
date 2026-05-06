import uuid
from decimal import Decimal
from sqlalchemy.dialects.postgresql import JSONB

from sqlalchemy import (
    Boolean,
    Column,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    BigInteger,
    Table,
    func, text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql.sqltypes import DateTime

from app.db.base import Base


product_categories = Table(
    "product_categories",
    Base.metadata,
    Column("product_id", UUID(as_uuid=True), ForeignKey("products.id", ondelete="CASCADE"), primary_key=True),
    Column("category_id", UUID(as_uuid=True), ForeignKey("categories.id", ondelete="CASCADE"), primary_key=True),
)


class Product(Base):
    __tablename__ = "products"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)

    description: Mapped[str | None] = mapped_column(String(2000), nullable=True)

    barcode: Mapped[str] = mapped_column(String(64), nullable=False, unique=True, index=True)

    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    images: Mapped[list[str] | None] = mapped_column(JSONB, nullable=True)

    serial_number: Mapped[int] = mapped_column(BigInteger, nullable=False, unique=True, index=True, server_default=text("nextval('products_serial_number_seq')")
    )

    price_wo_vat: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    purchase_price: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    last_purchase_price: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False, default=0)

    sale_price: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    markup_percent: Mapped[Decimal] = mapped_column(Numeric(7, 4), nullable=False, default=0)
    discount_percent: Mapped[Decimal] = mapped_column(Numeric(7, 4), nullable=False, default=0)

    currency_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("currencies.id"), nullable=False
    )

    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    currency = relationship("Currency", lazy="selectin")
    categories = relationship("Category", secondary=product_categories, lazy="selectin", back_populates='products')

    __table_args__ = (
        Index("ix_products_currency_id", "currency_id"),
    )


    @property
    def final_customer_price(self) -> Decimal:
        discount = Decimal(str(self.discount_percent)) if self.discount_percent else Decimal("0")
        sale = Decimal(str(self.sale_price)) if self.sale_price else Decimal("0")

        disc_multiplier = discount / Decimal("100")
        return sale * (Decimal("1") - disc_multiplier)
