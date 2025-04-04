from database.models import UserModel
from database.repository import SQLAlchemyRepository


class UserRepository(SQLAlchemyRepository):
    model = UserModel