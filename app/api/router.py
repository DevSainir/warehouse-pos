from fastapi import APIRouter

from app.api.routers.auth import router as auth_router
from app.api.routers.users import router as users_router
from app.api.routers.partners import router as partners_router
from app.api.routers.currencies import router as currencies_router
from app.api.routers.categories import router as categories_router
from app.api.routers.products import router as products_router
from app.api.routers.receipts import router as receipts_router
from app.api.routers.writeoffs import router as writeoffs_router
from app.api.routers.sales import router as sales_router

api_router = APIRouter()

api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(partners_router)
api_router.include_router(currencies_router)
api_router.include_router(categories_router)
api_router.include_router(products_router)
api_router.include_router(receipts_router)
api_router.include_router(writeoffs_router)
api_router.include_router(sales_router)
