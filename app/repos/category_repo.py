import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryUpdate


class CategoryRepo:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, category_id: uuid.UUID) -> Category | None:
        res = await self.session.execute(select(Category).where(Category.id == category_id))
        return res.scalar_one_or_none()

    async def get_by_name(self, name: str) -> Category | None:
        res = await self.session.execute(select(Category).where(Category.name == name))
        return res.scalar_one_or_none()

    async def list(self, *, limit: int = 50, offset: int = 0) -> list[Category]:
        res = await self.session.execute(
            select(Category)
            .order_by(Category.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(res.scalars().all())

    async def create(self, data: CategoryCreate) -> Category:
        obj = Category(name=data.name)
        self.session.add(obj)
        await self.session.flush()
        return obj

    async def update(self, obj: Category, data: CategoryUpdate) -> Category:
        if data.name is not None:
            obj.name = data.name
        await self.session.flush()
        return obj

    async def delete(self, obj: Category) -> None:
        await self.session.delete(obj)


    async def list_public(self, limit: int = 100, offset: int = 0):
        stmt = (
            select(Category)
            .options(selectinload(Category.products))
            .order_by(Category.name.asc())
            .limit(limit)
            .offset(offset)
        )
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def get_public_by_id(self, category_id):
        stmt = (
            select(Category)
            .options(selectinload(Category.products))
            .where(Category.id == category_id)
        )
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()
