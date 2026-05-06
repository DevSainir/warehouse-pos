from app.models.sale_item import SaleItem


class SaleItemRepo:
    def __init__(self, session):
        self.session = session

    async def create_many(self, items: list[SaleItem]) -> list[SaleItem]:
        self.session.add_all(items)
        await self.session.flush()
        return items