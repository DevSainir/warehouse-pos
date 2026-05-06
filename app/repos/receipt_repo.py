import uuid
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.receipt import Receipt


class ReceiptRepo:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, receipt_id: uuid.UUID) -> Optional[Receipt]:
        stmt = (
            select(Receipt)
            .where(Receipt.id == receipt_id)
            .options(selectinload(Receipt.items))
        )
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def list(self, limit: int = 50, offset: int = 0) -> list[Receipt]:
        stmt = (
            select(Receipt)
            .order_by(Receipt.created_at.desc())
            .limit(limit)
            .offset(offset)
            .options(selectinload(Receipt.partner))
        )
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def create(self, obj: Receipt) -> Receipt:
        self.session.add(obj)
        await self.session.flush()
        return obj