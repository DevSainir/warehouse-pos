import logging
from typing import List

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.writeoff import WriteOff
from app.models.writeoff_item import WriteOffItem
from app.repos.partner_repo import PartnerRepo
from app.repos.product_repo import ProductRepo
from app.repos.writeoff_repo import WriteOffRepo
from app.repos.writeoff_item_repo import WriteOffItemRepo
from app.schemas.writeoff import WriteOffCreateIn

logger = logging.getLogger(__name__)

class WriteOffController:
    def __init__(
        self,
        session: AsyncSession,
        product_repo: ProductRepo,
        partner_repo: PartnerRepo,
        writeoff_repo: WriteOffRepo,
        writeoff_item_repo: WriteOffItemRepo,
    ):
        self.partner_repo = partner_repo
        self.session = session
        self.product_repo = product_repo
        self.writeoff_repo = writeoff_repo
        self.writeoff_item_repo = writeoff_item_repo

    async def list_(self, limit: int, offset: int) -> list[WriteOff]:
        return await self.writeoff_repo.list(limit=limit, offset=offset)

    async def get_by_id(self, writeoff_id):
        obj = await self.writeoff_repo.get_by_id(writeoff_id)
        if not obj:
            raise HTTPException(status_code=404, detail="WriteOff not found")
        return obj

    async def create_writeoff(self, data: WriteOffCreateIn, created_by_id=None) -> WriteOff:
        try:
            partner = await self.partner_repo.get_by_id(data.partner_id)
            if not partner:
                raise HTTPException(status_code=400, detail="Partner not found")

            writeoff = WriteOff(
                partner_id=data.partner_id,
                created_by_id=created_by_id,
            )
            await self.writeoff_repo.create(writeoff)
            writeoff_items: List[WriteOffItem] = []

            for it in data.items:
                p = it.product
            
                product = await self.product_repo.get_by_barcode(p.barcode)
                if not product:
                    raise HTTPException(status_code=400, detail="Product not found")

                if product.quantity < it.quantity:
                    raise HTTPException(status_code=409, detail="Not enough stock")

                writeoff_items.append(
                    WriteOffItem(
                        writeoff_id=writeoff.id,
                        product_id=product.id,
                        quantity=it.quantity,
                        purchase_price=p.purchase_price,
                        sale_price=p.sale_price,
                    )
                )

                # обновляем остаток
                product.quantity = product.quantity - it.quantity

            await self.writeoff_item_repo.create_many(writeoff_items)
            await self.session.commit()

            await self.session.refresh(writeoff, attribute_names=["items"])
            obj = await self.writeoff_repo.get_by_id(writeoff.id)
            return obj

        except HTTPException:
            await self.session.rollback()
            raise
        except Exception:
            logger.exception("WriteOff create failed")
            await self.session.rollback()
            raise