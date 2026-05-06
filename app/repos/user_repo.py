import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User

class UserRepo:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, user_id: uuid.UUID) -> User | None:
        return await self.session.get(User, user_id)

    async def get_by_name(self, name: str) -> User | None:
        res = await self.session.execute(select(User).where(User.name == name))
        return res.scalar_one_or_none()

    async def list(self, limit: int = 50, offset: int = 0) -> list[User]:
        res = await self.session.execute(select(User).limit(limit).offset(offset))
        return list(res.scalars().all())

    async def create(self, user: User) -> User:
        self.session.add(user)
        await self.session.flush()
        return user

    async def delete(self, user: User) -> None:
        await self.session.delete(user)
