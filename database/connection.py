from typing import Literal

from loguru import logger
from sqlalchemy import text

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
    def __init__(self, db_type: Literal["aiosqlite", "postgres"]):
        self.db_type = db_type
        self.engine = None
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

    async def get_session(self) -> AsyncSession:
        """
        Получаем сессию из пула.
        :return: AsyncSession
        """
        return self.Session()

    def __repr__(self):
        return f"Тип базы данных: {self.db_type}"

async def create_database():
    database = Database("aiosqlite")
    database.create_engine()
    a_session = await database.get_session()
    async with a_session as session:
        # Пример: Создание таблицы
        async with session.begin():
            # Создаем таблицу
            result = await session.execute(text("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT
                )
            """))
            print(result)

        logger.info("Таблица успешно создана!")
