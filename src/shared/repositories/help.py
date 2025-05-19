from sqlalchemy import select, null
from sqlalchemy.orm import selectinload

from candidates_for_external_lib.pagination import PageNumberPagination
from models import Widget, Section, Subsection
from shared.repositories.base import BaseRepository
from web.api.help.filters import SectionFilters


class WidgetsRepository(BaseRepository):
    model = Widget


class SectionsRepository(BaseRepository):
    model = Section

    async def get_section_for_retrieve(self, section_id: int) -> Section | None:
        # todo: кандидат на замену методом кверисета
        stmt = (
            select(self.model)
            .where(self.model.id == section_id, self.model.deleted_at.is_(null()))
            .options(selectinload(self.model.subsections.and_(Subsection.deleted_at.is_(null()))))
        )
        return await self._session.scalar(stmt)

    async def get_section_for_update(self, section_id: int) -> Section | None:
        # todo: кандидат на замену методом кверисета
        stmt = (
            select(self.model)
            .where(
                self.model.id == section_id,
                self.model.deleted_at.is_(null()),
            )
            .options(
                selectinload(self.model.subsections.and_(Subsection.deleted_at.is_(null()))).selectinload(
                    Subsection.article_content
                )
            )
        )
        return await self._session.scalar(stmt)

    async def get_list_w_subsections(
        self, filtering: SectionFilters = None, pagination: PageNumberPagination | None = None
    ):
        # todo: кандидат на замену методом кверисета
        stmt = (
            select(self.model)
            .where(self.model.deleted_at.is_(null()))
            .options(selectinload(self.model.subsections.and_(Subsection.deleted_at.is_(null()))))
        )
        return await self.get_list(stmt, pagination, filtering)


class SubsectionRepository(BaseRepository):
    model = Subsection
