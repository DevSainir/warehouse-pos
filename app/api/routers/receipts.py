import uuid
from fastapi import APIRouter, Depends, Query, status

from app.core.deps import require_admin
from app.core.factory import get_receipt_controller
from app.controllers.receipt_controller import ReceiptController
from app.schemas.receipt import ReceiptCreateIn, ReceiptOut

router = APIRouter(prefix="/receipts", tags=["receipts"])


@router.get("/", response_model=list[ReceiptOut], dependencies=[Depends(require_admin)])
async def list_receipts(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    ctrl: ReceiptController = Depends(get_receipt_controller),
):
    return await ctrl.list_(limit=limit, offset=offset)


@router.get("/{receipt_id}", response_model=ReceiptOut, dependencies=[Depends(require_admin)])
async def get_receipt(
    receipt_id: uuid.UUID,
    ctrl: ReceiptController = Depends(get_receipt_controller),
):
    return await ctrl.get(receipt_id)


@router.post("/", response_model=ReceiptOut, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_admin)])
async def create_receipt(
    data: ReceiptCreateIn,
    ctrl: ReceiptController = Depends(get_receipt_controller),
):
    # если хочешь сохранять created_by_id:
    # user = Depends(get_current_user) и передать user.id
    return await ctrl.create_receipt(data)