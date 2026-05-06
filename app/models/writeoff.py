import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class WriteOff(Base):
    __tablename__ = "writeoffs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    partner_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("partners.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    created_by_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    items: Mapped[list["WriteOffItem"]] = relationship(
        "WriteOffItem",
        back_populates="writeoff",
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="selectin",
    )
    partner = relationship("Partner", lazy="selectin")
    created_by = relationship("User", lazy="selectin")
