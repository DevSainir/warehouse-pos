import uuid
from fastapi import APIRouter, Depends, Query, status

from app.core.deps import require_admin, get_current_user
from app.core.factory import get_user_controller
from app.controllers.user_controller import UserController
from app.schemas.user import UserCreate, UserOut, UserUpdate
from app.models.user import User


router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_model=list[UserOut], dependencies=[Depends(require_admin)])
async def list_users(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    ctrl: UserController = Depends(get_user_controller),
):
    return await ctrl.list(limit=limit, offset=offset)


@router.get("/me", response_model=UserOut)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.get("/{user_id}", response_model=UserOut, dependencies=[Depends(require_admin)])
async def get_user(
    user_id: uuid.UUID,
    ctrl: UserController = Depends(get_user_controller),
):
    return await ctrl.get(user_id)


@router.post("/", response_model=UserOut, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_admin)])
async def create_user(
    data: UserCreate,
    ctrl: UserController = Depends(get_user_controller),
):
    return await ctrl.create(data)


@router.patch("/{user_id}", response_model=UserOut, dependencies=[Depends(require_admin)])
async def update_user(
    user_id: uuid.UUID,
    data: UserUpdate,
    ctrl: UserController = Depends(get_user_controller),
):
    return await ctrl.update(user_id, data)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_admin)])
async def delete_user(
    user_id: uuid.UUID,
    ctrl: UserController = Depends(get_user_controller),
):
    await ctrl.delete(user_id)
