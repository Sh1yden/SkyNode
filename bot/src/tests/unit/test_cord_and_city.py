"""Unit тестирование асинхронного модуля cord_and_city.py."""

import pytest
from unittest.mock import patch
import aiohttp
import asyncio

from bot.src.services import get_city_from_cord, get_cord_from_city


# ============= get_city_from_cord =============


class TestGetCityFromCord:
    """Тесты для функции get_city_from_cord"""

    @pytest.mark.asyncio
    async def test_success_with_city(self, mock_successful_nominatim_response):
        """Успешное получение города из координат"""
        with patch("src.services.cord_and_city.req_data") as mock_req_data:
            mock_req_data.return_value = mock_successful_nominatim_response

            result = await get_city_from_cord(55.7558, 37.6173)

            assert result == "Moscow"
            mock_req_data.assert_called_once()

    @pytest.mark.asyncio
    async def test_success_with_town(self, mock_nominatim_response_with_town):
        """Успешное получение town из координат"""
        with patch("src.services.cord_and_city.req_data") as mock_req_data:
            mock_req_data.return_value = mock_nominatim_response_with_town

            result = await get_city_from_cord(51.7373, 36.1873)

            assert result == "Kursk"
            mock_req_data.assert_called_once()

    @pytest.mark.asyncio
    async def test_success_with_village(self, mock_nominatim_response_with_village):
        """Успешное получение village из координат"""
        with patch("src.services.cord_and_city.req_data") as mock_req_data:
            mock_req_data.return_value = mock_nominatim_response_with_village

            result = await get_city_from_cord(50.0, 40.0)

            assert result == "Ivanovka"
            mock_req_data.assert_called_once()

    @pytest.mark.asyncio
    async def test_success_with_municipality(
        self, mock_nominatim_response_with_municipality
    ):
        """Успешное получение municipality из координат"""
        with patch("src.services.cord_and_city.req_data") as mock_req_data:
            mock_req_data.return_value = mock_nominatim_response_with_municipality

            result = await get_city_from_cord(50.0, 40.0)

            assert result == "District Center"
            mock_req_data.assert_called_once()

    @pytest.mark.asyncio
    async def test_success_with_county(self, mock_nominatim_response_with_county):
        """Успешное получение county из координат"""
        with patch("src.services.cord_and_city.req_data") as mock_req_data:
            mock_req_data.return_value = mock_nominatim_response_with_county

            result = await get_city_from_cord(50.0, 40.0)

            assert result == "Oblast"
            mock_req_data.assert_called_once()

    @pytest.mark.asyncio
    async def test_no_city_found_returns_none(self, mock_nominatim_response_no_city):
        """Город не найден возвращает None"""
        with patch("src.services.cord_and_city.req_data") as mock_req_data:
            mock_req_data.return_value = mock_nominatim_response_no_city

            result = await get_city_from_cord(0.0, 0.0)

            assert result is None
            mock_req_data.assert_called_once()

    @pytest.mark.asyncio
    async def test_timeout_returns_none(self):
        """Таймаут возвращает None"""
        with patch("src.services.cord_and_city.req_data") as mock_req_data:
            mock_req_data.side_effect = asyncio.TimeoutError()

            result = await get_city_from_cord(55.7558, 37.6173)

            assert result is None

    @pytest.mark.asyncio
    async def test_client_error_returns_none(self):
        """Ошибка клиента возвращает None"""
        with patch("src.services.cord_and_city.req_data") as mock_req_data:
            mock_req_data.side_effect = aiohttp.ClientError("Connection failed")

            result = await get_city_from_cord(55.7558, 37.6173)

            assert result is None

    @pytest.mark.asyncio
    async def test_value_error_returns_none(self):
        """ValueError при парсинге возвращает None"""
        with patch("src.services.cord_and_city.req_data") as mock_req_data:
            mock_req_data.side_effect = ValueError("Invalid JSON")

            result = await get_city_from_cord(55.7558, 37.6173)

            assert result is None

    @pytest.mark.asyncio
    async def test_key_error_returns_none(self):
        """KeyError при доступе к данным возвращает None"""
        with patch("src.services.cord_and_city.req_data") as mock_req_data:
            mock_req_data.return_value = {"wrong_key": "value"}

            result = await get_city_from_cord(55.7558, 37.6173)

            assert result is None

    @pytest.mark.asyncio
    async def test_attribute_error_returns_none(self):
        """AttributeError возвращает None"""
        with patch("src.services.cord_and_city.req_data") as mock_req_data:
            mock_req_data.side_effect = AttributeError("No attribute")

            result = await get_city_from_cord(55.7558, 37.6173)

            assert result is None

    @pytest.mark.asyncio
    async def test_unexpected_exception_returns_none(self):
        """Неожиданное исключение возвращает None"""
        with patch("src.services.cord_and_city.req_data") as mock_req_data:
            mock_req_data.side_effect = Exception("Unexpected error")

            result = await get_city_from_cord(55.7558, 37.6173)

            assert result is None

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "latitude,longitude",
        [
            (55.7558, 37.6173),  # Moscow
            (51.7373, 36.1873),  # Kursk
            (59.9343, 30.3351),  # Saint Petersburg
            (0.0, 0.0),  # Null Island
            (-90.0, 0.0),  # South Pole
            (90.0, 0.0),  # North Pole
        ],
    )
    async def test_various_coordinates(
        self, latitude, longitude, mock_successful_nominatim_response
    ):
        """Различные координаты"""
        with patch("src.services.cord_and_city.req_data") as mock_req_data:
            mock_req_data.return_value = mock_successful_nominatim_response

            result = await get_city_from_cord(latitude, longitude)

            assert result == "Moscow"
            call_args = mock_req_data.call_args
            assert call_args is not None

    @pytest.mark.asyncio
    async def test_string_coordinates(self, mock_successful_nominatim_response):
        """Строковые координаты конвертируются"""
        with patch("src.services.cord_and_city.req_data") as mock_req_data:
            mock_req_data.return_value = mock_successful_nominatim_response

            result = await get_city_from_cord("55.7558", "37.6173")

            assert result == "Moscow"

    @pytest.mark.asyncio
    async def test_float_coordinates(self, mock_successful_nominatim_response):
        """Координаты типа float"""
        with patch("src.services.cord_and_city.req_data") as mock_req_data:
            mock_req_data.return_value = mock_successful_nominatim_response

            result = await get_city_from_cord(55.7558, 37.6173)

            assert result == "Moscow"

    @pytest.mark.asyncio
    async def test_priority_order_city_over_town(self):
        """Приоритет city над town"""
        response = {
            "address": {
                "city": "Moscow",
                "town": "Town",
                "village": "Village",
            }
        }
        with patch("src.services.cord_and_city.req_data") as mock_req_data:
            mock_req_data.return_value = response

            result = await get_city_from_cord(55.7558, 37.6173)

            assert result == "Moscow"

    @pytest.mark.asyncio
    async def test_priority_order_town_over_village(self):
        """Приоритет town над village"""
        response = {
            "address": {
                "city": None,
                "town": "Town",
                "village": "Village",
            }
        }
        with patch("src.services.cord_and_city.req_data") as mock_req_data:
            mock_req_data.return_value = response

            result = await get_city_from_cord(55.7558, 37.6173)

            assert result == "Town"

    @pytest.mark.asyncio
    async def test_none_response_returns_none(self):
        """None ответ возвращает None"""
        with patch("src.services.cord_and_city.req_data") as mock_req_data:
            mock_req_data.return_value = None

            result = await get_city_from_cord(55.7558, 37.6173)

            assert result is None


