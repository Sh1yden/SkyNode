"""Unit тестирование асинхронного модуля state_helpers.py."""

import pytest
from unittest.mock import AsyncMock

from bot.src.utils import (
    clear_state,
    is_waiting_for_location,
    get_current_state,
    set_state_data,
)


# ============= clear_state =============


class TestClearState:
    """Тесты для функции clear_state"""

    @pytest.mark.asyncio
    async def test_success_with_valid_state(self, mock_state):
        """Успешная очистка состояния"""
        mock_state.clear = AsyncMock(return_value=None)

        await clear_state(mock_state)

        mock_state.clear.assert_called_once()

    @pytest.mark.asyncio
    async def test_exception_handling(self, mock_state):
        """Обработка исключения при очистке состояния"""
        mock_state.clear = AsyncMock(side_effect=Exception("Clear error"))

        # Функция не должна выбрасывать исключение
        await clear_state(mock_state)

        mock_state.clear.assert_called_once()

    @pytest.mark.asyncio
    async def test_multiple_calls(self, mock_state):
        """Множественные вызовы очистки"""
        mock_state.clear = AsyncMock(return_value=None)

        await clear_state(mock_state)
        await clear_state(mock_state)
        await clear_state(mock_state)

        assert mock_state.clear.call_count == 3

    @pytest.mark.asyncio
    async def test_with_database_error(self, mock_state):
        """Обработка ошибки базы данных"""
        mock_state.clear = AsyncMock(side_effect=RuntimeError("Database error"))

        await clear_state(mock_state)

        mock_state.clear.assert_called_once()

    @pytest.mark.asyncio
    async def test_with_timeout_error(self, mock_state):
        """Обработка ошибки таймаута"""
        mock_state.clear = AsyncMock(side_effect=TimeoutError("Timeout"))

        await clear_state(mock_state)

        mock_state.clear.assert_called_once()


# ============= is_waiting_for_location =============


