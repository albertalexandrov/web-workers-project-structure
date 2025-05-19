from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, AnyUrl, AfterValidator, PositiveInt

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


class RetrieveArticleContentSchema(BaseModel):
    id: int
    subsection_id: int
    subtitle: str | None
    text: str | None
    video_url: str | AnyUrl | None
    order: int
    content_type: str
    widget: WidgetSchema | None


class CreateUpdateArticleContentSchema(BaseModel):
    subsection_id: PositiveInt
    subtitle: str
    text: str
    video_url: Annotated[AnyUrl | None, AfterValidator(lambda value: str(value))]
    order: int
    content_type: str
    image_id: UUID | None
    widget_id: PositiveInt
