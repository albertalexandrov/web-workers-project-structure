from fastapi import Depends

from models import Section
from models.help import ReferenceInfoStatus, Subsection
from shared.repositories.help import SectionsRepository, SubsectionRepository
from web.api.help.schemas import CreateUpdateSectionSchema
from web.api.help.utils import is_published_instance, subsection_has_content
from web.exceptions import AnyBodyBadRequestError, NotFoundError


class CreateSectionService:
    def __init__(
        self,
        section_repository: SectionsRepository = Depends(),
        subsection_repository: SubsectionRepository = Depends(),
    ):
        self._section_repository = section_repository
        self._subsection_repository = subsection_repository

    async def create_section(self, data: CreateUpdateSectionSchema) -> Section:
        section = await self._section_repository.create(**data.model_dump(), subsections=[])
        await self._subsection_repository.create(section=section, name="Новый подраздел", order=1)
        return section


class SectionUpdateService:
    def __init__(self, section_repository: SectionsRepository = Depends()):
        self._section_repository = section_repository

    async def update_section(self, section_id: int, data: dict) -> Section:
        if not (section := await self._section_repository.get_section_for_update(section_id)):
            # todo: заменить на метод кверисета get_one_or_raise или типа того
            raise NotFoundError
        if section.is_released and data["status"] == ReferenceInfoStatus.unpublished:
            self._unpublish_child_subsections(section)
        if is_published_instance(data["status"], section):
            if subsections_wo_content := self._get_unpublished_child_subsections_wo_content(section):
                subs_names = [subs.name for subs in subsections_wo_content]
                err_msg = ["Необходимо добавить контент в подраздел(ы) (" + "; ".join(subs_names) + ";)"]
                raise AnyBodyBadRequestError(err_msg)
            self._publish_child_subsections(section)
        return section.update(**data)

    def _publish_child_subsections(self, section: Section) -> None:
        for ss in section.subsections:
            ss.status = ReferenceInfoStatus.published

    def _unpublish_child_subsections(self, section: Section) -> None:
        for ss in section.subsections:
            ss.status = ReferenceInfoStatus.unpublished

    def _get_unpublished_child_subsections_wo_content(self, section: Section) -> set[Subsection]:
        subsections_wo_content = set()
        subsections = (
            ss for ss in section.subsections if ss.status == ReferenceInfoStatus.unpublished and ss.deleted_at is None
        )
        for subsection in subsections:
            if not subsection_has_content(subsection):
                subsections_wo_content.add(subsection)
        return subsections_wo_content
