from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from database.databases import _AbstractDatabase


class SessionMiddleware(BaseMiddleware):
    """
    Класс для проброса сессии базы данных в хэндлеры.
    """
    def __init__(
            self,
            database: _AbstractDatabase
    ) -> None:
        super().__init__()
        self.database = database
        if not self.database.engine:
            self.database.create_engine()

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
        session = self.database.get_session()
        data["session"] = session  # Передаем сессию в хэндлер
        return await handler(event, data)  # Обрабатываем хэндлер с сессией
