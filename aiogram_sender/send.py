import aiofiles
from typing import Union, Optional, Iterable, Any, Type, List

from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, KeyboardButton, BufferedInputFile
from pydantic_core import ValidationError

from aiogram_sender.window_builder import WindowBuilder


class Sender:
    window: WindowBuilder
    def __init__(
            self,
            event: Union[Message, CallbackQuery]
    ):
        self.event = event
        self.photo: Optional[Union[str, bytes]] = None
        self.user_photo: bool = False
        self.sizes: Iterable[int] = (1, )
        self._message_data: Optional[dict[str, Any]] = None

    def add_window(
            self,
            window: Type[WindowBuilder],
            new_buttons: Optional[List[Union[InlineKeyboardButton, KeyboardButton]]] = None
    ) -> None:

        self.window = window()

        self._message_data = self.window.render(self.sizes, new_buttons)

    async def _get_user_photo(self):
        photos = await self.event.bot.get_user_profile_photos(self.event.from_user.id)
        if photos.total_count > 0:
            self.photo = photos.photos[0][0].file_id

    async def _reformat_photo(self):
        try:
            async with aiofiles.open(file=self.photo, mode="rb") as file:
                photo = await file.read()
                self.photo = BufferedInputFile(file=photo, filename="photo")
        except FileNotFoundError:
            return
        except IOError:
            self.photo = None

    async def _check_photo(self):
        if not self._message_data:
            raise ValueError("Window not added")
        if self.user_photo:
            await self._get_user_photo()
        if self.photo:
            await self._reformat_photo()
        self._message_data["photo"] = self.photo

    async def _answer_message(self):
        await self.event.answer(**self._message_data)

    async def _answer_photo(self):
        await self.event.answer_photo(**self._message_data)

    async def _answer(self):
        try:
            await self._answer_photo()
        except ValidationError:
            await self._answer_message()

    async def _edit_text(self):
        await self.event.message.edit_text(**self._message_data)

    async def _edit_caption(self):
        await self.event.message.edit_caption(**self._message_data)

    async def _answer_callback(self, show_alert: bool = False):
        if show_alert:
            await self.event.answer(
                self._message_data.get("text", "Произошла непредвиденная ошибка"),
                show_alert=show_alert)
            return
        await self.event.answer()

    async def _edit(self, show_alert: bool = False):
        await self._answer_callback(show_alert)
        try:
            await self._edit_caption()
        except ValidationError:
            try:
                await self._edit_text()
            except ValidationError:
                self.event = self.event.message
                await self.event.delete()
                await self._answer()

    async def send(self):
        await self._check_photo()
        if isinstance(self.event, Message):
            await self._answer()
        else:
            try:
                await self._edit()
            except TelegramBadRequest:
                pass