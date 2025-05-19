from typing import Annotated

from fastapi import Query

# todo: может в отдельный пакет


class PageNumberPagination:
    def __init__(
        self,
        page: Annotated[int, Query(gt=0)] = 1,
        limit: Annotated[int, Query(gt=0), Query(le=100)] = 10,
    ):
        # todo: как параметризовать, если выносим в библиотеку?
        self.page = page
        self.limit = limit

    # todo:
    #  может получиться реализовать применение пагинации как и в случае
    #  с фильтрами и сортировкой, то есть в классе пагинации
