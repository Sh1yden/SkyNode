from aiogram.filters.callback_data import CallbackData


class HelpCallback(CallbackData, prefix="help"):
    action: str
