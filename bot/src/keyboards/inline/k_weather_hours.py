from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from fluentogram import TranslatorRunner

from bot.src.filters import WeatherCallback


def get_btns_weather_hours(locale: TranslatorRunner) -> InlineKeyboardMarkup:
    """Кнопки снизу сообщения после команды /weatherHours."""

    builder = InlineKeyboardBuilder()

    # 🕗 8 часов     🕛 12 часов
    builder.row(
        InlineKeyboardButton(
            text=locale.button_weather_hours_8(),
            callback_data=WeatherCallback(action="weather_hours_8").pack(),
        ),
        InlineKeyboardButton(
            text=locale.button_weather_hours_12(),
            callback_data=WeatherCallback(action="weather_hours_12").pack(),
        ),
    )

    # ☀️ 24 часа 🌙
    builder.row(
        InlineKeyboardButton(
            text=locale.button_weather_hours_24(),
            callback_data=WeatherCallback(action="weather_hours_24").pack(),
        )
    )

    # 🔙 Назад
    builder.row(
        InlineKeyboardButton(
            text=locale.button_weather_now_back(),
            callback_data=WeatherCallback(action="weather_menu").pack(),
        ),
    )

    return builder.as_markup(resize_keyboard=True)
