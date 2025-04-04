from abc import ABC, abstractmethod
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from loguru import logger
from sqlalchemy import text
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine
)

from database.models import Base


class _AbstractDatabase(ABC):
    engine = None

    def __init__(self, *args, **kwargs):
        self.engine = None
        self.async_session_maker = None
        self.create_engine()

    @abstractmethod
    def create_engine(self):
        """
        Создание асинхронного экземпляра SQLAlchemy engine
        """
        pass

    @abstractmethod
    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession]:
        """
        Асинхронный контекстный менеджер сессии
        """
        pass

    @abstractmethod
    async def build_db(self):
        """
        Создание базы данных
        """
        pass

    async def shutdown(self):
        """
        Закрытие соединения с БД
        """
        if self.engine:
            logger.info("Закрытие соединения с БД...")
            await self.engine.dispose()
            self.engine = None
            logger.info("Соединение с БД закрыто.")

class PostgresDatabase(_AbstractDatabase):
    def __init__(
            self,
            user: str,
            password: str,
            host: str,
            port: int,
            database: str,

    ):
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.database = database
        super().__init__()

    def create_engine(self):
        if self.engine:
            return
        self.engine = create_async_engine(
            url=f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}",
            echo=False,  # Уменьшает нагрузку на логгер
            pool_size=20,  # Увеличиваем пул соединений для высокой нагрузки
            max_overflow=10,  # Запас соединений, если 20 заняты
            pool_recycle=1800,  # Закрывает соединения, которые простаивают > 30 минут
            pool_pre_ping=True,  # Проверяет соединение перед выдачей из пула
            )
        self.async_session_maker = async_sessionmaker(self.engine, class_=AsyncSession, expire_on_commit=False)

    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession]:
        if self.engine is None:
            logger.warning("Движок БД не был создан! Создаю автоматически...")
            self.create_engine()  # <-- Автоматическое создание при первом вызове
        async with self.async_session_maker() as session:
            yield session

    async def build_db(self, is_delete: bool = False):
        if not self.engine:
            self.create_engine()
        if Base.metadata.tables:
            try:
                async with self.engine.begin() as conn:
                    if is_delete:
                        await conn.execute(text("DROP SCHEMA IF EXISTS public CASCADE;"))
                    await conn.execute(text("CREATE SCHEMA IF NOT EXISTS public;"))
                    await conn.run_sync(Base.metadata.create_all)
                    logger.info("Таблицы успешно созданы/пересозданы.")
            except OperationalError as e:
                logger.critical(f"Ошибка при создании таблиц: {e}")
                await conn.rollback()  # <--- Добавление отката в случае ошибки
                raise SystemExit(1)
        else:
            logger.critical("Вы не добавили таблицы для создания базы данных. Добавьте таблицы в файле models.")
            raise SystemExit(1)

class AioSQLiteDatabase(_AbstractDatabase):
    def __init__(
            self,
            db_path: str,
    ):
        self.db_path = db_path
        super().__init__()



    def create_engine(self):
        if self.engine:
            return
        self.engine = create_async_engine(
            f"sqlite+aiosqlite:///{self.db_path}",
            echo=False,
        )
        self.async_session_maker = async_sessionmaker(self.engine, class_=AsyncSession, expire_on_commit=False)


    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession]:
        if self.engine is None:
            logger.warning("Движок БД не был создан! Создаю автоматически...")
            self.create_engine()  # <-- Автоматическое создание при первом вызове
        async with self.async_session_maker() as session:
            yield session

    async def build_db(self, is_delete: bool = False):
        if not self.engine:
            self.create_engine()
        if Base.metadata.tables:
            try:
                async with self.engine.begin() as conn:
                    if is_delete:
                        await conn.run_sync(Base.metadata.drop_all)
                    await conn.run_sync(Base.metadata.create_all)
                    logger.info("Таблицы успешно созданы.")
            except OperationalError:
                logger.critical("Ошибка при создании таблиц.")
                await conn.rollback()  # <--- Добавление отката в случае ошибки
                raise SystemExit(1)
        else:
            logger.critical("Вы не добавили таблицы для создания базы данных. Добавьте таблицы в файле models.")
            raise SystemExit(1)









