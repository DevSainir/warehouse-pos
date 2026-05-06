import uuid
from fastapi import APIRouter, Depends, Query, status

from app.core.deps import require_admin
from app.core.factory import get_partner_controller
from app.controllers.partner_controller import PartnerController
from app.schemas.partner import PartnerCreate, PartnerOut, PartnerUpdate

router = APIRouter(prefix="/partners", tags=["partners"])


@router.get("/", response_model=list[PartnerOut], dependencies=[Depends(require_admin)])
async def list_partners(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    ctrl: PartnerController = Depends(get_partner_controller),
):
    return await ctrl.list(limit=limit, offset=offset)


@router.get("/{partner_id}", response_model=PartnerOut, dependencies=[Depends(require_admin)])
async def get_partner(
    partner_id: uuid.UUID,
    ctrl: PartnerController = Depends(get_partner_controller),
):
    return await ctrl.get(partner_id)


@router.post("/", response_model=PartnerOut, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_admin)])
async def create_partner(
    data: PartnerCreate,
    ctrl: PartnerController = Depends(get_partner_controller),
):
    return await ctrl.create(data)


@router.patch("/{partner_id}", response_model=PartnerOut, dependencies=[Depends(require_admin)])
async def update_partner(
    partner_id: uuid.UUID,
    data: PartnerUpdate,
    ctrl: PartnerController = Depends(get_partner_controller),
):
    return await ctrl.update(partner_id, data)


@router.delete("/{partner_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_admin)])
async def delete_partner(
    partner_id: uuid.UUID,
    ctrl: PartnerController = Depends(get_partner_controller),
):
    await ctrl.delete(partner_id)
