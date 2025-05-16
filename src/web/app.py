from pathlib import Path

from fastapi import FastAPI, APIRouter
from starlette.staticfiles import StaticFiles

from config import settings
from shared.constants import EnvironmentEnum

from web.api.docs.views import router as docs_router
from web.api.monitoring.views import router as monitoring_router
from web.middlewares import example_middleware

APP_ROOT = Path(__file__).parent


def include_routers(app: FastAPI):
    router = APIRouter(prefix=f"/{settings.api.root}")
    if settings.api.docs_enabled and settings.environment != EnvironmentEnum.PROD.value:
        app.mount(f"/{settings.api.root}/static", StaticFiles(directory=APP_ROOT / "static"), name="static")
        router.include_router(docs_router)
    router.include_router(monitoring_router)
    app.include_router(router)


def add_middlewares(app: FastAPI):
    app.middleware("http")(example_middleware)


def get_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        docs_url=None,
        openapi_url=(f"/{settings.api.root}/docs/openapi.json" if settings.api.docs_enabled else None),
        redoc_url=None,
        version=settings.api.version,
    )
    include_routers(app)
    add_middlewares(app)
    return app
