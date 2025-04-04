"""
Модуль для добавления таблиц в базу данных.
"""

from typing import Optional

from sqlalchemy import BigInteger, String, Integer, Float
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeMeta, declarative_base

Base: DeclarativeMeta = declarative_base()

__all__ = [
    "Base",
    "UserModel"
]


class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    username: Mapped[str] = mapped_column(String, default="___")
    balance: Mapped[float] = mapped_column(Float, default=0.0)

    def __init__(self, user_id: int, username: Optional[str] = "___"):
        self.user_id = user_id
        self.username = username