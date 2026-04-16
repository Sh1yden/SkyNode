from aiogram.fsm.state import State, StatesGroup


class LocationState(StatesGroup):
    waiting_for_city_phone = State()  # состояние ожидания ввода города с телефона
    waiting_for_city_pc = State()  # состояние ожидания ввода города с пк
