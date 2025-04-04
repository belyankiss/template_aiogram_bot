from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from database.repository import UserRepository


class UnitOfWork:
    def __init__(
            self,
            async_session_maker: async_sessionmaker
    ):
        self.async_session_maker = async_session_maker

    async def __aenter__(self):
        self.session = self.async_session_maker()
        self.users = UserRepository(self.session)

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            await self.commit()
        else:
            await self.rollback()
        await self.session.close()

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()