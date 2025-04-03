from contextlib import asynccontextmanager
from typing import Literal, AsyncGenerator

from loguru import logger
from sqlalchemy import text
from sqlalchemy.exc import OperationalError

from database.models import Base

try:
    from sqlalchemy.ext.asyncio import (
        AsyncEngine,
        AsyncSession,
        async_sessionmaker,
        create_async_engine
    )
    from sqlalchemy.pool import Pool
except ImportError:
    logger.critical("Установите пакет 'sqlalchemy' для работы с базой данных!")
    raise SystemExit(1)


from settings import settings


class Database:
    def __init__(
            self,
            db_type: Literal["aiosqlite", "postgres"],
            create_database: bool = False
    ):
        self.db_type = db_type
        self.engine = None
        self._create_database: bool = create_database
        self.Session = None

    def create_engine(self):
        """
        Создаем асинхронный engine с пулом соединений.
        """
        if self.db_type == "postgres":
            self.engine = create_async_engine(
                settings.postgres_url,
                pool_size=10,
                max_overflow=5,
                echo=False
            )
        else:
            self.engine = create_async_engine(
                settings.aiosqlite_url,
                echo=False
            )
        # Создание sessionmaker для асинхронной работы
        self.Session = async_sessionmaker(self.engine, class_=AsyncSession, expire_on_commit=False)

    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator:
        """
        Получаем сессию из пула.
        :return: AsyncSession
        """
        async with self.Session() as session:
            yield session

    async def create_tables(
            self,
            is_delete: bool = False
    ):
        if self._create_database:
            if not self.engine:
                self.create_engine()
            try:
                async with self.engine.begin() as conn:
                    # Полностью удаляем все таблицы
                    if is_delete:
                        await conn.execute(text("DROP SCHEMA IF EXISTS public CASCADE;"))
                    await conn.execute(text("CREATE SCHEMA IF NOT EXISTS public;"))
                    # Пересоздаём все таблицы
                    await conn.run_sync(Base.metadata.create_all)
                    logger.info("Таблицы успешно созданы/пересозданы.")
            except OperationalError:
                    try:
                        # Попытка создания новой базы данных
                        async with self.engine.begin() as conn:
                            if is_delete:
                                await conn.run_sync(Base.metadata.drop_all)
                            await conn.run_sync(Base.metadata.create_all)
                        logger.info(f"База данных {settings.NAME_DATABASE} успешно пересоздана.")
                    except Exception as ex:
                        logger.error(f"Не удалось пересоздать базу данных: {ex}")

    def __repr__(self):
        return f"Тип базы данных: {self.db_type}"


