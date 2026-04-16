from aiogram.filters.callback_data import CallbackData


class DeviceCallback(CallbackData, prefix="device"):
    action: str