class TestIsWaitingForLocation:
    """Тесты для функции is_waiting_for_location"""

    @pytest.mark.asyncio
    async def test_waiting_for_city_phone(self, mock_state_with_phone_location):
        """Ожидание локации с телефона возвращает True"""
        result = await is_waiting_for_location(mock_state_with_phone_location)

        assert result is True
        mock_state_with_phone_location.get_state.assert_called_once()

    @pytest.mark.asyncio
    async def test_waiting_for_city_pc(self, mock_state_with_pc_location):
        """Ожидание локации с ПК возвращает True"""
        result = await is_waiting_for_location(mock_state_with_pc_location)

        assert result is True
        mock_state_with_pc_location.get_state.assert_called_once()

    @pytest.mark.asyncio
    async def test_not_waiting_for_location(self, mock_state_with_other_state):
        """Другое состояние возвращает False"""
        result = await is_waiting_for_location(mock_state_with_other_state)

        assert result is False
        mock_state_with_other_state.get_state.assert_called_once()

    @pytest.mark.asyncio
    async def test_no_state_returns_false(self, mock_state_with_none_state):
        """Отсутствие состояния возвращает False"""
        result = await is_waiting_for_location(mock_state_with_none_state)

        assert result is False
        mock_state_with_none_state.get_state.assert_called_once()

    @pytest.mark.asyncio
    async def test_exception_handling_returns_false(self, mock_state):
        """Исключение при проверке возвращает False"""
        mock_state.get_state = AsyncMock(side_effect=Exception("State error"))

        result = await is_waiting_for_location(mock_state)

        assert result is False
        mock_state.get_state.assert_called_once()

    @pytest.mark.asyncio
    async def test_empty_string_state_returns_false(self, mock_state):
        """Пустая строка как состояние возвращает False"""
        mock_state.get_state = AsyncMock(return_value="")

        result = await is_waiting_for_location(mock_state)

        assert result is False

    @pytest.mark.asyncio
    async def test_whitespace_state_returns_false(self, mock_state):
        """Пробелы как состояние возвращает False"""
        mock_state.get_state = AsyncMock(return_value="   ")

        result = await is_waiting_for_location(mock_state)

        assert result is False

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "state_name",
        [
            "LocationState:waiting_for_city_phone",
            "LocationState:waiting_for_city_pc",
        ],
    )
    async def test_all_waiting_states(self, mock_state, state_name):
        """Все состояния ожидания локации"""
        mock_state.get_state = AsyncMock(return_value=state_name)

        result = await is_waiting_for_location(mock_state)

        assert result is True

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "invalid_state",
        [
            "WeatherState:waiting",
            "UserState:active",
            "LocationState:completed",
            "LocationState:cancelled",
            "",
            None,
        ],
    )
    async def test_various_invalid_states(self, mock_state, invalid_state):
        """Различные невалидные состояния возвращают False"""
        mock_state.get_state = AsyncMock(return_value=invalid_state)

        result = await is_waiting_for_location(mock_state)

        assert result is False

    @pytest.mark.asyncio
    async def test_case_sensitive_state_check(self, mock_state):
        """Проверка чувствительности к регистру"""
        mock_state.get_state = AsyncMock(
            return_value="locationstate:waiting_for_city_phone"
        )

        result = await is_waiting_for_location(mock_state)

        assert result is False

    @pytest.mark.asyncio
    async def test_partial_state_match_returns_false(self, mock_state):
        """Частичное совпадение состояния возвращает False"""
        mock_state.get_state = AsyncMock(return_value="waiting_for_city_phone")

        result = await is_waiting_for_location(mock_state)

        assert result is False

    @pytest.mark.asyncio
    async def test_state_with_extra_characters(self, mock_state):
        """Состояние с дополнительными символами"""
        mock_state.get_state = AsyncMock(
            return_value="LocationState:waiting_for_city_phone_extra"
        )

        result = await is_waiting_for_location(mock_state)

        assert result is False


# ============= get_current_state =============


class TestGetCurrentState:
    """Тесты для функции get_current_state"""

    @pytest.mark.asyncio
    async def test_success_with_valid_state(self, mock_state_with_phone_location):
        """Успешное получение валидного состояния"""
        expected_state = "LocationState:waiting_for_city_phone"

        result = await get_current_state(mock_state_with_phone_location)

        assert result == expected_state
        mock_state_with_phone_location.get_state.assert_called_once()

    @pytest.mark.asyncio
    async def test_none_state_returns_none(self, mock_state_with_none_state):
        """Отсутствие состояния возвращает None"""
        result = await get_current_state(mock_state_with_none_state)

        assert result is None
        mock_state_with_none_state.get_state.assert_called_once()

    @pytest.mark.asyncio
    async def test_exception_handling_returns_none(self, mock_state):
        """Исключение при получении состояния возвращает None"""
        mock_state.get_state = AsyncMock(side_effect=Exception("Get state error"))

        result = await get_current_state(mock_state)

        assert result is None
        mock_state.get_state.assert_called_once()

    @pytest.mark.asyncio
    async def test_empty_string_state(self, mock_state):
        """Пустая строка как состояние"""
        mock_state.get_state = AsyncMock(return_value="")

        result = await get_current_state(mock_state)

        assert result == ""

    @pytest.mark.asyncio
    async def test_very_long_state_name(self, mock_state):
        """Очень длинное имя состояния"""
        long_state = "A" * 1000
        mock_state.get_state = AsyncMock(return_value=long_state)

        result = await get_current_state(mock_state)

        assert result == long_state

    @pytest.mark.asyncio
    async def test_state_with_special_characters(self, mock_state):
        """Состояние со спецсимволами"""
        special_state = "State:with-special_chars@123"
        mock_state.get_state = AsyncMock(return_value=special_state)

        result = await get_current_state(mock_state)

        assert result == special_state

    @pytest.mark.asyncio
    async def test_unicode_state_name(self, mock_state):
        """Unicode в имени состояния"""
        unicode_state = "Состояние:ожидание_测试"
        mock_state.get_state = AsyncMock(return_value=unicode_state)

        result = await get_current_state(mock_state)

        assert result == unicode_state

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "state_name",
        [
            "LocationState:waiting_for_city_phone",
            "LocationState:waiting_for_city_pc",
            "WeatherState:active",
            "UserState:registered",
            "",
            None,
        ],
    )
    async def test_various_state_names(self, mock_state, state_name):
        """Различные имена состояний"""
        mock_state.get_state = AsyncMock(return_value=state_name)

        result = await get_current_state(mock_state)

        assert result == state_name

    @pytest.mark.asyncio
    async def test_multiple_calls_same_state(self, mock_state):
        """Множественные вызовы для одного состояния"""
        expected_state = "LocationState:waiting_for_city_phone"
        mock_state.get_state = AsyncMock(return_value=expected_state)

        result1 = await get_current_state(mock_state)
        result2 = await get_current_state(mock_state)
        result3 = await get_current_state(mock_state)

        assert result1 == result2 == result3 == expected_state
        assert mock_state.get_state.call_count == 3

    @pytest.mark.asyncio
    async def test_runtime_error_handling(self, mock_state):
        """Обработка RuntimeError"""
        mock_state.get_state = AsyncMock(side_effect=RuntimeError("Runtime error"))

        result = await get_current_state(mock_state)

        assert result is None

    @pytest.mark.asyncio
    async def test_timeout_error_handling(self, mock_state):
        """Обработка TimeoutError"""
        mock_state.get_state = AsyncMock(side_effect=TimeoutError("Timeout"))

        result = await get_current_state(mock_state)

        assert result is None


