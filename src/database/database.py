"""
SQLAlchemy async engine + sessionmaker + dependency get_session().

Упрощённая версия appss-back/src/database/database.py.
"""

import asyncio
import logging
from contextlib import suppress
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import declarative_base

from config import get_config


Base = declarative_base()


class SQLAlchemyManager:
    logger = logging.getLogger("sqlalchemy")
    _engine: AsyncEngine | None = None
    _sessionmaker: async_sessionmaker[AsyncSession] | None = None

    @classmethod
    def get_async_engine(cls) -> AsyncEngine:
        if cls._engine is not None:
            return cls._engine

        url = get_config().db.url
        cls._engine = create_async_engine(
            url,
            pool_pre_ping=True,
            pool_size=5,
            max_overflow=5,
            pool_timeout=15,
            pool_recycle=1800,
            echo=False,
        )
        return cls._engine

    @classmethod
    def get_sessionmaker(cls) -> async_sessionmaker[AsyncSession]:
        if cls._sessionmaker is not None:
            return cls._sessionmaker

        engine = cls.get_async_engine()
        cls._sessionmaker = async_sessionmaker(
            bind=engine,
            autoflush=False,
            expire_on_commit=False,
            class_=AsyncSession,
        )
        return cls._sessionmaker


SessionLocal = SQLAlchemyManager.get_sessionmaker()


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI-зависимость: открывает сессию, коммитит или роллбэкает, закрывает."""
    session: AsyncSession = SessionLocal()
    try:
        yield session
        if session.in_transaction():
            try:
                await asyncio.shield(session.commit())
            except Exception:
                raise
    except BaseException:
        with suppress(Exception):
            await asyncio.shield(session.rollback())
        raise
    finally:
        with suppress(Exception):
            await asyncio.shield(session.close())
