from typing import Callable, Dict, Any, Awaitable, Optional, List, Union

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery

from aiogram_sender.sender import Send


class WindowMiddleware(BaseMiddleware):
    def __init__(
            self,
            private: bool = False,
            admins: Optional[List[int]] = None
    ):
        super().__init__()
        self._private: bool = private
        self._admins: Optional[List[int]] = admins

    async def __call__(self,
                       handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
                       event: TelegramObject,
                       data: Dict[str, Any],
                       ) -> Any:

        state = data.get("state")

        sender = Send(event, state)

        data["sender"] = sender

        if self._private and _check_chat_type(event):
            return await handler(event, data)



        return await handler(event, data)

def _check_chat_type(event: Union[Message, CallbackQuery]) -> bool:
    return event.chat.type == "private"
