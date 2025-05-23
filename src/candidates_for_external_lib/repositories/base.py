from typing import Any

from sqlalchemy import select, delete, func, literal_column
from sqlalchemy.ext.asyncio import AsyncSession

from candidates_for_external_lib.pagination import PageNumberPagination
from candidates_for_external_lib.repositories.queryset import QuerySet


class BaseRepository:
    model = None

    # todo: внедрить django-like фильтрацию?

    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, **values):
        instance = self.model(**values)
        self._session.add(instance)
        await self._session.commit()  # todo: пока так. позже подумаю, как внедрить транзакцию
        return instance

    @property
    def objects(self) -> QuerySet:
        return QuerySet(self.model, self._session)

    async def all(self):
        stmt = select(self.model)
        result = await self._session.scalars(stmt)
        return result.all()

    async def first(self):
        stmt = select(self.model).limit(1)
        return await self._session.scalar(stmt)

    async def delete(self):
        stmt = delete(self.model)
        await self._session.execute(stmt)
        await self._session.commit()  # todo: пока так. позже подумаю, как внедрить транзакцию

    async def get_list(self, query=None, pagination: PageNumberPagination | None = None, filtering=None):
        if query is None:
            query = select(self.model)
        count_query = query.with_only_columns(func.count(literal_column("1")), maintain_column_froms=True)
        if filtering:
            query = filtering.filter(query)
            query = filtering.sort(query)
            count_query = filtering.filter(count_query)
        if pagination:
            # todo:
            #  попробовать поместить логику применения пагинации в класс пагинации,
            #  который бы принимал в метод, например, paginate, sql запрос и sql возвращал запрос,
            #  как то происходит в фильтрации:
            #   query = filtering.filter(query)
            #   query = filtering.sort(query)
            offset = (pagination.page - 1) * pagination.limit
            query = query.limit(pagination.limit).offset(offset)
        result = await self._session.scalars(query)
        entries = result.unique().all()
        if pagination:
            count = await self._session.scalar(count_query)
            return {"count": count, "results": entries}
        return entries

    async def get_by_pk(self, pk_value: int):
        return await self._session.get(self.model, pk_value)

    async def delete_by_id(self, id_: Any) -> Any:
        stmt = delete(self.model).where(self.model.id == id_)
        await self._session.execute(stmt)
        await self._session.commit()  # todo: пока так. позже подумаю, как внедрить транзакцию

    # todo: другие методы
