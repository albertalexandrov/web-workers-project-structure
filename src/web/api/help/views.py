from fastapi import APIRouter, Depends
from fastapi_filter import FilterDepends

from candidates_for_external_lib.responses.paginated import PaginatedResponse
from candidates_for_external_lib.pagination import PageNumberPagination
from shared.repositories.help import WidgetsRepository, SectionsRepository, ArticleContentRepository
from web.api.help.filters import SectionFilters, ArticleContentFilters
from web.api.help.schemas import WidgetSchema, RetrieveSectionSchema, CreateUpdateSectionSchema, \
    RetrieveArticleContentSchema, CreateUpdateArticleContentSchema
from web.api.help.services import CreateSectionService, SectionUpdateService, SectionDeleteService, \
    ArticleContentCreateService
from web.exceptions import NotFoundError

router = APIRouter(tags=["Справка"])


@router.get("/widgets", response_model=list[WidgetSchema])
async def get_widgets(repository: WidgetsRepository = Depends()):
    return await repository.all()


@router.post("/section", response_model=RetrieveSectionSchema, status_code=201)
async def create_section(data: CreateUpdateSectionSchema, service: CreateSectionService = Depends()):
    # todo:
    #  разобраться с ситуацией, когда при использовании зависимости, сначала происходит сериализация,
    #  и только потом коммит. возможно создавать сессию в виде декоратора для вьюхи
    return await service.create_section(data)


@router.get("/section/{section_id}", response_model=RetrieveSectionSchema)
async def get_section(section_id: int, repository: SectionsRepository = Depends()):
    if section := await repository.get_section_for_retrieve(section_id):
        # todo: заменить на метод кверисета get_one_or_raise или типа того
        return section
    raise NotFoundError


@router.put("/section/{section_id}", response_model=RetrieveSectionSchema)
async def update_section(section_id: int, data: CreateUpdateSectionSchema, service: SectionUpdateService = Depends()):
    return await service.update_section(section_id, data.model_dump(exclude_unset=True))


@router.delete("/section/{section_id}", status_code=204)
async def delete_section(section_id: int, service: SectionDeleteService = Depends()):
    await service.delete_section(section_id)


@router.get("/section", response_model=PaginatedResponse[RetrieveSectionSchema])
async def get_sections(
    filtering: SectionFilters = FilterDepends(SectionFilters),
    pagination: PageNumberPagination = Depends(),
    repository: SectionsRepository = Depends(),
):
    return await repository.get_list_w_subsections(filtering, pagination)


@router.get("/article_content", response_model=PaginatedResponse[RetrieveArticleContentSchema])
async def get_article_contents(
    filtering: ArticleContentFilters = FilterDepends(ArticleContentFilters),
    pagination: PageNumberPagination = Depends(),
    repository: ArticleContentRepository = Depends(),
):
    return await repository.get_list_w_widgets(filtering, pagination)


@router.post("/article_content", response_model=RetrieveArticleContentSchema, status_code=201)
async def create_article_content(
    data: CreateUpdateArticleContentSchema, service: ArticleContentCreateService = Depends()
):
    return await service.create_article_content(data)
