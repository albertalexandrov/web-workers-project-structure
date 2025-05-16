from fastapi import APIRouter, Depends

from shared.repositories.help import WidgetsRepository, SectionsRepository
from web.api.help.schemas import WidgetSchema, RetrieveSectionSchema, CreateUpdateSectionSchema
from web.api.help.services import CreateSectionService

router = APIRouter(tags=["Справка"])


@router.get("/widgets", response_model=list[WidgetSchema])
async def get_widgets(repository: WidgetsRepository = Depends()):
    return await repository.all()


@router.post("/section", response_model=RetrieveSectionSchema, status_code=201)
async def create_section(data: CreateUpdateSectionSchema, service: CreateSectionService = Depends()):
    return await service.create_section(data)


@router.get("/section/{section_id}", response_model=RetrieveSectionSchema)
async def get_section(section_id: int, repository: SectionsRepository = Depends()):
    return await repository.get_section_for_retrieve(section_id)  # todo: or raise 404


# @router.put("/section/{section_id}", response_model=RetrieveSectionSchema)
# async def update_section(section_id: int, data: CreateUpdateSectionSchema, service: SectionUpdateService = Depends()):  # noqa
#     return await service.update_section(section_id, data.model_dump(exclude_unset=True))
