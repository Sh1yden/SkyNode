from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from fluentogram import TranslatorRunner

from bot.src.filters import WeatherCallback


def get_btns_exit_to_hours_menu(locale: TranslatorRunner) -> InlineKeyboardMarkup:
    """Кнопки на выход в почасовое меню."""

    builder = InlineKeyboardBuilder()

    # 🔙 Назад
    builder.row(
        InlineKeyboardButton(
            text=locale.button_weather_now_back(),
            callback_data=WeatherCallback(action="weather_hours").pack(),
        ),
    )

    return builder.as_markup(resize_keyboard=True)
