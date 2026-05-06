from __future__ import annotations

import uuid
from decimal import Decimal

from sqlalchemy import ForeignKey, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class ReceiptItem(Base):
    __tablename__ = "receipt_items"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    receipt_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("receipts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    product_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("products.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    quantity: Mapped[int] = mapped_column(nullable=False)

    # опционально: зафиксировать закупочную цену на момент прихода
    purchase_price: Mapped[Decimal | None] = mapped_column(Numeric(18, 6), nullable=True)
    currency_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("currencies.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    receipt = relationship("Receipt", back_populates="items", lazy="selectin")
    product = relationship("Product", lazy="selectin")
    currency = relationship("Currency", lazy="selectin")