from datetime import datetime

from sqlalchemy import TIMESTAMP, func
from sqlalchemy.orm import declarative_mixin, Mapped, mapped_column

from candidates_for_external_lib.utils.time import utcnow


@declarative_mixin
class TimestampzMixin:
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        default=utcnow,  # будет подставлено при insert
        server_default=func.now(),
        comment="Дата и время создания записи",
    )
    # на стороне СУБД вроде нет возможности обновлять поле при обновлении записи, поэтому без server_onupdate
    updated_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP(timezone=True),
        onupdate=utcnow,  # будет подставлено при update
        comment="Дата и время обновления записи",
    )
