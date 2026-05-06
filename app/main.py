from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from app.core.config import settings
from app.api.router import api_router
from app.core.logging_custom import setup_logging

from starlette.middleware.cors import CORSMiddleware

setup_logging()

app = FastAPI(title=settings.APP_NAME)
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="warehouse",
        version="1.0.0",
        description="API",
        routes=app.routes,
    )
    openapi_schema.setdefault("components", {}).setdefault("securitySchemes", {})["HTTPBearer"] = {
        "type": "http",
        "scheme": "bearer",
        "bearerFormat": "JWT",
    }
    # делаем авторизацию глобальной по умолчанию (можно убрать, если не хочешь)
    openapi_schema["security"] = [{"HTTPBearer": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi