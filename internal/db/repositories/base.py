import abc
from contextlib import AbstractContextManager
from typing import Callable, Generic, Type, TypeVar

from asyncpg import UniqueViolationError
from sqlalchemy import delete, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from internal.db.errors import UserAlreadyExists
from internal.models.schemas import BaseSchema

IN_SCHEMA = TypeVar("IN_SCHEMA", bound=BaseSchema)
SCHEMA = TypeVar("SCHEMA", bound=BaseSchema)
TABLE = TypeVar("TABLE")


class BaseRepository(Generic[IN_SCHEMA, SCHEMA, TABLE], metaclass=abc.ABCMeta):

    def __init__(self, context_async_session: Callable[..., AbstractContextManager[AsyncSession]]) -> None:
        self.context_async_session = context_async_session

    @property
    @abc.abstractmethod
    def _in_schema(self) -> Type[IN_SCHEMA]:
        ...

    @property
    @abc.abstractmethod
    def _table(self) -> Type[TABLE]:
        ...

    @property
    @abc.abstractmethod
    def _schema(self) -> Type[SCHEMA]:
        ...

    async def create(self, in_schema: IN_SCHEMA) -> SCHEMA | None:
        session: AsyncSession

        async with self.context_async_session() as session:
            entry = self._table(**in_schema.dict())
            session.add(entry)
            try:
                await session.commit()
                return self._schema.from_orm(entry)
            except (IntegrityError, UniqueViolationError):
                return None

    async def get_by_id(self, entry_id: int) -> SCHEMA | None:
        session: AsyncSession

        async with self.context_async_session() as session:
            entry = await session.get(self._table, entry_id)
            if not entry:
                return None
            return self._schema.from_orm(entry)

    async def get(self, **filters) -> SCHEMA | None:
        session: AsyncSession

        async with self.context_async_session() as session:
            q = select(self._table).filter_by(**filters)
            entry = await session.execute(q)
            if result := entry.scalar():
                return self._schema.from_orm(result)
            else:
                return result

    async def update_by_id(self, _id: int, **fields) -> SCHEMA | None:
        session: AsyncSession

        async with self.context_async_session() as session:
            q = update(self._table).where(self._table.id == _id).values(**fields).returning(self._table)
            result = (await session.execute(q)).fetchone()
            await session.commit()
            if result:
                return self._schema.from_orm(result)
            return result

    async def delete_by_id(self, _id: int) -> bool:
        session: AsyncSession

        async with self.context_async_session() as session:
            q = delete(self._table).where(self._table.id == _id)
            result = await session.execute(q)
            await session.commit()
            return bool(result.rowcount)
