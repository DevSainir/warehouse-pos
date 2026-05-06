from fastapi import APIRouter

from app.api.routers.warehouse import warehouse_router

api_router = APIRouter()

api_router.include_router(warehouse_router)
