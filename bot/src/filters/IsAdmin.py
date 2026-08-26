from typing import Union

from aiogram.filters import BaseFilter
from aiogram.types import Message, CallbackQuery


class IsAdmin(BaseFilter):
    async def __call__(
        self, event: Union[Message, CallbackQuery], is_admin: bool
    ) -> bool:
        return is_admin
