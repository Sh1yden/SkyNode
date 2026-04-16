from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from fluentogram import TranslatorRunner

from bot.src.filters import WeatherCallback
from bot.src.filters import DeviceCallback


def get_btns_device(locale: TranslatorRunner) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    # 📱 Телефон    🖥️💻 Компьютер
    builder.row(
        InlineKeyboardButton(
            text=locale.button_device_is_phone(),
            callback_data=DeviceCallback(action="device_phone").pack(),
        ),
        InlineKeyboardButton(
            text=locale.button_device_is_pc(),
            callback_data=DeviceCallback(action="device_pc").pack(),
        ),
    )

    # 🔙 Назад
    builder.row(
        InlineKeyboardButton(
            text=locale.button_weather_now_back(),
            callback_data=WeatherCallback(action="weather_menu").pack(),
        ),
    )

    return builder.as_markup(resize_keyboard=True)
