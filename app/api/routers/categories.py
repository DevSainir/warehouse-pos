import uuid
from fastapi import APIRouter, Depends, Query, status

from app.core.deps import require_admin
from app.core.factory import get_category_controller
from app.controllers.category_controller import CategoryController
from app.schemas.category import CategoryCreate, CategoryOut, CategoryUpdate

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("/", response_model=list[CategoryOut], dependencies=[Depends(require_admin)])
async def list_categories(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    ctrl: CategoryController = Depends(get_category_controller),
):
    return await ctrl.list(limit=limit, offset=offset)


@router.get("/{category_id}", response_model=CategoryOut, dependencies=[Depends(require_admin)])
async def get_category(
    category_id: uuid.UUID,
    ctrl: CategoryController = Depends(get_category_controller),
):
    return await ctrl.get(category_id)


@router.post("/", response_model=CategoryOut, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_admin)])
async def create_category(
    data: CategoryCreate,
    ctrl: CategoryController = Depends(get_category_controller),
):
    return await ctrl.create(data)


@router.patch("/{category_id}", response_model=CategoryOut, dependencies=[Depends(require_admin)])
async def update_category(
    category_id: uuid.UUID,
    data: CategoryUpdate,
    ctrl: CategoryController = Depends(get_category_controller),
):
    return await ctrl.update(category_id, data)


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_admin)])
async def delete_category(
    category_id: uuid.UUID,
    ctrl: CategoryController = Depends(get_category_controller),
):
    await ctrl.delete(category_id)
