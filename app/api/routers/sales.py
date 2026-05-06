import uuid
from fastapi import APIRouter, Depends, Query, status

from app.core.deps import require_admin
from app.core.factory import get_sale_controller
from app.controllers.sale_controller import SaleController
from app.schemas.sale import SaleCreateIn, SaleOut

router = APIRouter(prefix="/sales", tags=["sales"])


@router.get("/", response_model=list[SaleOut], dependencies=[Depends(require_admin)])
async def list_sales(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    ctrl: SaleController = Depends(get_sale_controller),
):
    return await ctrl.list_(limit=limit, offset=offset)


@router.get("/{sale_id}", response_model=SaleOut, dependencies=[Depends(require_admin)])
async def get_sale(
    sale_id: uuid.UUID,
    ctrl: SaleController = Depends(get_sale_controller),
):
    return await ctrl.get(sale_id)


@router.post("/", response_model=SaleOut, status_code=status.HTTP_201_CREATED)
async def create_sale(
    data: SaleCreateIn,
    ctrl: SaleController = Depends(get_sale_controller),
):
    return await ctrl.create_sale(data)