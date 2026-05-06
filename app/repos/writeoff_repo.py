from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.writeoff import WriteOff
from app.models.writeoff_item import WriteOffItem


class WriteOffRepo:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, writeoff_id):
        stmt = (
            select(WriteOff)
            .where(WriteOff.id == writeoff_id)
            .options(
                selectinload(WriteOff.items),          # главное
                selectinload(WriteOff.partner),        # если в ответе нужен partner
                # selectinload(WriteOff.items).selectinload(WriteOffItem.product)  # если нужен product
            )
        )
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def list(self, limit: int, offset: int):
        stmt = (
            select(WriteOff)
            .order_by(WriteOff.created_at.desc())
            .limit(limit)
            .offset(offset)
            .options(
                selectinload(WriteOff.items),
                selectinload(WriteOff.partner),
                # selectinload(WriteOff.items).selectinload(WriteOffItem.product)
            )
        )
        res = await self.session.execute(stmt)
        return res.scalars().all()

    async def create(self, obj: WriteOff) -> WriteOff:
        self.session.add(obj)
        await self.session.flush()
        return obj