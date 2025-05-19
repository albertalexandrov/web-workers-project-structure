import logging
from pathlib import Path

import sentry_sdk
from benedict import benedict
from fastapi import FastAPI, APIRouter
from fastapi.exceptions import RequestValidationError
from prometheus_fastapi_instrumentator import PrometheusFastApiInstrumentator
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from sentry_sdk.integrations.starlette import StarletteIntegration
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.staticfiles import StaticFiles

from config import settings
from shared.constants import EnvironmentEnum

from web.api.docs.views import router as docs_router
from web.api.monitoring.views import router as monitoring_router
from web.api.help.views import router as help_router
from web.exceptions import RequestBodyValidationError, NotFoundError, AnyBodyBadRequestError
from web.i18n import locale
from web.middlewares import example_middleware

APP_ROOT = Path(__file__).parent

# todo: обработчики можно вынести в библиотеку в папку faststream, например

def request_body_validation_error_handler(request: Request, exc: RequestBodyValidationError):
    return JSONResponse(exc.validation_errors, status_code=422)


def not_found_error_handler(request: Request, exc: NotFoundError):
    return JSONResponse({"error": exc.error}, status_code=404)


def any_body_bad_request_exception_handler(request: Request, exc: AnyBodyBadRequestError) -> JSONResponse:
    return JSONResponse(status_code=400, content=exc.body)


def request_validation_error_handler(request: Request, exc):
    errors = locale.translate(exc.errors(), "ru_RU")
    content = benedict()
    for error in errors:
        key = []
        for item in error["loc"][1:]:
            key.append(item)
        key = '.'.join(key)
        content[key] = error["msg"]
    return JSONResponse(content, status_code=422)


def include_routers(app: FastAPI):
    router = APIRouter(prefix=f"/{settings.api.root}")
    if settings.api.docs_enabled and settings.environment != EnvironmentEnum.PROD.value:
        app.mount(f"/{settings.api.root}/static", StaticFiles(directory=APP_ROOT / "static"), name="static")
        router.include_router(docs_router)
    router.include_router(monitoring_router)
    router.include_router(help_router)
    app.include_router(router)


def add_middlewares(app: FastAPI):
    app.middleware("http")(example_middleware)


def setup_prometheus(app: FastAPI) -> None:  # pragma: no cover
    instrumentator = PrometheusFastApiInstrumentator(should_group_status_codes=False)
    instrumentator = instrumentator.instrument(app)
    instrumentator.expose(app, should_gzip=True, name="prometheus_metrics", tags=["Метрики"])


def get_app() -> FastAPI:
    if settings.sentry_dsn:
        sentry_sdk.init(
            dsn=settings.sentry_dsn,
            traces_sample_rate=0.1,
            environment=settings.environment,
            integrations=[
                StarletteIntegration(),
                FastApiIntegration(transaction_style="endpoint"),
                LoggingIntegration(level=logging.getLevelName(settings.log_level)),
                SqlalchemyIntegration(),
            ],
        )
    app = FastAPI(
        title=settings.app_name,
        docs_url=None,
        openapi_url=(f"/{settings.api.root}/docs/openapi.json" if settings.api.docs_enabled else None),
        redoc_url=None,
        version=settings.api.version,
        exception_handlers={
            RequestValidationError: request_validation_error_handler,
            RequestBodyValidationError: request_body_validation_error_handler,
            NotFoundError: not_found_error_handler,
            AnyBodyBadRequestError: any_body_bad_request_exception_handler,
        },
    )
    include_routers(app)
    add_middlewares(app)
    setup_prometheus(app)
    return app
