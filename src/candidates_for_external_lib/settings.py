from typing import Any

import orjson
from pydantic import BaseModel, field_validator
from sqlalchemy import URL

NON_SET = object()


class UvicornSettings(BaseModel):
    host: str = "localhost"
    port: int = 8000
    log_level: str = "info"
    reload: bool = True
    workers: int = 1
    limit_max_requests: int | None = None
    # todo: оставшиеся параметры?


class DatabaseSettings(BaseModel):
    host: str
    port: int = 5432
    username: str
    password: str
    database: str
    options: dict | None = None  # todo: может kwargs

    @field_validator("options", mode="after")  # noqa
    @classmethod
    def append_options(cls, options: dict[str, Any] | None) -> dict[str, Any]:
        options = options or {}
        if "connect_args" not in options:
            options["connect_args"] = {}
        if "server_settings" not in options["connect_args"]:
            options["connect_args"]["server_settings"] = {}
        # todo:
        #  обработать получение application_name из энвов, учитывая, что DatabaseSettings будет во внешней либе
        #  p.s. или наверно пусть будет возможность в определить в настройках DatabaseSettings
        # options["connect_args"]["server_settings"]["application_name"] = PROJECT_NAME
        options["json_serializer"] = lambda obj: orjson.dumps(obj).decode()
        options["json_deserializer"] = orjson.loads
        return options

    @property
    def dsn(self):
        return URL.create(
            drivername="postgresql+asyncpg",
            host=self.host,
            port=self.port,
            username=self.username,
            password=self.password,
            database=self.database,
        )


class ApiSettings(BaseModel):
    root: str = "/api"
    docs_enabled: bool = True
    version: str = "0.1"


class RedisBrokerSettings(BaseModel):
    host: str = "localhost"
    port: int = 6379
    # todo:
    #  другие настройки для faststream.redis.RedisBroker
    #
