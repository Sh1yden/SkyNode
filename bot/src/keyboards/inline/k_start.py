from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from fluentogram import TranslatorRunner

from bot.src.filters import WeatherCallback


def get_btns_start(locale: TranslatorRunner) -> InlineKeyboardMarkup:
    """Кнопки снизу сообщения после команды /start."""

    builder = InlineKeyboardBuilder()

    # добавить еще кнопок для других функций
    builder.row(
        InlineKeyboardButton(
            text=locale.button_start_weather(),
            callback_data=WeatherCallback(action="weather_menu").pack(),
        )
    )

    return builder.as_markup(resize_keyboard=True)
