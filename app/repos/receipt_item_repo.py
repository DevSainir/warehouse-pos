from __future__ import annotations

from typing import List
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.receipt_item import ReceiptItem


class ReceiptItemRepo:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_many(self, items: List[ReceiptItem]) -> List[ReceiptItem]:
        self.session.add_all(items)
        await self.session.flush()
        return items