# ============= set_state_data =============


class TestSetStateData:
    """Тесты для функции set_state_data"""

    @pytest.mark.asyncio
    async def test_success_with_valid_data(self, mock_state):
        """Успешное сохранение валидных данных"""
        test_data = {"city": "Moscow", "latitude": 55.75, "longitude": 37.61}
        mock_state.update_data = AsyncMock(return_value=None)

        await set_state_data(mock_state, test_data)

        mock_state.update_data.assert_called_once_with(**test_data)

    @pytest.mark.asyncio
    async def test_empty_dict(self, mock_state):
        """Сохранение пустого словаря"""
        test_data = {}
        mock_state.update_data = AsyncMock(return_value=None)

        await set_state_data(mock_state, test_data)

        mock_state.update_data.assert_called_once_with(**test_data)

    @pytest.mark.asyncio
    async def test_complex_nested_data(self, mock_state):
        """Сохранение сложных вложенных данных"""
        test_data = {
            "user_id": 123456,
            "location": {"city": "Moscow", "coords": [55.75, 37.61]},
            "settings": {"language": "ru", "notifications": True},
            "metadata": {"created_at": "2025-01-16", "version": 1},
        }
        mock_state.update_data = AsyncMock(return_value=None)

        await set_state_data(mock_state, test_data)

        mock_state.update_data.assert_called_once_with(**test_data)

    @pytest.mark.asyncio
    async def test_exception_handling(self, mock_state):
        """Обработка исключения при сохранении данных"""
        test_data = {"city": "Moscow"}
        mock_state.update_data = AsyncMock(side_effect=Exception("Update data error"))

        # Функция не должна выбрасывать исключение
        await set_state_data(mock_state, test_data)

        mock_state.update_data.assert_called_once_with(**test_data)

    @pytest.mark.asyncio
    async def test_none_values_in_data(self, mock_state):
        """None значения в данных"""
        data_with_none = {"city": None, "latitude": None, "longitude": None}
        mock_state.update_data = AsyncMock(return_value=None)

        await set_state_data(mock_state, data_with_none)

        mock_state.update_data.assert_called_once_with(**data_with_none)

    @pytest.mark.asyncio
    async def test_unicode_in_data(self, mock_state):
        """Unicode символы в данных"""
        unicode_data = {
            "city": "Москва",
            "description": "Тестовое описание 测试 🌍",
            "emoji": "🏙️",
        }
        mock_state.update_data = AsyncMock(return_value=None)

        await set_state_data(mock_state, unicode_data)

        mock_state.update_data.assert_called_once_with(**unicode_data)

    @pytest.mark.asyncio
    async def test_boolean_values(self, mock_state):
        """Boolean значения в данных"""
        bool_data = {
            "is_active": True,
            "is_verified": False,
            "has_location": True,
        }
        mock_state.update_data = AsyncMock(return_value=None)

        await set_state_data(mock_state, bool_data)

        mock_state.update_data.assert_called_once_with(**bool_data)

    @pytest.mark.asyncio
    async def test_numeric_values(self, mock_state):
        """Числовые значения в данных"""
        numeric_data = {
            "user_id": 123456,
            "latitude": 55.7558,
            "longitude": 37.6173,
            "temperature": -5.5,
            "count": 0,
        }
        mock_state.update_data = AsyncMock(return_value=None)

        await set_state_data(mock_state, numeric_data)

        mock_state.update_data.assert_called_once_with(**numeric_data)

    @pytest.mark.asyncio
    async def test_list_values(self, mock_state):
        """Списки в данных"""
        list_data = {
            "cities": ["Moscow", "Petersburg", "Kursk"],
            "coordinates": [55.75, 37.61],
            "empty_list": [],
        }
        mock_state.update_data = AsyncMock(return_value=None)

        await set_state_data(mock_state, list_data)

        mock_state.update_data.assert_called_once_with(**list_data)

    @pytest.mark.asyncio
    async def test_mixed_types_data(self, mock_state):
        """Смешанные типы данных"""
        mixed_data = {
            "string": "Moscow",
            "integer": 42,
            "float": 3.14,
            "boolean": True,
            "none": None,
            "list": [1, 2, 3],
            "dict": {"key": "value"},
        }
        mock_state.update_data = AsyncMock(return_value=None)

        await set_state_data(mock_state, mixed_data)

        mock_state.update_data.assert_called_once_with(**mixed_data)

    @pytest.mark.asyncio
    async def test_special_characters_in_values(self, mock_state):
        """Спецсимволы в значениях"""
        special_data = {
            "city": "New-York@123",
            "description": "Test!@#$%^&*()",
            "path": "/usr/local/bin",
        }
        mock_state.update_data = AsyncMock(return_value=None)

        await set_state_data(mock_state, special_data)

        mock_state.update_data.assert_called_once_with(**special_data)

    @pytest.mark.asyncio
    async def test_very_long_string_value(self, mock_state):
        """Очень длинная строка в значении"""
        long_data = {"description": "A" * 10000}
        mock_state.update_data = AsyncMock(return_value=None)

        await set_state_data(mock_state, long_data)

        mock_state.update_data.assert_called_once_with(**long_data)

    @pytest.mark.asyncio
    async def test_multiple_calls_with_different_data(self, mock_state):
        """Множественные вызовы с разными данными"""
        mock_state.update_data = AsyncMock(return_value=None)

        await set_state_data(mock_state, {"city": "Moscow"})
        await set_state_data(mock_state, {"latitude": 55.75})
        await set_state_data(mock_state, {"longitude": 37.61})

        assert mock_state.update_data.call_count == 3

    @pytest.mark.asyncio
    async def test_runtime_error_handling(self, mock_state):
        """Обработка RuntimeError"""
        test_data = {"city": "Moscow"}
        mock_state.update_data = AsyncMock(side_effect=RuntimeError("Runtime error"))

        await set_state_data(mock_state, test_data)

        mock_state.update_data.assert_called_once()

    @pytest.mark.asyncio
    async def test_timeout_error_handling(self, mock_state):
        """Обработка TimeoutError"""
        test_data = {"city": "Moscow"}
        mock_state.update_data = AsyncMock(side_effect=TimeoutError("Timeout"))

        await set_state_data(mock_state, test_data)

        mock_state.update_data.assert_called_once()


