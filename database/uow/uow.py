"""
Модуль для создания и управления транзакциями
"""

from typing import final

from sqlalchemy.ext.asyncio import async_sessionmaker

from database.repositories import UserRepository

@final
class UnitOfWork:
    """
    Unit of Work pattern for managing database transactions.
    """
    def __init__(
            self,
            async_session_maker: async_sessionmaker
    ):
        self.async_session_maker = async_session_maker

    async def __aenter__(self):
        """
        Create a new session and start a new transaction.
        """
        self.session = self.async_session_maker()
        self.users = UserRepository(self.session) # добавлен репозиторий для работы
        ...

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """
        Commit or rollback the transaction based on the provided exception.
        """
        if exc_type is None:
            await self.commit()
        else:
            await self.rollback()
        await self.session.close()

    async def commit(self):
        """
        Commit the current transaction.
        """
        await self.session.commit()

    async def rollback(self):
        """
        Rollback the current transaction.
        """
        await self.session.rollback()