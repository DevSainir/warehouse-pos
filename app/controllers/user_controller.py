import logging
import uuid
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError

from app.models.user import User
from app.repos.user_repo import UserRepo
from app.schemas.user import UserCreate, UserUpdate  # твои схемы
from app.core.security import hash_password  # твоя функция

logger = logging.getLogger(__name__)


class UserController:
    def __init__(self, repo: UserRepo):
        self.repo = repo

    async def list(self, limit: int, offset: int) -> list[User]:
        return await self.repo.list(limit=limit, offset=offset)

    async def get(self, user_id: uuid.UUID) -> User:
        obj = await self.repo.get_by_id(user_id)
        if not obj:
            raise HTTPException(status_code=404, detail="User not found")
        return obj

    async def create(self, data: UserCreate) -> User:
        try:
            user = User(
                name=data.name,
                role=data.role,
                is_active=getattr(data, "is_active", True),
                password_hash=hash_password(data.password),
            )
            obj = await self.repo.create(user)  
            await self.repo.session.commit()
            await self.repo.session.refresh(obj)
            return obj

        except IntegrityError:
            await self.repo.session.rollback()
            raise HTTPException(status_code=409, detail="User with this name already exists")
        except Exception:
            logger.exception("User create failed")
            await self.repo.session.rollback()
            raise

    async def update(self, user_id: uuid.UUID, data: UserUpdate) -> User:
        obj = await self.get(user_id)
        try:
            if getattr(data, "name", None) is not None:
                obj.name = data.name
            if getattr(data, "role", None) is not None:
                obj.role = data.role
            if getattr(data, "is_active", None) is not None:
                obj.is_active = data.is_active
            if getattr(data, "password", None):
                obj.password_hash = hash_password(data.password)

            await self.repo.session.commit()
            await self.repo.session.refresh(obj)
            return obj

        except IntegrityError:
            await self.repo.session.rollback()
            raise HTTPException(status_code=409, detail="User with this name already exists")
        except Exception:
            logger.exception("User update failed")
            await self.repo.session.rollback()
            raise

    async def delete(self, user_id: uuid.UUID) -> None:
        obj = await self.get(user_id)
        try:
            await self.repo.delete(obj)
            await self.repo.session.commit()
        except Exception:
            logger.exception("User delete failed")
            await self.repo.session.rollback()
            raise
