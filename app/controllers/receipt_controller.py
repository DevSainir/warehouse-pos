from __future__ import annotations

import logging
import uuid
from typing import List

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.product import Product
from app.models.receipt import Receipt
from app.models.receipt_item import ReceiptItem
from app.repos.category_repo import CategoryRepo
from app.repos.currency_repo import CurrencyRepo
from app.repos.partner_repo import PartnerRepo
from app.repos.product_repo import ProductRepo
from app.repos.receipt_repo import ReceiptRepo
from app.repos.receipt_item_repo import ReceiptItemRepo
from app.schemas.receipt import ReceiptCreateIn

logger = logging.getLogger(__name__)


class ReceiptController:
    def __init__(
        self,
        session: AsyncSession,
        receipt_repo: ReceiptRepo,
        receipt_item_repo: ReceiptItemRepo,
        product_repo: ProductRepo,
        partner_repo: PartnerRepo,
        currency_repo: CurrencyRepo,
        category_repo: CategoryRepo,
    ):
        self.session = session
        self.receipt_repo = receipt_repo
        self.receipt_item_repo = receipt_item_repo
        self.product_repo = product_repo
        self.partner_repo = partner_repo
        self.currency_repo = currency_repo
        self.category_repo = category_repo

    async def list_(self, limit: int, offset: int) -> list[Receipt]:
        return await self.receipt_repo.list(limit=limit, offset=offset)

    async def get(self, receipt_id: uuid.UUID) -> Receipt:
        obj = await self.receipt_repo.get_by_id(receipt_id)
        if not obj:
            raise HTTPException(status_code=404, detail="Receipt not found")
        return obj

    async def create_receipt(self, data: ReceiptCreateIn, created_by_id=None) -> Receipt:
        try:
            partner = await self.partner_repo.get_by_id(data.partner_id)
            if not partner:
                raise HTTPException(status_code=400, detail="Partner not found")

            receipt = Receipt(partner_id=data.partner_id, created_by_id=created_by_id)
            await self.receipt_repo.create(receipt)

            receipt_items: List[ReceiptItem] = []

            for it in data.items:
                p = it.product

                # currency must exist
                cur = await self.currency_repo.get_by_id(p.currency_id)
                if not cur:
                    raise HTTPException(status_code=400, detail=f"Currency not found: {p.currency_id}")

                product = await self.product_repo.get_by_barcode(p.barcode)

                if product is None:
                    # create
                    product = Product(
                        name=p.name,
                        description=p.description,
                        barcode=p.barcode,
                        quantity=it.quantity,
                        price_wo_vat=p.price_wo_vat,
                        purchase_price=p.purchase_price,
                        last_purchase_price=p.purchase_price,
                        sale_price=p.sale_price,
                        markup_percent=p.markup_percent,
                        discount_percent=p.discount_percent,
                        currency_id=p.currency_id,
                        is_active=p.is_active,
                    )
                    await self.product_repo.create(product)
                else:
                    # overwrite all fields coming from frontend
                    product.name = p.name
                    product.description = p.description
                    product.quantity += it.quantity
                    product.price_wo_vat = p.price_wo_vat
                    product.last_purchase_price = product.purchase_price
                    product.purchase_price = p.purchase_price
                    product.sale_price = p.sale_price
                    product.markup_percent = p.markup_percent
                    product.discount_percent = p.discount_percent
                    product.currency_id = p.currency_id
                    product.is_active = p.is_active

                # categories (replace)
                await self.session.refresh(product, attribute_names=["categories"])
                if p.category_ids:
                    cats = []
                    for cid in p.category_ids:
                        c = await self.category_repo.get_by_id(cid)
                        if not c:
                            raise HTTPException(status_code=400, detail=f"Category not found: {cid}")
                        cats.append(c)
                    product.categories = cats
                else:
                    product.categories = []

                # ReceiptItem
                receipt_items.append(
                    ReceiptItem(
                        receipt_id=receipt.id,
                        product_id=product.id,
                        quantity=it.quantity,
                        purchase_price=p.purchase_price,   # snapshot (optional)
                        currency_id=p.currency_id,
                    )
                )

            await self.receipt_item_repo.create_many(receipt_items)
            await self.session.commit()

            # reload
            obj = await self.receipt_repo.get_by_id(receipt.id)
            return obj  # type: ignore[return-value]

        except HTTPException:
            await self.session.rollback()
            raise
        except Exception:
            logger.exception("Receipt create failed")
            await self.session.rollback()
            raise