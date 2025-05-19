from typing import Any

from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase

from candidates_for_external_lib.mixins import ReprMixin


class Base(AsyncAttrs, ReprMixin, DeclarativeBase):
    metadata = MetaData()

    def update(self, **values) -> Any:
        # это здесь, потому что существование и использование соответствующего метода в репозитории выглядит странно
        for key, value in values.items():
            setattr(self, key, value)
        return self
