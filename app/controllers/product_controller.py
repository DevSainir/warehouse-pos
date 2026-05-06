from __future__ import annotations

import logging
import uuid
from decimal import Decimal, InvalidOperation

from fastapi import HTTPException, UploadFile
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.uploads import save_product_images, delete_product_images
from app.integrations.s3 import presign_get_url
from app.models.product import Product
from app.repos.product_repo import ProductRepo
from app.repos.currency_repo import CurrencyRepo
from app.repos.category_repo import CategoryRepo
from app.schemas.product import ProductCreate, ProductUpdate


logger = logging.getLogger(__name__)


class ProductController:
    def __init__(
        self,
        session: AsyncSession,
        repo: ProductRepo,
        currency_repo: CurrencyRepo,
        category_repo: CategoryRepo,
    ):
        self.session = session
        self.repo = repo
        self.currency_repo = currency_repo
        self.category_repo = category_repo

    def _with_presigned(self, obj):
        if obj.images:
            obj.image_urls = [presign_get_url(k) for k in obj.images]
        else:
            obj.image_urls = None
        return obj

    def _to_decimal(self, v: float | None, field: str) -> Decimal | None:
        if v is None:
            return None
        try:
            return Decimal(v)
        except (InvalidOperation, ValueError):
            raise HTTPException(status_code=422, detail=f"Invalid decimal for {field}")

    def _parse_category_ids(self, raw: list[str] | None) -> list[uuid.UUID] | None:
        """
        Принимает:
          - None
          - ["uuid1", "uuid2"]
          - ["uuid1,uuid2"]   (как у фронта сейчас)
          - ["uuid1", "uuid2,uuid3"] (смешанный вариант)
        Возвращает list[UUID] или None.
        """
        if raw is None:
            return None

        parts: list[str] = []
        for item in raw:
            if item is None:
                continue
            s = str(item).strip()
            if not s:
                continue
            # поддержка "uuid1,uuid2"
            parts.extend([p.strip() for p in s.split(",") if p.strip()])

        if not parts:
            return []

        out: list[uuid.UUID] = []
        for p in parts:
            try:
                out.append(uuid.UUID(p))
            except (ValueError, TypeError):
                raise HTTPException(status_code=422, detail=f"Invalid UUID in category_ids: {p}")

        return out

    async def list_(self, limit: int, offset: int) -> list[Product]:
        items = await self.repo.list_(limit=limit, offset=offset)
        return [self._with_presigned(p) for p in items]

    async def get_by_barcode(self, barcode: str) -> Product:
        obj = await self.repo.get_by_barcode(barcode)
        if not obj:
            raise HTTPException(status_code=404, detail="Product not found")
        return self._with_presigned(obj)

    async def get(self, product_id: uuid.UUID) -> Product:
        obj = await self.repo.get_by_id(product_id)
        if not obj:
            raise HTTPException(status_code=404, detail="Product not found")
        return self._with_presigned(obj)

    async def create(self, data: ProductCreate) -> Product:
        try:
            cur = await self.currency_repo.get_by_id(data.currency_id)
            if not cur:
                raise HTTPException(status_code=400, detail="Currency not found")

            exists = await self.repo.get_by_barcode(data.barcode)
            if exists:
                raise HTTPException(status_code=409, detail="Product with this barcode already exists")

            obj = Product(
                name=data.name,
                description=data.description,
                barcode=data.barcode,
                quantity=data.quantity,
                images=data.images,
                price_wo_vat=data.price_wo_vat,
                purchase_price=data.purchase_price,
                last_purchase_price=data.last_purchase_price,
                sale_price=data.sale_price,
                markup_percent=data.markup_percent,
                discount_percent=data.discount_percent,
                currency_id=data.currency_id,
                is_active=data.is_active,
            )

            if data.category_ids:
                cats = []
                for cid in data.category_ids:
                    c = await self.category_repo.get_by_id(cid)
                    if not c:
                        raise HTTPException(status_code=400, detail=f"Category not found: {cid}")
                    cats.append(c)
                obj.categories = cats

            obj = await self.repo.create(obj)
            await self.session.commit()
            await self.session.refresh(obj)

            return await self.get(obj.id)

        except HTTPException:
            await self.session.rollback()
            raise
        except IntegrityError:
            await self.session.rollback()
            raise HTTPException(status_code=409, detail="Integrity error")
        except Exception:
            logger.exception("Product create failed")
            await self.session.rollback()
            raise

    async def update(self, product_id: uuid.UUID, data: ProductUpdate) -> Product:
        obj = await self.get(product_id)

        try:
            if data.currency_id is not None:
                cur = await self.currency_repo.get_by_id(data.currency_id)
                if not cur:
                    raise HTTPException(status_code=400, detail="Currency not found")
                obj.currency_id = data.currency_id

            if data.barcode is not None and data.barcode != obj.barcode:
                exists = await self.repo.get_by_barcode(data.barcode)
                if exists:
                    raise HTTPException(status_code=409, detail="Product with this barcode already exists")
                obj.barcode = data.barcode

            if data.name is not None:
                obj.name = data.name

            if data.description is not None:
                obj.description = data.description

            if data.quantity is not None:
                obj.quantity = data.quantity

            if data.images is not None:
                if len(data.images) > 3:
                    raise HTTPException(status_code=422, detail="Max 3 images")
                obj.images = data.images

            if data.price_wo_vat is not None:
                obj.price_wo_vat = data.price_wo_vat
            if data.purchase_price is not None:
                obj.purchase_price = data.purchase_price
            if data.last_purchase_price is not None:
                obj.last_purchase_price = data.last_purchase_price
            if data.sale_price is not None:
                obj.sale_price = data.sale_price
            if data.markup_percent is not None:
                obj.markup_percent = data.markup_percent
            if data.discount_percent is not None:
                obj.discount_percent = data.discount_percent
            if data.is_active is not None:
                obj.is_active = data.is_active

            if data.category_ids is not None:
                cats = []
                for cid in data.category_ids:
                    c = await self.category_repo.get_by_id(cid)
                    if not c:
                        raise HTTPException(status_code=400, detail=f"Category not found: {cid}")
                    cats.append(c)
                obj.categories = cats

            await self.session.commit()
            await self.session.refresh(obj)
            return await self.get(obj.id)

        except HTTPException:
            await self.session.rollback()
            raise
        except IntegrityError:
            await self.session.rollback()
            raise HTTPException(status_code=409, detail="Integrity error")
        except Exception:
            logger.exception("Product update failed")
            await self.session.rollback()
            raise

    async def delete(self, product_id: uuid.UUID) -> None:
        obj = await self.get(product_id)
        try:
            await self.session.delete(obj)
            await self.session.commit()
        except IntegrityError:
            await self.session.rollback()
            raise HTTPException(
                status_code=409,
                detail="Нельзя удалить товар: у него есть история приходов. Используйте деактивацию.",
            )

    async def upload_images(self, product_id: uuid.UUID, images: list[UploadFile]):
        obj = await self.repo.get_by_id(product_id)
        if not obj:
            raise HTTPException(status_code=404, detail="Product not found")

        old_keys = list(obj.images or [])

        try:
            new_keys = await save_product_images(product_id, images)
            obj.images = new_keys
            await self.session.commit()
            await self.session.refresh(obj)

            # удаляем старые только после успешного сохранения новых
            to_delete = set(old_keys) - set(new_keys)
            if to_delete:
                await delete_product_images(to_delete)

            return await self.get(obj.id)
        except Exception:
            logger.exception("Product upload_images failed")
            await self.session.rollback()
            raise

    async def clear_images(self, product_id: uuid.UUID):
        obj = await self.repo.get_by_id(product_id)
        if not obj:
            raise HTTPException(status_code=404, detail="Product not found")

        old_keys = list(obj.images or [])

        try:
            obj.images = None
            await self.session.commit()
            await self.session.refresh(obj)

            if old_keys:
                await delete_product_images(old_keys)

            return await self.get(obj.id)
        except Exception:
            logger.exception("Product clear_images failed")
            await self.session.rollback()
            raise

    async def create_with_images(
            self,
            *,
            name,
            barcode,
            quantity,
            price_wo_vat,
            purchase_price,
            last_purchase_price,
            sale_price,
            markup_percent,
            discount_percent,
            currency_id,
            is_active,
            description,
            category_ids,
            images,
    ):
        exists = await self.repo.get_by_barcode(barcode)
        if exists:
            raise HTTPException(status_code=409, detail="Product with this barcode already exists")
        try:
            product = Product(
                name=name,
                barcode=barcode,
                quantity=quantity,
                price_wo_vat=price_wo_vat,
                purchase_price=purchase_price,
                last_purchase_price=last_purchase_price,
                sale_price=sale_price,
                markup_percent=markup_percent,
                discount_percent=discount_percent,
                currency_id=currency_id,
                is_active=is_active,
                description=description,
            )

            # категории (парсим оба формата)
            parsed = self._parse_category_ids(category_ids)
            if parsed:
                cats = []
                for cid in parsed:
                    c = await self.category_repo.get_by_id(cid)
                    if not c:
                        raise HTTPException(status_code=400, detail=f"Category not found: {cid}")
                    cats.append(c)
                product.categories = cats

            # добавляем и flush -> получаем product.id
            await self.repo.create(product)  # repo.create должен делать session.add + flush
            # если repo.create flush не делает — тогда: self.session.add(product); await self.session.flush()

            # картинки
            if images:
                keys = await save_product_images(product.id, images)
                product.images = keys

            await self.session.commit()
            return await self.get(product.id)

        except Exception:
            logger.exception("Product create_with_images failed")
            await self.session.rollback()
            raise

    async def update_with_images(
            self,
            product_id: uuid.UUID,
            *,
            name: str | None,
            description: str | None,
            barcode: str | None,
            quantity: int | None,
            price_wo_vat: str | None,
            purchase_price: str | None,
            last_purchase_price: str | None,
            sale_price: str | None,
            markup_percent: str | None,
            discount_percent: str | None,
            currency_id: uuid.UUID | None,
            is_active: bool | None,
            category_ids: list[str] | None,
            images: list[UploadFile] | None,
    ) -> Product:
        product = await self.get(product_id)

        try:
            # currency
            if currency_id is not None:
                cur = await self.currency_repo.get_by_id(currency_id)
                if not cur:
                    raise HTTPException(status_code=400, detail="Currency not found")
                product.currency_id = currency_id

            # barcode unique
            if barcode is not None and barcode != product.barcode:
                exists = await self.repo.get_by_barcode(barcode)
                if exists:
                    raise HTTPException(status_code=409, detail="Product with this barcode already exists")
                product.barcode = barcode

            # simple fields
            if name is not None:
                product.name = name
            if description is not None:
                product.description = description
            if quantity is not None:
                product.quantity = quantity

            # decimals
            d = self._to_decimal(price_wo_vat, "price_wo_vat")
            if d is not None:
                product.price_wo_vat = d
            d = self._to_decimal(purchase_price, "purchase_price")
            if d is not None:
                product.purchase_price = d
            d = self._to_decimal(last_purchase_price, "last_purchase_price")
            if d is not None:
                product.last_purchase_price = d
            d = self._to_decimal(sale_price, "sale_price")
            if d is not None:
                product.sale_price = d
            d = self._to_decimal(markup_percent, "markup_percent")
            if d is not None:
                product.markup_percent = d
            d = self._to_decimal(discount_percent, "discount_percent")
            if d is not None:
                product.discount_percent = d

            if is_active is not None:
                product.is_active = is_active

            # categories
            parsed = self._parse_category_ids(category_ids)
            if parsed is not None:
                cats = []
                for cid in parsed:
                    c = await self.category_repo.get_by_id(cid)
                    if not c:
                        raise HTTPException(status_code=400, detail=f"Category not found: {cid}")
                    cats.append(c)
                product.categories = cats

            # images (replace полностью)
            if images:
                logger.exception(images)
                # удалить старые
                if product.images:
                    await delete_product_images(product.images)

                new_urls = await save_product_images(product_id, images)  # max 3 внутри
                product.images = new_urls

            await self.repo.session.commit()
            return await self.get(product.id)

        except HTTPException:
            await self.repo.session.rollback()
            raise
        except IntegrityError:
            await self.repo.session.rollback()
            raise HTTPException(status_code=409, detail="Integrity error")
        except Exception:
            logger.exception("Product update_with_images failed")
            await self.repo.session.rollback()
            raise