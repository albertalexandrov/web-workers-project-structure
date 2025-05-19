from fastapi import Depends

from candidates_for_external_lib.pagination import PageNumberPagination
from models import Section
from models.help import ReferenceInfoStatus, Subsection, ArticleContent
from shared.repositories.help import SectionsRepository, SubsectionRepository, ArticleContentRepository, \
    WidgetsRepository
from web.api.help.filters import ArticleContentFilters
from web.api.help.schemas import CreateUpdateSectionSchema, CreateUpdateArticleContentSchema
from web.api.help.utils import is_published_instance, subsection_has_content, delete_section
from web.exceptions import AnyBodyBadRequestError, NotFoundError, RequestBodyValidationError
from web.mixins import GetOr404Mixin


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
        section = await self._get_section(section_id)
        if section.is_released and data["status"] == ReferenceInfoStatus.unpublished:
            self._unpublish_child_subsections(section)
        if is_published_instance(data["status"], section):
            if subsections_wo_content := self._get_unpublished_child_subsections_wo_content(section):
                subs_names = [subs.name for subs in subsections_wo_content]
                err_msg = ["Необходимо добавить контент в подраздел(ы) (" + "; ".join(subs_names) + ";)"]
                raise AnyBodyBadRequestError(err_msg)
            self._publish_child_subsections(section)
        return section.update(**data)

    async def _get_section(self, section_id: int) -> Section:
        if section := await self._section_repository.get_section_for_update(section_id):
            # todo: заменить на метод кверисета get_one_or_raise или типа того
            return section
        raise NotFoundError

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


class SectionDeleteService(GetOr404Mixin):
    def __init__(self, section_repository: SectionsRepository = Depends()):
        self._section_repository = section_repository

    async def delete_section(self, section_id: int):
        section = await self._get_section(section_id)
        delete_section(section)

    async def _get_section(self, section_id: int) -> Section:
        section = await self._section_repository.get_section_for_update(section_id)
        # todo: заменить на метод кверисета get_one_or_raise или типа того
        return self.get_or_404(section)


class ArticleContentCreateService(GetOr404Mixin):
    def __init__(
        self,
        article_content_repository: ArticleContentRepository = Depends(),
        widget_repository: WidgetsRepository = Depends(),
        subsection_repository: SubsectionRepository = Depends(),
    ):
        self._article_content_repository = article_content_repository
        self._widget_repository = widget_repository
        self._subsection_repository = subsection_repository

    async def create_article_content(self, data: CreateUpdateArticleContentSchema) -> ArticleContent:
        validated_data = await self._validate_create_update_data(data)
        return await self._article_content_repository.create(**validated_data)

    # async def _get_article_content(self, article_content_id: int) -> ArticleContent:
    #     article_content = await self._article_content_repository.get_article_content_for_retrieve(article_content_id)
    #     # todo: заменить на метод кверисета get_one_or_raise или типа того
    #     return self.get_or_404(article_content)

    async def _validate_create_update_data(self, data: CreateUpdateArticleContentSchema) -> dict:
        validation_errors = {}
        widget = await self._widget_repository.get_by_pk(data.widget_id)
        if not widget:
            validation_errors["widget_id"] = ["Виджет не найден"]
        subsection = await self._subsection_repository.get_by_pk(data.subsection_id)
        if not subsection:
            validation_errors["subsection_id"] = ["Подраздел не найден"]
        if validation_errors:
            raise RequestBodyValidationError(validation_errors)
        data = data.model_dump()
        data.pop("widget_id")
        data["widget"] = widget
        return data
