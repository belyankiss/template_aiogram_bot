"""
Модуль для создания и хранения сервисов и работы с базой данных
examples:

class UserService:
    @staticmethod
    async def add_user(uow: UnitOfWork, user: UserModel):
        async with uow:
            existing_user = await uow.users.get_by_filter(dict(user_id=user.user_id))
            if existing_user:
                return
            await uow.users.add_one(user)
            await uow.commit()

"""

__all__ = []