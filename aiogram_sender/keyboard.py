from typing import Optional, List, Union, Iterable

from aiogram.types import InlineKeyboardButton, KeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

from aiogram_sender.exceptions import ButtonError





class Keyboard:
    """
    Класс создания клавиатуры!

    :param buttons: Список кнопок InlineKeyboardButton или KeyboardButton
    :param sizes: Размер клавиатуры. Итерируемый объект целых чисел. Значение по умолчанию - (1,)
    """
    def __init__(
            self,
            buttons: Optional[List[Union[InlineKeyboardButton, KeyboardButton]]],
            sizes: Iterable[int] = (1,)
    ):
        self.buttons: Optional[List[Union[InlineKeyboardButton, KeyboardButton]]] = buttons
        self.sizes: Iterable[int] = sizes
        self._reply_markup = None

    def create_keyboard(self) -> Union[InlineKeyboardMarkup, ReplyKeyboardMarkup, None]:
        """
        Основной метод создания клавиатуры.
        :return: Union[InlineKeyboardMarkup, ReplyKeyboardMarkup, None]
        """
        if not self.buttons:
            return None
        if not all(isinstance(btn, type(self.buttons[0])) for btn in self.buttons):
            raise ButtonError("Все кнопки должны быть одного типа (InlineKeyboardButton или KeyboardButton)")
        if isinstance(self.buttons[0], InlineKeyboardButton):
            b = InlineKeyboardBuilder()
        else:
            b = ReplyKeyboardBuilder()
        b.add(*self.buttons)
        self._reply_markup = b.adjust(*self.sizes).as_markup(resize_keyboard=True)
        return self._reply_markup

    def __repr__(self):
        return f"{self._reply_markup}"
