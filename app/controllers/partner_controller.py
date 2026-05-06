import logging
import uuid
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError

from app.models.partner import Partner
from app.repos.partner_repo import PartnerRepo
from app.schemas.partner import PartnerCreate, PartnerUpdate

logger = logging.getLogger(__name__)


class PartnerController:
    def __init__(self, repo: PartnerRepo):
        self.repo = repo

    async def list(self, limit: int, offset: int) -> list[Partner]:
        return await self.repo.list(limit=limit, offset=offset)

    async def get(self, partner_id: uuid.UUID) -> Partner:
        obj = await self.repo.get_by_id(partner_id)
        if not obj:
            raise HTTPException(status_code=404, detail="Partner not found")
        return obj

    async def create(self, data: PartnerCreate) -> Partner:
        try:
            obj = await self.repo.create(data)
            await self.repo.session.commit()
            await self.repo.session.refresh(obj)
            return obj
        except IntegrityError:
            await self.repo.session.rollback()
            raise HTTPException(status_code=409, detail="Partner with this name already exists")
        except Exception:
            logger.exception("Partner create failed")
            await self.repo.session.rollback()
            raise

    async def update(self, partner_id: uuid.UUID, data: PartnerUpdate) -> Partner:
        obj = await self.get(partner_id)
        try:
            obj = await self.repo.update(obj, data)
            await self.repo.session.commit()
            await self.repo.session.refresh(obj)
            return obj
        except IntegrityError:
            await self.repo.session.rollback()
            raise HTTPException(status_code=409, detail="Partner with this name already exists")
        except Exception:
            logger.exception("Partner update failed")
            await self.repo.session.rollback()
            raise

    async def delete(self, partner_id: uuid.UUID) -> None:
        obj = await self.get(partner_id)
        try:
            await self.repo.delete(obj)
            await self.repo.session.commit()
        except IntegrityError:
            await self.repo.session.rollback()
            raise HTTPException(
                status_code=409,
                detail="Нельзя удалить партнера: у него есть история приходов. Используйте деактивацию.",
            )
