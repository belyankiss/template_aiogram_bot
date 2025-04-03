from typing import Optional, Union

from aiogram.types import InlineKeyboardButton, KeyboardButton

from aiogram_sender.button import Button


class BaseWindow:
    """
    Класс для создания окон в телеграм.
    :param message: Текст сообщения
    :param keyboard: Optional[Union[Button, InlineKeyboardButton, KeyboardButton]] - Не обязательный параметр. Сюда передаем кнопку.
    """
    message: str
    keyboard: Optional[Union[Button, InlineKeyboardButton, KeyboardButton]] = None

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

    @classmethod
    def build(cls):
        buttons = []
        for value in cls.__dict__.values():
            if isinstance(value, (Button, InlineKeyboardButton, KeyboardButton)):
                buttons.append(value)
        return buttons



class Doo(BaseWindow):
    message = "Hello"
    fsfs = InlineKeyboardButton(text="sdfs", callback_data="/start")
    hi = Button(InlineKeyboardButton, text="hello", callback_data="hello", data=True)
    gete = Button(InlineKeyboardButton, text="sds", url="https://hello.world")



