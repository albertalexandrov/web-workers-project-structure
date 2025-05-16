from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from candidates_for_external_lib.repositories import mixin


class BaseRepository(mixin.BaseRepository):
    def __init__(self, session: AsyncSession = Depends(get_session)):
        super().__init__(session)
