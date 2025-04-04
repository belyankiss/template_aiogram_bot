from abc import ABC, abstractmethod
from typing import TypeVar, Type, Optional, Sequence

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from database.models import Base, UserModel

T = TypeVar('T', bound=Base)


class AbstractRepository(ABC):
    def __init__(
            self,
            session: async_sessionmaker
    ):
        self.session = session

    @abstractmethod
    async def get_by_id(self, id: int):
        raise NotImplementedError

    @abstractmethod
    async def edit_one(self, id: int, data: dict):
        raise NotImplementedError

    @abstractmethod
    async def add_one(self, obj: T):
        raise NotImplementedError

    @abstractmethod
    async def get_all(self, data: dict):
        raise NotImplementedError


class SQLAlchemyRepository(AbstractRepository):
    model = Type[T]

    async def get_by_id(self, id: int) -> Optional[T]:
        return await self.session.get(self.model, id)

    async def edit_one(self, id: int, data: dict) -> None:
        stmt = update(self.model).filter_by(id=id).values(**data)
        await self.session.execute(stmt)

    async def add_one(self, obj: T):
        self.session.add(obj)

    async def get_all(self, data: dict) -> Sequence[T]:
        stmt = select(self.model).filter_by(**data)
        result = await self.session.scalars(stmt)
        return result.all()

class UserRepository(SQLAlchemyRepository):
    model = UserModel

