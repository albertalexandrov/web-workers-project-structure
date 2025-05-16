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
    # прим.
    #   тут возникает неприятный эффект. если приджойнить как сконфигурировано ниже
    #   и вызвать метод QuerySet.first, то из help_subsections будет всегда максимум одна запись
    #   допустим, в таблице help_section по критерию одна запись:
    #   id | code | name | ...
    #    1 | cs1   | ns1   | ...
    #   а в таблице help_subsection две записи со ссылкой на раздел section_id=1:
    #   id | section_id | deleted_at | code | ...
    #    1 |          1 |       null | css1 | ...
    #    2 |          1 |       null | css2 | ...
    #   если сделать запрос при помощи метода QuerySet.first, то будет сгенерирован sql-запрос:
    #    SELECT help_subsection.id,
    #           help_subsection.section_id,
    #           help_subsection.code,
    #           help_subsection.name,
    #           help_subsection.status,
    #           help_subsection."order",
    #           help_subsection.document_ids,
    #           help_subsection.deleted_at,
    #           help_subsection.created_by_id,
    #           help_subsection.updated_by_id,
    #           help_subsection.created_at,
    #           help_subsection.updated_at,
    #           help_section.id            AS id_1,
    #           help_section.code          AS code_1,
    #           help_section.name          AS name_1,
    #           help_section.status        AS status_1,
    #           help_section.page_url,
    #           help_section."order"       AS order_1,
    #           help_section.deleted_at    AS deleted_at_1,
    #           help_section.created_by_id AS created_by_id_1,
    #           help_section.updated_by_id AS updated_by_id_1,
    #           help_section.created_at    AS created_at_1,
    #           help_section.updated_at    AS updated_at_1
    #    FROM help_section
    #    JOIN help_subsection ON help_section.id = help_subsection.section_id
    #    WHERE help_section.id = 1
    #      AND help_section.deleted_at IS NULL
    #      AND help_subsection.deleted_at IS NULL
    #    LIMIT 1;
    # который вернет только одну запись из help_subsection, хотя условию в filter удовлетворяют обе записи
    # поэтому при обратных join-ах следует с осторожностью использовать метод QuerySet.first
    return await repository.objects.filter(id=section_id, deleted_at__isnull=True,
                                           subsections__deleted_at__isnull=True).options('subsections').first()

# @router.put("/section/{section_id}", response_model=RetrieveSectionSchema)
# async def update_section(section_id: int, data: CreateUpdateSectionSchema, service: SectionUpdateService = Depends()):  # noqa
#     return await service.update_section(section_id, data.model_dump(exclude_unset=True))
