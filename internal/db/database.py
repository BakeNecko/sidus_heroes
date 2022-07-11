import logging
from asyncio import current_task
from collections.abc import Generator
from contextlib import asynccontextmanager

from sqlalchemy import orm
from sqlalchemy.ext.asyncio import (AsyncSession, async_scoped_session,
                                    create_async_engine)

from internal.db.tables.base import Base

logger = logging.getLogger(__name__)


class PostgresDatabase:
    def __init__(self, db_url: str) -> None:
        self._engine = create_async_engine(db_url, echo=True)
        self._async_session_factory = async_scoped_session(
            orm.sessionmaker(
                class_=AsyncSession,  # <- use Session.future=True mode (exclude autocommit=True)
                expire_on_commit=False,
                bind=self._engine,
            ),
            scopefunc=current_task,
        )

    async def init_db(self) -> None:
        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    @asynccontextmanager
    async def async_session(self) -> Generator[AsyncSession, None, None]:
        async_session = self._async_session_factory()
        try:
            yield async_session
        except Exception:
            logger.exception("Session rollback because of exception")
            await async_session.rollback()
            raise
        finally:
            await async_session.close()
