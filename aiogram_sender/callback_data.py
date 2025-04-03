from typing import Optional, Union

from aiogram.filters.callback_data import CallbackData


class BaseCallback(CallbackData, prefix="..."):
    value: Optional[Union[int, float, str]] = None