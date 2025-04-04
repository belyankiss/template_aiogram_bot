from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from database.databases import _AbstractDatabase
from database.uow.uow import UnitOfWork


class SessionMiddleware(BaseMiddleware):
    """
    Класс для проброса UnitOfWork.
    """
    def __init__(
            self,
            database: _AbstractDatabase
    ) -> None:
        super().__init__()
        self.database = database

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
    ) -> Any:
        """
        Проброс сессии базы данных в хэндлерах!
        :param handler: Тип хэндлера
        :param event: Событие телеграмм
        :param data: Данные для получения в хэндлерах
        :return: Any
        """

        uow = UnitOfWork(self.database.async_session_maker)
        data["uow"] = uow
        return await handler(event, data)  # Обрабатываем хэндлер с сессией
