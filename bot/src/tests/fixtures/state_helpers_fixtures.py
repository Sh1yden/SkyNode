"""Фикстуры для тестирования state_helpers.py"""

import pytest
from unittest.mock import AsyncMock

from aiogram.fsm.context import FSMContext


@pytest.fixture
def mock_state():
    """Фикстура для создания мок-объекта FSMContext"""
    state = AsyncMock(spec=FSMContext)
    return state


@pytest.fixture
def mock_state_with_phone_location(mock_state):
    """Состояние ожидания локации с телефона"""
    mock_state.get_state = AsyncMock(
        return_value="LocationState:waiting_for_city_phone"
    )
    return mock_state


@pytest.fixture
def mock_state_with_pc_location(mock_state):
    """Состояние ожидания локации с ПК"""
    mock_state.get_state = AsyncMock(return_value="LocationState:waiting_for_city_pc")
    return mock_state


@pytest.fixture
def mock_state_with_other_state(mock_state):
    """Состояние не связанное с локацией"""
    mock_state.get_state = AsyncMock(return_value="SomeOtherState:some_state")
    return mock_state


@pytest.fixture
def mock_state_with_none_state(mock_state):
    """Отсутствие состояния (None)"""
    mock_state.get_state = AsyncMock(return_value=None)
    return mock_state
