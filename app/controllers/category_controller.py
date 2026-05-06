import logging
import uuid
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError

from app.models.category import Category
from app.repos.category_repo import CategoryRepo
from app.schemas.category import CategoryCreate, CategoryUpdate

logger = logging.getLogger(__name__)


class CategoryController:
    def __init__(self, repo: CategoryRepo):
        self.repo = repo

    async def list(self, limit: int, offset: int) -> list[Category]:
        return await self.repo.list(limit=limit, offset=offset)

    async def get(self, category_id: uuid.UUID) -> Category:
        obj = await self.repo.get_by_id(category_id)
        if not obj:
            raise HTTPException(status_code=404, detail="Category not found")
        return obj

    async def create(self, data: CategoryCreate) -> Category:
        try:
            obj = await self.repo.create(data)
            await self.repo.session.commit()
            await self.repo.session.refresh(obj)
            return obj
        except IntegrityError:
            await self.repo.session.rollback()
            raise HTTPException(status_code=409, detail="Category with this name already exists")
        except Exception:
            logger.exception("Category create failed")
            await self.repo.session.rollback()
            raise

    async def update(self, category_id: uuid.UUID, data: CategoryUpdate) -> Category:
        obj = await self.get(category_id)
        try:
            obj = await self.repo.update(obj, data)
            await self.repo.session.commit()
            await self.repo.session.refresh(obj)
            return obj
        except IntegrityError:
            await self.repo.session.rollback()
            raise HTTPException(status_code=409, detail="Category with this name already exists")
        except Exception:
            logger.exception("Category update failed")
            await self.repo.session.rollback()
            raise

    async def delete(self, category_id: uuid.UUID) -> None:
        obj = await self.get(category_id)
        try:
            await self.repo.delete(obj)
            await self.repo.session.commit()
        except Exception:
            logger.exception("Category delete failed")
            await self.repo.session.rollback()
            raise
