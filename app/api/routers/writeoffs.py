from fastapi import APIRouter, Depends, Query

from app.core.deps import require_admin
from app.core.factory import get_writeoff_controller
from app.controllers.writeoff_controller import WriteOffController
from app.schemas.writeoff import WriteOffCreateIn, WriteOffOut
import uuid

router = APIRouter(prefix="/writeoffs", tags=["WriteOffs"])

@router.get("/", response_model=list[WriteOffOut], dependencies=[Depends(require_admin)])
async def list_writeoffs(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    ctrl: WriteOffController = Depends(get_writeoff_controller),
):
    return await ctrl.list_(limit=limit, offset=offset)

@router.get("/{writeoff_id}", response_model=WriteOffOut, dependencies=[Depends(require_admin)])
async def get_writeoff(
    writeoff_id: uuid.UUID,
    ctrl: WriteOffController = Depends(get_writeoff_controller),
):
    return await ctrl.get_by_id(writeoff_id)

@router.post("/", response_model=WriteOffOut, dependencies=[Depends(require_admin)])
async def create_writeoff(
    data: WriteOffCreateIn,
    ctrl: WriteOffController = Depends(get_writeoff_controller),
):
    obj = await ctrl.create_writeoff(data)
    return await ctrl.get_by_id(obj.id)