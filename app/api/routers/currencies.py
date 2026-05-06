import uuid
from fastapi import APIRouter, Depends, Query, status

from app.core.deps import require_admin
from app.core.factory import get_currency_controller
from app.controllers.currency_controller import CurrencyController
from app.schemas.currency import CurrencyCreate, CurrencyOut, CurrencyUpdate

router = APIRouter(prefix="/currencies", tags=["currencies"])


@router.get("/", response_model=list[CurrencyOut], dependencies=[Depends(require_admin)])
async def list_currencies(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    ctrl: CurrencyController = Depends(get_currency_controller),
):
    return await ctrl.list(limit=limit, offset=offset)


@router.get("/{currency_id}", response_model=CurrencyOut, dependencies=[Depends(require_admin)])
async def get_currency(
    currency_id: uuid.UUID,
    ctrl: CurrencyController = Depends(get_currency_controller),
):
    return await ctrl.get(currency_id)


@router.post("/", response_model=CurrencyOut, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_admin)])
async def create_currency(
    data: CurrencyCreate,
    ctrl: CurrencyController = Depends(get_currency_controller),
):
    return await ctrl.create(data)


@router.patch("/{currency_id}", response_model=CurrencyOut, dependencies=[Depends(require_admin)])
async def update_currency(
    currency_id: uuid.UUID,
    data: CurrencyUpdate,
    ctrl: CurrencyController = Depends(get_currency_controller),
):
    return await ctrl.update(currency_id, data)


@router.delete("/{currency_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_admin)])
async def delete_currency(
    currency_id: uuid.UUID,
    ctrl: CurrencyController = Depends(get_currency_controller),
):
    await ctrl.delete(currency_id)
