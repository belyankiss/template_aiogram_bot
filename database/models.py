from typing import Optional

from sqlalchemy import BigInteger, String, Integer
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeMeta, declarative_base

Base: DeclarativeMeta = declarative_base()


class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger)
    username: Mapped[str] = mapped_column(String, default="___")

    def __init__(self, user_id: int, username: Optional[str] = "___"):
        self.user_id = user_id
        self.username = username