# ============= get_cord_from_city =============


class TestGetCordFromCity:
    """Тесты для функции get_cord_from_city"""

    @pytest.mark.asyncio
    async def test_success_with_valid_city(self, mock_successful_geocoding_response):
        """Успешное получение координат для валидного города"""
        with patch("src.services.cord_and_city.req_data") as mock_req_data:
            mock_req_data.return_value = mock_successful_geocoding_response

            result = await get_cord_from_city("Moscow")

            assert result == {"lat": "55.7558", "lon": "37.6173"}
            mock_req_data.assert_called_once()

    @pytest.mark.asyncio
    async def test_empty_results_returns_none(self, mock_empty_geocoding_response):
        """Пустые результаты возвращают None"""
        with patch("src.services.cord_and_city.req_data") as mock_req_data:
            mock_req_data.return_value = mock_empty_geocoding_response

            result = await get_cord_from_city("InvalidCityXYZ123")

            assert result is None

    @pytest.mark.asyncio
    async def test_no_results_key_returns_none(
        self, mock_geocoding_response_no_results
    ):
        """Отсутствие ключа results возвращает None"""
        with patch("src.services.cord_and_city.req_data") as mock_req_data:
            mock_req_data.return_value = mock_geocoding_response_no_results

            result = await get_cord_from_city("SomeCity")

            assert result is None

    @pytest.mark.asyncio
    async def test_timeout_returns_none(self):
        """Таймаут возвращает None"""
        with patch("src.services.cord_and_city.req_data") as mock_req_data:
            mock_req_data.side_effect = asyncio.TimeoutError()

            result = await get_cord_from_city("Moscow")

            assert result is None

    @pytest.mark.asyncio
    async def test_client_error_returns_none(self):
        """Ошибка клиента возвращает None"""
        with patch("src.services.cord_and_city.req_data") as mock_req_data:
            mock_req_data.side_effect = aiohttp.ClientError("Connection failed")

            result = await get_cord_from_city("Moscow")

            assert result is None

    @pytest.mark.asyncio
    async def test_index_error_returns_none(self):
        """IndexError возвращает None"""
        with patch("src.services.cord_and_city.req_data") as mock_req_data:
            mock_req_data.side_effect = IndexError("Index out of range")

            result = await get_cord_from_city("Moscow")

            assert result is None

    @pytest.mark.asyncio
    async def test_type_error_returns_none(self):
        """TypeError возвращает None"""
        with patch("src.services.cord_and_city.req_data") as mock_req_data:
            mock_req_data.side_effect = TypeError("Type error")

            result = await get_cord_from_city("Moscow")

            assert result is None

    @pytest.mark.asyncio
    async def test_unexpected_exception_returns_none(self):
        """Неожиданное исключение возвращает None"""
        with patch("src.services.cord_and_city.req_data") as mock_req_data:
            mock_req_data.side_effect = Exception("Unexpected error")

            result = await get_cord_from_city("Moscow")

            assert result is None

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "city_name",
        [
            "Moscow",
            "Москва",
            "New York",
            "Saint-Petersburg",
            "Нью-Йорк",
            "北京",  # Beijing in Chinese
            "Kursk",
        ],
    )
    async def test_various_city_names(
        self, city_name, mock_successful_geocoding_response
    ):
        """Различные названия городов"""
        with patch("src.services.cord_and_city.req_data") as mock_req_data:
            mock_req_data.return_value = mock_successful_geocoding_response

            result = await get_cord_from_city(city_name)

            assert result == {"lat": "55.7558", "lon": "37.6173"}

    @pytest.mark.asyncio
    async def test_city_with_spaces(self, mock_successful_geocoding_response):
        """Город с пробелами"""
        with patch("src.services.cord_and_city.req_data") as mock_req_data:
            mock_req_data.return_value = mock_successful_geocoding_response

            result = await get_cord_from_city("New York City")

            assert result == {"lat": "55.7558", "lon": "37.6173"}

    @pytest.mark.asyncio
    async def test_city_with_special_characters(
        self, mock_successful_geocoding_response
    ):
        """Город со спецсимволами"""
        with patch("src.services.cord_and_city.req_data") as mock_req_data:
            mock_req_data.return_value = mock_successful_geocoding_response

            result = await get_cord_from_city("Saint-Étienne")

            assert result == {"lat": "55.7558", "lon": "37.6173"}

    @pytest.mark.asyncio
    async def test_empty_string_city_returns_none(self):
        """Пустая строка как город"""
        with patch("src.services.cord_and_city.req_data") as mock_req_data:
            mock_req_data.return_value = {"results": []}

            result = await get_cord_from_city("")

            assert result is None

    @pytest.mark.asyncio
    async def test_very_long_city_name(self, mock_successful_geocoding_response):
        """Очень длинное название города"""
        with patch("src.services.cord_and_city.req_data") as mock_req_data:
            mock_req_data.return_value = mock_successful_geocoding_response

            result = await get_cord_from_city("A" * 1000)

            assert result == {"lat": "55.7558", "lon": "37.6173"}

    @pytest.mark.asyncio
    async def test_coordinates_as_strings(self, mock_successful_geocoding_response):
        """Координаты возвращаются как строки"""
        with patch("src.services.cord_and_city.req_data") as mock_req_data:
            mock_req_data.return_value = mock_successful_geocoding_response

            result = await get_cord_from_city("Moscow")

            assert isinstance(result["lat"], str)
            assert isinstance(result["lon"], str)

    @pytest.mark.asyncio
    async def test_negative_coordinates(self):
        """Отрицательные координаты"""
        response = {
            "results": [
                {
                    "latitude": -33.8688,
                    "longitude": 151.2093,
                }
            ]
        }
        with patch("src.services.cord_and_city.req_data") as mock_req_data:
            mock_req_data.return_value = response

            result = await get_cord_from_city("Sydney")

            assert result == {"lat": "-33.8688", "lon": "151.2093"}

    @pytest.mark.asyncio
    async def test_zero_coordinates(self):
        """Нулевые координаты"""
        response = {"results": [{"latitude": 0.0, "longitude": 0.0}]}
        with patch("src.services.cord_and_city.req_data") as mock_req_data:
            mock_req_data.return_value = response

            result = await get_cord_from_city("Null Island")

            assert result == {"lat": "0.0", "lon": "0.0"}

    @pytest.mark.asyncio
    async def test_none_data_returns_none(self):
        """None данные возвращают None"""
        with patch("src.services.cord_and_city.req_data") as mock_req_data:
            mock_req_data.return_value = None

            result = await get_cord_from_city("Moscow")

            assert result is None
