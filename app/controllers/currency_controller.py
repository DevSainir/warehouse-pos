import logging
import uuid
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError

from app.models.currency import Currency
from app.repos.currency_repo import CurrencyRepo
from app.schemas.currency import CurrencyCreate, CurrencyUpdate

logger = logging.getLogger(__name__)


class CurrencyController:
    def __init__(self, repo: CurrencyRepo):
        self.repo = repo

    async def list(self, limit: int, offset: int) -> list[Currency]:
        return await self.repo.list(limit=limit, offset=offset)

    async def get(self, currency_id: uuid.UUID) -> Currency:
        obj = await self.repo.get_by_id(currency_id)
        if not obj:
            raise HTTPException(status_code=404, detail="Currency not found")
        return obj

    async def create(self, data: CurrencyCreate) -> Currency:
        try:
            obj = await self.repo.create(Currency(name=data.name))
            await self.repo.session.commit()
            await self.repo.session.refresh(obj)
            return obj
        except IntegrityError:
            await self.repo.session.rollback()
            raise HTTPException(status_code=409, detail="Currency with this name already exists")
        except Exception:
            logger.exception("Currency create failed")
            await self.repo.session.rollback()
            raise

    async def update(self, currency_id: uuid.UUID, data: CurrencyUpdate) -> Currency:
        obj = await self.get(currency_id)
        try:
            if data.name is not None:
                obj.name = data.name
            await self.repo.session.commit()
            await self.repo.session.refresh(obj)
            return obj
        except IntegrityError:
            await self.repo.session.rollback()
            raise HTTPException(status_code=409, detail="Currency with this name already exists")
        except Exception:
            logger.exception("Currency update failed")
            await self.repo.session.rollback()
            raise

    async def delete(self, currency_id: uuid.UUID) -> None:
        obj = await self.get(currency_id)
        try:
            await self.repo.delete(obj)
            await self.repo.session.commit()
        except Exception:
            logger.exception("Currency delete failed")
            await self.repo.session.rollback()
            raise
