from database.models import UserModel
from database.uow import UnitOfWork


class UserService:
    async def add_user(self, uow: UnitOfWork, user: UserModel):
        async with uow:
            await uow.users.add_one(user)
            await uow.commit()