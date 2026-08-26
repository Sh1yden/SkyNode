from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from fluentogram import TranslatorRunner

from bot.src.filters import MenuCallback


def get_btns_admin_menu(
    locale: TranslatorRunner, is_admin: bool = False
) -> InlineKeyboardMarkup:
    """Кнопки снизу сообщения после команды /admin_menu."""

    builder = InlineKeyboardBuilder()

    # 🔙 Назад
    builder.row(
        InlineKeyboardButton(
            text=locale.button_weather_menu_back(),
            callback_data=MenuCallback(action="main_menu").pack(),
        ),
    )

    return builder.as_markup(resize_keyboard=True)
