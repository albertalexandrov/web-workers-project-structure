from typing import Any

from fastapi import Depends
from fastapi._compat import _regenerate_error_with_loc

from models import Section
from models.help import ReferenceInfoStatus
from shared.repositories.help import SectionsRepository, SubsectionRepository
from web.api.help.schemas import CreateUpdateSectionSchema
from web.exceptions import RequestBodyValidationError


class CreateSectionService:
    def __init__(
        self,
        section_repository: SectionsRepository = Depends(),
        subsection_repository: SubsectionRepository = Depends(),
    ):
        self._section_repository = section_repository
        self._subsection_repository = subsection_repository

    async def create_section(self, data: CreateUpdateSectionSchema) -> Section:
        data = await self._validate(data)
        section = await self._section_repository.create(**data, subsections=[])
        await self._subsection_repository.create(section=section, name="Новый подраздел", order=1)
        return section

    async def _validate(self, data: CreateUpdateSectionSchema) -> dict[str, Any]:
        if await self._section_repository.objects.filter(code=data.code).exists():
            raise RequestBodyValidationError({"code": "Секция с таким кодом уже существует"})
        return data.model_dump()


# class SectionUpdateService(GetOr404Mixin):
#     def __init__(self, section_repository: SectionsRepository = Depends()):
#         self._section_repository = section_repository
#
#     async def update_section(self, section_id: int, data: dict) -> Section:
#         section = await self._section_repository.get_section_for_update(section_id)
#         self.get_or_404(section)
#         if section.is_released and data["status"] == ReferenceInfoStatus.unpublished:
#             self._unpublish_child_subsections(section)
#         if is_published_instance(data["status"], section):
#             if subsections_wo_content := self._get_unpublished_child_subsections_wo_content(section):
#                 subs_names = [subs.name for subs in subsections_wo_content]
#                 err_msg = ["Необходимо добавить контент в подраздел(ы) (" + "; ".join(subs_names) + ";)"]
#                 raise AnyBodyBadRequestError(err_msg)
#             self._publish_child_subsections(section)
#         return section.update(**data)
#
#     def _publish_child_subsections(self, section: Section) -> None:
#         for ss in section.subsections:
#             ss.status = ReferenceInfoStatus.published
#
#     def _unpublish_child_subsections(self, section: Section) -> None:
#         for ss in section.subsections:
#             ss.status = ReferenceInfoStatus.unpublished
#
#     def _get_unpublished_child_subsections_wo_content(self, section: Section) -> set[Subsection]:
#         subsections_wo_content = set()
#         subsections = (
#             ss for ss in section.subsections if ss.status == ReferenceInfoStatus.unpublished and ss.deleted_at is None
#         )
#         for subsection in subsections:
#             if not subsection_has_content(subsection):
#                 subsections_wo_content.add(subsection)
#         return subsections_wo_content
