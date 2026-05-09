from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from fluentogram import TranslatorRunner

from bot.src.filters import WeatherCallback, AdminCallback


def get_btns_start(
    locale: TranslatorRunner, is_admin: bool = False
) -> InlineKeyboardMarkup:
    """Кнопки снизу сообщения после команды /start."""

    builder = InlineKeyboardBuilder()

    # ⛅️ Погода
    builder.row(
        InlineKeyboardButton(
            text=locale.button_start_weather(),
            callback_data=WeatherCallback(action="weather_menu").pack(),
        )
    )

    # 🔐 Админ панель
    if is_admin:
        builder.row(
            InlineKeyboardButton(
                text=locale.button_admin_menu(),
                callback_data=AdminCallback(action="admin_menu").pack(),
            )
        )

    return builder.as_markup(resize_keyboard=True)
