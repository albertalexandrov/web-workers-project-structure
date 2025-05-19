from fastapi_filter.contrib.sqlalchemy import Filter

from models import Section, ArticleContent

# todo: кастомный базовый класс фильтрации от Сережи

class SectionFilters(Filter):
    ordering: list[str] | None = ["id"]

    class Constants(Filter.Constants):
        model = Section
        ordering_field_name = "ordering"


class ArticleContentFilters(Filter):
    ordering: list[str] | None = ["id"]

    class Constants(Filter.Constants):
        model = ArticleContent
        ordering_field_name = "ordering"