# ============= Integration Tests =============


class TestIntegration:
    """Интеграционные тесты"""

    @pytest.mark.asyncio
    async def test_complete_state_workflow(self, mock_state):
        """Полный рабочий процесс со состоянием"""
        # Устанавливаем состояние ожидания локации
        mock_state.get_state = AsyncMock(
            return_value="LocationState:waiting_for_city_phone"
        )

        # Проверяем, что ждем локацию
        is_waiting = await is_waiting_for_location(mock_state)
        assert is_waiting is True

        # Получаем текущее состояние
        current = await get_current_state(mock_state)
        assert current == "LocationState:waiting_for_city_phone"

        # Сохраняем данные локации
        mock_state.update_data = AsyncMock(return_value=None)
        await set_state_data(
            mock_state, {"city": "Moscow", "latitude": 55.75, "longitude": 37.61}
        )
        mock_state.update_data.assert_called_once()

        # Очищаем состояние
        mock_state.clear = AsyncMock(return_value=None)
        await clear_state(mock_state)
        mock_state.clear.assert_called_once()

    @pytest.mark.asyncio
    async def test_state_transitions(self, mock_state):
        """Переходы между состояниями"""
        # Начальное состояние
        mock_state.get_state = AsyncMock(return_value=None)
        result = await get_current_state(mock_state)
        assert result is None

        # Переход к ожиданию локации
        mock_state.get_state = AsyncMock(
            return_value="LocationState:waiting_for_city_phone"
        )
        is_waiting = await is_waiting_for_location(mock_state)
        assert is_waiting is True

        # Сохранение данных
        mock_state.update_data = AsyncMock(return_value=None)
        await set_state_data(mock_state, {"city": "Moscow"})

        # Очистка состояния
        mock_state.clear = AsyncMock(return_value=None)
        await clear_state(mock_state)

    @pytest.mark.asyncio
    async def test_error_recovery_workflow(self, mock_state):
        """Рабочий процесс с восстановлением после ошибок"""
        # Ошибка при получении состояния
        mock_state.get_state = AsyncMock(side_effect=Exception("Error"))
        result = await get_current_state(mock_state)
        assert result is None

        # Восстановление - успешное получение состояния
        mock_state.get_state = AsyncMock(
            return_value="LocationState:waiting_for_city_phone"
        )
        result = await get_current_state(mock_state)
        assert result == "LocationState:waiting_for_city_phone"

        # Ошибка при сохранении данных
        mock_state.update_data = AsyncMock(side_effect=Exception("Save error"))
        await set_state_data(mock_state, {"city": "Moscow"})

        # Успешная очистка после ошибок
        mock_state.clear = AsyncMock(return_value=None)
        await clear_state(mock_state)
        mock_state.clear.assert_called_once()

    @pytest.mark.asyncio
    async def test_concurrent_state_operations(self, mock_state):
        """Одновременные операции с состоянием"""
        import asyncio

        mock_state.get_state = AsyncMock(
            return_value="LocationState:waiting_for_city_phone"
        )
        mock_state.update_data = AsyncMock(return_value=None)
        mock_state.clear = AsyncMock(return_value=None)

        # Параллельное выполнение операций
        results = await asyncio.gather(
            get_current_state(mock_state),
            is_waiting_for_location(mock_state),
            set_state_data(mock_state, {"city": "Moscow"}),
            clear_state(mock_state),
        )

        assert results[0] == "LocationState:waiting_for_city_phone"
        assert results[1] is True
