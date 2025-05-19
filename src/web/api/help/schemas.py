from typing import Annotated

from pydantic import BaseModel, AnyUrl, AfterValidator

from models.help import ReferenceInfoStatus


class WidgetSchema(BaseModel):
    id: int
    name: str
    code: str


class RetrieveSectionSchema(BaseModel):
    class SubsectionSchema(BaseModel):
        id: int
        name: str
        order: int
        status: str
        code: str | None

    id: int
    code: str | None
    name: str
    status: str
    page_url: str
    order: int
    subsections: list[SubsectionSchema]


class CreateUpdateSectionSchema(BaseModel):
    name: str
    status: ReferenceInfoStatus
    page_url: Annotated[AnyUrl, AfterValidator(lambda value: str(value))]
    order: int
