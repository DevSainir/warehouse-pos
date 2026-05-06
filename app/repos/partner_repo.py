import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.partner import Partner
from app.schemas.partner import PartnerCreate, PartnerUpdate


class PartnerRepo:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, partner_id: uuid.UUID) -> Partner | None:
        res = await self.session.execute(select(Partner).where(Partner.id == partner_id))
        return res.scalar_one_or_none()

    async def get_by_name(self, name: str) -> Partner | None:
        res = await self.session.execute(select(Partner).where(Partner.name == name))
        return res.scalar_one_or_none()

    async def list(self, *, limit: int = 50, offset: int = 0) -> list[Partner]:
        res = await self.session.execute(
            select(Partner)
            .order_by(Partner.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(res.scalars().all())

    async def create(self, data: PartnerCreate) -> Partner:
        obj = Partner(name=data.name, comment=data.comment)
        self.session.add(obj)
        await self.session.flush()
        return obj

    async def update(self, obj: Partner, data: PartnerUpdate) -> Partner:
        if data.name is not None:
            obj.name = data.name
        # comment: None означает "очистить"
        if data.comment is not None or data.comment is None:
            obj.comment = data.comment
        if data.comment is not None or data.comment is None:
            obj.comment = data.comment
        if data.is_active is not None:
            obj.is_active = data.is_active
        await self.session.flush()
        return obj

    async def delete(self, obj: Partner) -> None:
        await self.session.delete(obj)
