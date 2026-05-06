import logging
from decimal import Decimal

from fastapi import HTTPException

from app.models.sale import Sale
from app.models.sale_item import SaleItem
from app.repos.partner_repo import PartnerRepo
from app.repos.product_repo import ProductRepo
from app.repos.sale_repo import SaleRepo
from app.repos.sale_item_repo import SaleItemRepo
from app.schemas.sale import SaleCreateIn

logger = logging.getLogger(__name__)


class SaleController:
    def __init__(
        self,
        session,
        partner_repo: PartnerRepo,
        product_repo: ProductRepo,
        sale_repo: SaleRepo,
        sale_item_repo: SaleItemRepo,
    ):
        self.session = session
        self.partner_repo = partner_repo
        self.product_repo = product_repo
        self.sale_repo = sale_repo
        self.sale_item_repo = sale_item_repo

    async def get(self, sale_id):
        obj = await self.sale_repo.get_by_id(sale_id)
        if not obj:
            raise HTTPException(status_code=404, detail="Sale not found")
        return obj

    async def list_(self, limit: int, offset: int):
        return await self.sale_repo.list_(limit=limit, offset=offset)

    async def create_sale(self, data: SaleCreateIn, created_by_id=None):
        try:
            partner = await self.partner_repo.get_by_id(data.partner_id)
            if not partner:
                raise HTTPException(status_code=400, detail="Partner not found")

            if not data.items:
                raise HTTPException(status_code=400, detail="Items are required")

            sale_items: list[SaleItem] = []
            total_amount = Decimal("0")

            sale = Sale(
                partner_id=data.partner_id,
                total_amount=Decimal("0"),
                created_by_id=created_by_id,
            )
            await self.sale_repo.create(sale)

            for item in data.items:
                product = await self.product_repo.get_by_barcode(item.barcode)
                if not product:
                    raise HTTPException(status_code=400, detail="Product not found")

                if product.quantity < item.quantity:
                    raise HTTPException(
                        status_code=409,
                        detail="Not enough stock",
                    )

                amount = item.price * item.quantity

                if item.amount is not None and item.amount != amount:
                    raise HTTPException(
                        status_code=409,
                        detail="Invalid amount",
                    )

                product.quantity -= item.quantity

                sale_items.append(
                    SaleItem(
                        sale_id=sale.id,
                        product_id=product.id,
                        quantity=item.quantity,
                        price=item.price,
                        amount=amount,
                    )
                )

                total_amount += amount

            if data.total_amount is not None and data.total_amount != total_amount:
                raise HTTPException(status_code=409, detail="Invalid total amount")

            sale.total_amount = total_amount

            await self.sale_item_repo.create_many(sale_items)
            await self.session.commit()

            return await self.get(sale.id)

        except HTTPException:
            await self.session.rollback()
            raise
        except Exception:
            logger.exception("Sale create failed")
            await self.session.rollback()
            raise