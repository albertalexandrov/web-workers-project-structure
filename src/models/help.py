from datetime import datetime
from enum import StrEnum
from uuid import UUID

from sqlalchemy import TIMESTAMP, ForeignKey, String, sql, func
from sqlalchemy import UUID as saUUID  # noqa
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, declarative_mixin, mapped_column, relationship

from candidates_for_external_lib.sa.models.mixins import TimestampzMixin
from candidates_for_external_lib.sa.models.base import Base
from candidates_for_external_lib.utils.time import utcnow


class ReferenceInfoStatus(StrEnum):
    published = "published"  # опубликованный
    unpublished = "unpublished"  # неопубликованный


class ArticleContentType(StrEnum):
    subtitle = "subtitle"  # подзаголовок
    text = "text"  # текст
    video_url = "video_url"  # видео
    image = "image"  # фото
    widget = "widget"  # виджет


@declarative_mixin
class LastActionModelMixin(TimestampzMixin):
    created_by_id: Mapped[int | None]
    updated_by_id: Mapped[int | None]


class Menu(LastActionModelMixin, Base):
    __tablename__ = "help_menu"
    __mapper_args__ = {"eager_defaults": True}
    __repr_attrs__ = ("id", "name", "order")

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    parent_id: Mapped[int | None] = mapped_column(ForeignKey("help_menu.id"))
    # parent = models.ForeignKey(
    #     verbose_name="Родитель",
    #     to="self",
    #     on_delete=models.PROTECT,
    #     related_name="children",
    #     null=True,
    #     blank=True,
    #     default=None,
    # )
    name: Mapped[str] = mapped_column(String(250), unique=True, comment="Код пункта")
    description: Mapped[str] = mapped_column(String(250), comment="Название пункта")
    image_url: Mapped[str | None] = mapped_column(String(250))
    page_url: Mapped[str | None] = mapped_column(String(250))
    order: Mapped[int]
    is_modal: Mapped[bool] = mapped_column(default=False, comment="Признак модального окна")
    modal_text: Mapped[str | None] = mapped_column(comment="Текст для модального окна")


class Section(LastActionModelMixin, Base):
    __tablename__ = "help_section"
    __repr_attrs__ = ("id", "code", "name", "status", "order")

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    code: Mapped[str | None] = mapped_column(unique=True, comment="Код")
    name: Mapped[str] = mapped_column(String(250))
    status: Mapped[str] = mapped_column(String(120), default=ReferenceInfoStatus.unpublished)
    page_url: Mapped[str | None] = mapped_column(String(250))
    order: Mapped[int] = mapped_column(default=0)
    deleted_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True), comment="Время удаления")
    subsections: Mapped[list["Subsection"]] = relationship(back_populates="section")

    @property
    def is_released(self):
        return self.status == ReferenceInfoStatus.published


class Subsection(LastActionModelMixin, Base):
    __tablename__ = "help_subsection"
    __repr_attrs__ = ("id", "code", "name", "status", "order")
    __mapper_args__ = {"eager_defaults": True}

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    section_id: Mapped[int] = mapped_column(ForeignKey("help_section.id"))
    section: Mapped[Section] = relationship(back_populates="subsections")
    code: Mapped[str | None] = mapped_column(String(100), unique=True, comment="Код")
    name: Mapped[str] = mapped_column(String(250))
    status: Mapped[str] = mapped_column(String(120), default=ReferenceInfoStatus.unpublished)
    order: Mapped[int] = mapped_column(default=0)
    document_ids: Mapped[list[UUID]] = mapped_column(ARRAY(saUUID), server_default="{}")
    deleted_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True), comment="Время удаления")
    article_content: Mapped[list["ArticleContent"]] = relationship(back_populates="subsection")

    @property
    def is_released(self):
        return self.status == ReferenceInfoStatus.published


class SubsectionDocument(Base):
    """
    Документ подраздела
    """

    __tablename__ = "help_subsectiondocument"
    __repr_attrs__ = ("id", "document_id")

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    subsection_id: Mapped[int] = mapped_column(ForeignKey("help_subsection.id"))
    subsection: Mapped[Subsection] = relationship()
    # subsection = models.ForeignKey(Subsection, on_delete=models.CASCADE)
    document_id: Mapped[UUID | None]
    created_at = mapped_column(TIMESTAMP(timezone=True), default=utcnow, server_default=func.now(), comment="Время удаления")


class ArticleContent(LastActionModelMixin, Base):
    """
    Контент статьи.
    """

    __tablename__ = "help_articlecontent"
    __mapper_args__ = {"eager_defaults": True}
    __repr_attrs__ = ("id", "subtitle", "content_type", "order")

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    subsection_id: Mapped[int] = mapped_column(ForeignKey("help_subsection.id"))
    subsection: Mapped["Subsection"] = relationship(back_populates="article_content")
    order: Mapped[int] = mapped_column(default=0)
    content_type: Mapped[str] = mapped_column(String(120), default=ArticleContentType.subtitle)
    subtitle: Mapped[str | None] = mapped_column(String(100))
    text: Mapped[str | None]
    video_url: Mapped[str | None]
    image_id: Mapped[UUID | None]
    widget_id: Mapped[int | None] = mapped_column(ForeignKey("help_widget.id"))
    widget: Mapped["Widget"] = relationship(back_populates="articles")

    @property
    def has_content(self):
        if self.content_type == ArticleContentType.image:
            return self.image_id is not None
        field_content = getattr(self, self.content_type)
        return field_content != "" and field_content is not None


class Widget(Base):
    __tablename__ = "help_widget"
    __repr_attrs__ = ("id", "code", "name")

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255))
    code: Mapped[str] = mapped_column(String(50), unique=True)
    articles: Mapped[list["ArticleContent"]] = relationship(back_populates="widget")
