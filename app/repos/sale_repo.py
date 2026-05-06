from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.sale import Sale


class SaleRepo:
    def __init__(self, session):
        self.session = session

    async def create(self, obj: Sale) -> Sale:
        self.session.add(obj)
        await self.session.flush()
        return obj

    async def get_by_id(self, sale_id):
        stmt = (
            select(Sale)
            .where(Sale.id == sale_id)
            .options(selectinload(Sale.items))
        )
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def list_(self, limit: int = 50, offset: int = 0):
        stmt = (
            select(Sale)
            .order_by(Sale.created_at.desc())
            .limit(limit)
            .offset(offset)
            .options(selectinload(Sale.items))
        )
        res = await self.session.execute(stmt)
        return list(res.scalars().all())