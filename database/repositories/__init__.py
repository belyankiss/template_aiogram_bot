"""
Модуль хранения и создания репозиториев для работы с базой данных


Пример:

class UserRepository(SQLAlchemyRepository):
    model = UserModel
"""
from user_repository import UserRepository


__all__ = [
    "UserRepository"
]