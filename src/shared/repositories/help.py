from sqlalchemy import select, null
from sqlalchemy.orm import selectinload

from candidates_for_external_lib.repositories.queryset import QuerySet
from models import Widget, Section, Subsection
from shared.repositories.base import BaseRepository


class WidgetsRepository(BaseRepository):
    model = Widget


class SectionsRepository(BaseRepository):
    model = Section

    async def get_section_for_retrieve(self, section_id: int) -> Section | None:
        stmt = (
            select(self.model)
            .where(self.model.id == section_id, self.model.deleted_at.is_(null()))
            .options(selectinload(self.model.subsections.and_(Subsection.deleted_at.is_(null()))))
        )
        return await self._session.scalar(stmt)


class SubsectionRepository(BaseRepository):
    model = Subsection
