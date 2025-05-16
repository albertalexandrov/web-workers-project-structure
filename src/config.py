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


settings = Settings()
print(settings)