import uuid
from typing import List, Optional, Annotated, Any

from fastapi import APIRouter, Depends, Query, status, UploadFile, File, Form

from app.core.deps import require_admin
from app.core.factory import get_product_controller
from app.controllers.product_controller import ProductController
from app.schemas.product import ProductOut

router = APIRouter(prefix="/products", tags=["products"])


@router.get("/", response_model=list[ProductOut], dependencies=[Depends(require_admin)])
async def list_products(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    ctrl: ProductController = Depends(get_product_controller),
):
    return await ctrl.list_(limit=limit, offset=offset)


@router.get("/by-barcode/{barcode}", response_model=ProductOut)
async def get_product_by_barcode(
    barcode: str,
    ctrl: ProductController = Depends(get_product_controller),
):
    return await ctrl.get_by_barcode(barcode)


@router.get("/{product_id}", response_model=ProductOut, dependencies=[Depends(require_admin)])
async def get_product(
    product_id: uuid.UUID,
    ctrl: ProductController = Depends(get_product_controller),
):
    return await ctrl.get(product_id)


@router.post("/", response_model=ProductOut, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_admin)])
async def create_product(
    name: str = Form(...),
    barcode: str = Form(...),
    quantity: int = Form(...),
    price_wo_vat: float = Form(...),
    purchase_price: float = Form(...),
    last_purchase_price: float = Form(...),
    sale_price: float = Form(...),
    markup_percent: float = Form(...),
    discount_percent: float = Form(...),
    currency_id: uuid.UUID = Form(...),
    is_active: bool = Form(True),
    description: Optional[str] = Form(None),
    category_ids: Optional[List[str]] = Form(None),
    images: Optional[List[Any]] = File(None),
    ctrl: ProductController = Depends(get_product_controller),
):
    valid_images = []
    if images:
        valid_images = [img for img in images if isinstance(img, UploadFile) and img.filename]
    return await ctrl.create_with_images(
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
        category_ids=category_ids,
        images=valid_images,
    )


@router.patch("/{product_id}", response_model=ProductOut, dependencies=[Depends(require_admin)])
async def update_product(
    product_id: uuid.UUID,
    name: Annotated[str | None, Form()] = None,
    description: Annotated[str | None, Form()] = None,
    barcode: Annotated[str | None, Form()] = None,
    quantity: Annotated[int | None, Form()] = None,
    price_wo_vat: Annotated[float | None, Form()] = None,          # decimal как строка
    purchase_price: Annotated[float | None, Form()] = None,        # decimal как строка
    last_purchase_price: Annotated[float | None, Form()] = None,   # decimal как строка
    sale_price: Annotated[float | None, Form()] = None,            # decimal как строка
    markup_percent: Annotated[float | None, Form()] = None,        # decimal как строка
    discount_percent: Annotated[float | None, Form()] = None,      # decimal как строка
    currency_id: Annotated[uuid.UUID | None, Form()] = None,
    is_active: Annotated[bool | None, Form()] = None,
    category_ids: Annotated[List[str] | None, Form()] = None,          # "id1,id2,id3"
    images: list[Any] | None = File(default=None),
    ctrl: ProductController = Depends(get_product_controller),
):
    valid_images = []
    if images:
        valid_images = [img for img in images if isinstance(img, UploadFile) and img.filename]
    return await ctrl.update_with_images(
        product_id=product_id,
        name=name,
        description=description,
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
        category_ids=category_ids,
        images=valid_images,
    )


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_admin)])
async def delete_product(
    product_id: uuid.UUID,
    ctrl: ProductController = Depends(get_product_controller),
):
    await ctrl.delete(product_id)


@router.delete("/{product_id}/images", response_model=ProductOut, dependencies=[Depends(require_admin)])
async def clear_product_images(
    product_id: uuid.UUID,
    ctrl: ProductController = Depends(get_product_controller),
):
    return await ctrl.clear_images(product_id)