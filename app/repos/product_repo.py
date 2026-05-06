from __future__ import annotations

import uuid
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.product import Product


class ProductRepo:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, product_id: uuid.UUID) -> Optional[Product]:
        stmt = (
            select(Product)
            .where(Product.id == product_id)
            .options(selectinload(Product.currency), selectinload(Product.categories))
        )
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def get_by_barcode(self, barcode: str) -> Product | None:
        stmt = (
            select(Product)
            .where(Product.barcode == barcode)
            .options(
                selectinload(Product.categories),
                selectinload(Product.currency),
            )
        )
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def get_many_by_ids(self, ids: List[uuid.UUID]) -> List[Product]:
        if not ids:
            return []
        stmt = select(Product).where(Product.id.in_(ids))
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def list_(self, limit: int = 50, offset: int = 0) -> List[Product]:
        stmt = select(Product).limit(limit).offset(offset)
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def create(self, obj: Product) -> Product:
        self.session.add(obj)
        await self.session.flush()
        return obj

    async def delete(self, obj: Product) -> None:
        await self.session.delete(obj)


    async def list_public(self, limit: int = 50, offset: int = 0, q: str | None = None):
        stmt = (
            select(Product)
            .where(Product.is_active.is_(True))
            .options(selectinload(Product.categories))
            .order_by(Product.serial_number.asc())
            .limit(limit)
            .offset(offset)
        )

        if q:
            stmt = stmt.where(Product.name.ilike(f"%{q}%"))

        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def get_public_by_id(self, product_id):
        stmt = (
            select(Product)
            .where(Product.id == product_id, Product.is_active.is_(True))
            .options(selectinload(Product.categories))
        )
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()
