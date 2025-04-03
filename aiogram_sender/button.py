"""
Модуль для создания кнопок и клавиатур.
"""
from dataclasses import dataclass
from typing import Union, Type, Optional, List, Iterable

from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, KeyboardButton

from aiogram_sender.callback_data import BaseCallback
from aiogram_sender.exceptions import UrlError, ButtonError, CallbackDataError, DataError


@dataclass
class KeyboardConfig:
    """
    Класс для составления клавиатуры.
    """
    data: Iterable[Union[int, float, str]] = None
    in_text: bool = False
    in_callback: bool = False
    start: bool = False
    sep: str = "-"
    include_back_button: bool = False
    back_button_text: str = "Назад"
    back_button_callback: str = "back"
    sizes: Iterable[int] = (1,)

class Button:
    """
    Класс для создания Reply и Inline кнопок.

    :param type_button: Используется типизация кнопки InlineKeyboardButton или KeyboardButton
    :param text: Строковое значение. Для названия кнопки.
    :param callback_data: Можно использовать либо CallbackData, либо BaseCallback. Обязательно должен быть атрибут
                          value! Так же принимает строковые значения.
    :param url: Ссылка для прикрепления к инлайн кнопке. Обязательно должна начинаться с https://
    :param data: Булево. Если в дальнейшем будут передаваться данные для прикрепления к кнопке.
                         Если истина, то будет вызван метод create_inline_buttons, иначе create_button
    :param prefix: Добавление префикса в кнопке
    :param postfix: Добавление постфикса в кнопке
    """
    def __init__(
            self,
            type_button: Union[Type["InlineKeyboardButton"], Type["KeyboardButton"]],
            text: str,
            callback_data: Optional[Union[str, BaseCallback]] = None,
            url: Optional[str] = None,
            data: bool = False,
            prefix: Optional[str] = None,
            postfix: Optional[str] = None
    ):

        self.type_button: Union[Type["InlineKeyboardButton"], Type["KeyboardButton"]] = type_button
        self.text: str = text
        self.callback_data: Optional[Union[str, CallbackData]] = callback_data
        self.url: Optional[str] = url
        self.data: bool = data
        self.prefix: Optional[str] = prefix
        self.postfix: Optional[str] = postfix


    def create_button(self) -> Union[InlineKeyboardButton, KeyboardButton, None]:
        """
        Метод для создания кнопки.
        :return: Union[InlineKeyboardButton, KeyboardButton, None]
        """
        if issubclass(self.type_button, KeyboardButton):
            return self._create_keyboard_button()
        elif issubclass(self.type_button, InlineKeyboardButton):
            return self._create_inline_button()
        return None

    def create_inline_buttons(
            self,
            config: KeyboardConfig
    ) -> List[InlineKeyboardButton]:
        """
        Метод для создания списка инлайн-кнопок! Так же добавляется кнопка 'Назад', если data пустой список!

        :param config: Класс KeyboardConfig
        :return: List[InlineKeyboardButton]
        """

        if not config.data:
            return [InlineKeyboardButton(text=config.back_button_text, callback_data=config.back_button_callback)]

        buttons = []
        if config.data and not self.data:
            raise DataError("Вы забыли поставить в инлайн кнопке флаг data в положение True.")
        for item in config.data:
            if config.in_text:
                text = f"{item} {config.sep} {self.text}" if config.start else f"{self.text} {config.sep} {item}"
            else:
                text = self.text

            if config.in_callback:
                callback_data = self._create_callback_data(item)
            else:
                callback_data = self.callback_data

            buttons.append(
                InlineKeyboardButton(
                    text=text,
                    callback_data=callback_data
                )
            )
        if config.include_back_button:
            buttons.append(InlineKeyboardButton(text=config.back_button_text, callback_data=config.back_button_callback))
        return buttons

    def _check_url(self) -> None:
        """
        Проверка на корректность введенного url.
        :return: None
        """
        if self.url and not self.url.startswith("https://"):
            raise UrlError("Неверный формат ссылки! Ссылка должна начинаться с https://")


    def _create_inline_button(self) -> InlineKeyboardButton:
        """
        Метод создания инлайн-кнопки
        :return: InlineKeyboardButton
        """
        if not self.callback_data and not self.url:
            raise ButtonError("Не передан один из атрибутов для создания кнопки: url или callback_data!")

        self._check_url()

        if self.callback_data:
            return InlineKeyboardButton(
                text=self._format_text(),
                callback_data=self.callback_data
            )
        return InlineKeyboardButton(
            text=self._format_text(),
            url=self.url
        )

    def _format_text(self) -> str:
        """
        Метод для создания текста кнопки с учетом префикса и постфикса.
        :return: str
        """
        return f"{self.prefix or ''} {self.text} {self.postfix or ''}".strip()

    def _create_keyboard_button(self) -> KeyboardButton:
        """
        Метод создания обычной кнопки.
        :return: KeyboardButton
        """
        return KeyboardButton(text=self._format_text())

    def _create_callback_data(self, item: Union[int, float, str]) -> str:
        """
        Метод для модификации callback_data при перечислении переданных данных!
        :param item: Union[int, float, str]
        :return: str
        """
        if self.callback_data is None:
            raise CallbackDataError("Значение callback_data не может быть None")

        if isinstance(self.callback_data, BaseCallback):
            callback_data = self.callback_data.model_copy(update={"value": item},
                                                          deep=True)
            callback_data = callback_data.pack().rstrip(":")

        else:
            callback_data = f"{self.callback_data}:{item}"
        return callback_data

    def __repr__(self):
        return f"{self.type_button.__name__}, text={self.text}, callback_data={self.callback_data}, url={self.url}"


