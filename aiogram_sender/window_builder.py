from typing import Optional, Iterable, Union, List

from aiogram.types import InlineKeyboardButton, KeyboardButton
from pydantic import BaseModel, Field


from aiogram_sender.keyboard import Keyboard


class WindowBuilder(BaseModel):
    text: Optional[str] = None
    keyboard: Optional[Keyboard] = Field(default=None)

    def render(
            self,
            sizes: Iterable[int],
            new_keyboard: Optional[List[Union[InlineKeyboardButton, KeyboardButton]]] = None
    ):

        if not new_keyboard and self.keyboard is not None:
            buttons = self.keyboard.create_list()
        else:
            buttons = new_keyboard
            self.keyboard = Keyboard()

        return {
            "text": self.text,
            "caption": self.text,
            "reply_markup": self.keyboard.create_reply_markup(sizes, buttons)
        }

