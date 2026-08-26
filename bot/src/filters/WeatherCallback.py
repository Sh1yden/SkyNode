from aiogram.filters.callback_data import CallbackData


class WeatherCallback(CallbackData, prefix="weather"):
    action: str
