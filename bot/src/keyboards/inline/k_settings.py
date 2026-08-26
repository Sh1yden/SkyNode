from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from fluentogram import TranslatorRunner

from bot.src.filters import WeatherCallback


def get_btns_settings(locale: TranslatorRunner) -> InlineKeyboardMarkup:
    """Кнопки снизу сообщения после команды /start."""

    builder = InlineKeyboardBuilder()

    # 🌐 Язык
    builder.row(
        InlineKeyboardButton(
            text=locale.message_settings_change_lang(),
            callback_data=WeatherCallback(action="").pack(),
        )
    )

    # 📍 Изменить геопозицию
    builder.row(
        InlineKeyboardButton(
            text=locale.message_settings_location(),
            callback_data=WeatherCallback(action="change_weather_location").pack(),
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
