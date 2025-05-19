"""
Конфиги на одном уровне с web и tasks, тк они используются и там и там
Конфиги UvicornSettings, DatabaseSettings, ApiSettings предполагается, что будут вынесены в библиотеку,
и поэтому сделаны подключаемыми (отнаседованы от BaseModel) к настройками проекта (отнаследованы от BaseSettings)
Потом экземпляр S3Settings (не существует) может быть передан, например, в класс S3Storage
"""

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from candidates_for_external_lib.settings import DatabaseSettings, UvicornSettings, ApiSettings
from shared.constants import EnvironmentEnum

ENVIRONMENT = EnvironmentEnum.get_environment()

if ENVIRONMENT == EnvironmentEnum.LOCAL:
    load_dotenv()


class Settings(BaseSettings):
    app_name: str = "Мое приложение"
    environment: str = ENVIRONMENT
    log_level: str = "INFO"
    uvicorn: UvicornSettings = Field(default_factory=UvicornSettings)
    db: DatabaseSettings = Field(default_factory=DatabaseSettings)
    api: ApiSettings = Field(default_factory=ApiSettings)
    sentry_dsn: str | None = None

    model_config = SettingsConfigDict(env_prefix="MY_PROJECT__", env_nested_delimiter="__")
    # пример переменных окружения:
    #   MY_PROJECT__UVICORN__APP=web.app:get_app
    #   MY_PROJECT__UVICORN__HOST=localhost
    #   MY_PROJECT__UVICORN__PORT=8000
    #   MY_PROJECT__DB__HOST=localhost
    #   MY_PROJECT__DB__PORT=5433
    #   MY_PROJECT__DB__USERNAME=postgres
    #   MY_PROJECT__DB__PASSWORD=postgres
    #   MY_PROJECT__DB__DATABASE=project-structure
    #   MY_PROJECT__DB__OPTIONS={"echo": true}
    #   MY_PROJECT__API__ROOT=api
    #   MY_PROJECT__API__DOCS_ENABLED=true
    #   MY_PROJECT__API__VERSION=0.2
    #   MY_PROJECT__SENTRY_DSN=


settings = Settings()
