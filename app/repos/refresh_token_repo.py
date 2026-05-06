from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.refresh_token import RefreshToken


class RefreshTokenRepo:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_jti_hash(self, jti_hash: str) -> RefreshToken | None:
        res = await self.session.execute(
            select(RefreshToken).where(RefreshToken.jti_hash == jti_hash)
        )
        return res.scalar_one_or_none()

    async def create(self, rt: RefreshToken) -> RefreshToken:
        self.session.add(rt)
        await self.session.flush()
        return rt

    def revoke(self, rt: RefreshToken) -> None:
        rt.revoked_at = datetime.utcnow()
