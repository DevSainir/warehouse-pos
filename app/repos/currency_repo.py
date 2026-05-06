import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.currency import Currency


class CurrencyRepo:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, currency_id: uuid.UUID) -> Currency | None:
        return await self.session.get(Currency, currency_id)

    async def get_by_name(self, name: str) -> Currency | None:
        res = await self.session.execute(select(Currency).where(Currency.name == name))
        return res.scalar_one_or_none()

    async def list(self, limit: int = 50, offset: int = 0) -> list[Currency]:
        res = await self.session.execute(select(Currency).limit(limit).offset(offset))
        return list(res.scalars().all())

    async def create(self, obj: Currency) -> Currency:
        self.session.add(obj)
        await self.session.flush()
        return obj

    async def delete(self, obj: Currency) -> None:
        await self.session.delete(obj)
