from typing import List

from sqlalchemy.ext.asyncio import AsyncSession
from app.models.writeoff_item import WriteOffItem

class WriteOffItemRepo:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_many(self, items: List[WriteOffItem]) -> List[WriteOffItem]:
        self.session.add_all(items)
        await self.session.flush()
        return items