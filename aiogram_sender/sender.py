import logging
from typing import Union, Type, Optional, Self

import aiofiles
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import (Message,
                           CallbackQuery,
                           InlineKeyboardButton,
                           KeyboardButton,
                           InlineKeyboardMarkup,
                           ReplyKeyboardMarkup,
                           BufferedInputFile,
                           UserProfilePhotos)
from pydantic import ValidationError

from aiogram_sender.button import Button, KeyboardConfig
from aiogram_sender.keyboard import Keyboard
from aiogram_sender.window import BaseWindow
from aiogram_sender.exceptions import EmptyTextError


class Send:
    """
    Класс для отправки сообщения в чат с автоматическим определение типа сообщения.
    """

    def __init__(
            self,
            event: Union[Message, CallbackQuery],
            state: FSMContext
    ):
        self.event: Union[Message, CallbackQuery] = event
        self.state: FSMContext = state
        self.text = None
        self.reply_markup: Union[InlineKeyboardMarkup, ReplyKeyboardMarkup, None] = None
        self.keyboard_config: Type[KeyboardConfig] = KeyboardConfig
        self._photo: Optional[str] = None
        self._user_photo: bool = False


    def add_window(
            self,
            interface: Union[Type["BaseWindow"], str],
            photo: Optional[str] = None,
            user_photo: bool = False,
            **kwargs) -> Self:
        """
        Добавление окна для отправки, содержащие текст и кнопки, если они нужны.
        :param interface: Используется подкласс BaseWindow или строковое представление.
        :param photo: Путь к файлу с фото, либо ID телеграм фото
        :param user_photo: Если истина, то будет отправлено сообщение с прикрепленным фото из фото пользователя.
        :param kwargs: Можно использовать для передачи параметров для форматирования строк через .format()
        :return: None
        """

        self._photo = photo
        self._user_photo = user_photo

        if isinstance(interface, type) and issubclass(interface, BaseWindow):
            self.text = interface.message.format(**kwargs)
            buttons = self._create_keyboard(interface)
            self.reply_markup = buttons.create_keyboard()
        else:
            self.text = interface.format(**kwargs)
        return self

    async def send(self, answer_callback: str = None) -> Optional[Message]:
        """
        Метод для отправки сообщения. Так же обрабатывает ошибку коллбэка, если не модифицировано сообщение.
        :param answer_callback: Если передана строка, то будет показана пользователю через show_alert
        :return: Optional[Message]
        """
        self._check_text()
        if isinstance(self.event, Message):
            return await self._send_message()
        else:
            try:
                return await self._send_callback(answer_callback)
            except TelegramBadRequest as error:
                logging.error(f"{error} ошибка в отправке сообщения")
                pass

    def _check_text(self) -> None:
        """
        Проверка на наличие текста для сообщения.
        :return: None
        """
        if not self.text or not self.text.strip():
            raise EmptyTextError("Сообщение не может быть пустым. Используйте метод add_window()")

    async def _send_message(self) -> Message:
        """
        Если объект self.event - Message, то отправляется сообщение. Учитывается так же отправка фото,
         если удовлетворены условия.
        :return: Message
        """
        if self._photo or self._user_photo:
            photo = await self._prepare_photo()
            return await self._answer_photo(photo)
        return await self.event.answer(text=self.text, reply_markup=self.reply_markup)

    async def _prepare_photo(self) -> Union[BufferedInputFile, str]:
        """
        Обработка фотографии.
        :return: Union[BufferedInputFile, str]
        """
        if self._user_photo:
            return await self._get_user_photo()
        if "/" in self._photo:
            return self._photo
        return await self._reformat_photo()

    async def _answer_photo(self, photo: Union[BufferedInputFile, str]) -> Message:
        """
        Отправка сообщения с фото.
        :param photo: Union[BufferedInputFile, str]
        :return: Message
        """
        try:
            return await self.event.answer_photo(caption=self.text, photo=photo, reply_markup=self.reply_markup)
        except ValidationError:
            return await self.event.answer(text=self.text, reply_markup=self.reply_markup)

    async def _get_user_photo(self) -> Optional[str]:
        """
        Получение фотографий пользователя из профиля.
        :return: Optional[str]
        """
        user_photos: UserProfilePhotos = await self.event.bot.get_user_profile_photos(self.event.from_user.id)
        if user_photos.total_count > 0:
            return user_photos.photos[0][0].file_id

    async def _send_callback(self, answer_callback: str) -> Message:
        """
        Работа с CallbackQuery
        :param answer_callback: Сообщение для показа пользователю в режиме show_alert.
        :return: Message
        """
        if answer_callback:
            return await self.event.answer(text=answer_callback, show_alert=True)
        else:
            await self.event.answer()

        if self.event.message.caption:
            return await self.event.message.edit_caption(caption=self.text, reply_markup=self.reply_markup)
        return await self.event.message.edit_text(text=self.text, reply_markup=self.reply_markup)

    async def _reformat_photo(self) -> BufferedInputFile:
        """
        Упаковка фотографии, если передан путь к ней.

        :exception: FileNotFoundError

        :return: BufferedInputFile

        """
        try:
            async with aiofiles.open(self._photo, mode="rb") as file:
                photo = await file.read()
                return BufferedInputFile(photo, filename="photo")
        except FileNotFoundError:
            logging.error(f"Файл {self._photo} не найден")
            raise


    def _create_keyboard(self,
            interface: Type["BaseWindow"],
    ) -> Keyboard:
        """
        Создание клавиатуры.
        :param interface: Используется подкласс BaseWindow или строковое представление.
        :return: Keyboard
        """

        window = interface()
        buttons = window.build()
        list_buttons = []
        for button in buttons:
            if isinstance(button, (InlineKeyboardButton, KeyboardButton)):
                list_buttons.append(button)
            elif isinstance(button, Button):
                if button.data:
                    return Keyboard(button.create_inline_buttons(
                        self.keyboard_config()
                    ),
                    self.keyboard_config.sizes)
                list_buttons.append(button.create_button())
        return Keyboard(list_buttons, self.keyboard_config.sizes)
