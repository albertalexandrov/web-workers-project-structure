from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from candidates_for_external_lib.repositories import base
from web.dependencies import get_session


class BaseRepository(base.BaseRepository):
    def __init__(self, session: AsyncSession = Depends(get_session)):
        # todo: прим:
        #  приходится переопределять __init__, чтобы внедрить зависимость get_session,
        #  которую пока не представляется, как можно импортировать из внешней библиотеки
        super().__init__(session)
