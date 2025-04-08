from typing import Optional, List, Union, Iterable

from aiogram.types import InlineKeyboardButton, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from pydantic import BaseModel


class Keyboard(BaseModel):
    @classmethod
    def create_list(cls) -> Optional[List[Union[InlineKeyboardButton, KeyboardButton]]]:
        return [v.default for v in cls.model_fields.values() if v.default is not None]

    @classmethod
    def create_reply_markup(
            cls,
            sizes: Iterable[int],
            buttons: Optional[List[Union[InlineKeyboardButton, KeyboardButton]]] = None
    ):
        if not buttons:
            return None
        if isinstance(buttons[0], InlineKeyboardButton):
            builder = InlineKeyboardBuilder()
            button_type = InlineKeyboardButton
        else:
            builder = ReplyKeyboardBuilder()
            button_type = KeyboardButton
        for button in buttons:
            if isinstance(button, button_type):
                builder.add(button)

        return builder.adjust(*sizes).as_markup(resize_keyboard=True)