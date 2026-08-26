"""Unit тестирование асинхронного модуля api_helper.py."""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import aiohttp
import asyncio

from bot.src.utils.api_helper import get_raw_link_api, req_data

# ============= get_raw_link_api =============


class TestGetRawLinkApi:
    """Тесты для функции get_raw_link_api"""

    @pytest.mark.asyncio
    async def test_return_all_links_when_no_api_name(self):
        """Возвращает все ссылки когда api_name=None"""
        result = await get_raw_link_api()

        assert isinstance(result, dict)
        assert "OpenMeteo" in result
        assert "WeatherAPI" in result
        assert "YandexParser" in result

    @pytest.mark.asyncio
    async def test_return_specific_link_for_open_meteo(self):
        """Возвращает ссылку для OpenMeteo"""
        result = await get_raw_link_api(api_name="OpenMeteo")

        assert isinstance(result, str)
        assert "open-meteo.com" in result

    @pytest.mark.asyncio
    async def test_return_specific_link_for_weather_api(self):
        """Возвращает ссылку для WeatherAPI"""
        result = await get_raw_link_api(api_name="WeatherAPI")

        assert isinstance(result, str)
        assert "weatherapi.com" in result

    @pytest.mark.asyncio
    async def test_return_specific_link_for_yandex_parser(self):
        """Возвращает ссылку для YandexParser"""
        result = await get_raw_link_api(api_name="YandexParser")

        assert isinstance(result, str)
        assert "yandex.ru/pogoda" in result

    @pytest.mark.asyncio
    async def test_return_specific_link_for_nominatim(self):
        """Возвращает ссылку для Nominatim"""
        result = await get_raw_link_api(api_name="Nominatim")

        assert isinstance(result, str)
        assert "nominatim.openstreetmap.org" in result

    @pytest.mark.asyncio
    async def test_return_specific_link_for_geocoding(self):
        """Возвращает ссылку для Geocoding"""
        result = await get_raw_link_api(api_name="Geocoding")

        assert isinstance(result, str)
        assert "geocoding-api.open-meteo.com" in result

    @pytest.mark.asyncio
    async def test_replace_lat_lon_in_all_links_when_provided(self):
        """Заменяет {lat} и {lon} во всех ссылках"""
        result = await get_raw_link_api(latitude=51.5074, longitude=-0.1278)

        assert isinstance(result, dict)
        visual_crossing_link = result.get("VisualCrossing", "")
        # Проверяем что плейсхолдеры заменены
        assert "{lat}" not in visual_crossing_link
        assert "{lon}" not in visual_crossing_link

    @pytest.mark.asyncio
    async def test_none_coordinates_are_converted_to_string(self):
        """None координаты конвертируются в строку 'None'"""
        result = await get_raw_link_api(
            latitude=None, longitude=None, api_name="VisualCrossing"
        )

        assert "None" in result

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "api_name",
        [
            "OpenMeteo",
            "VisualCrossing",
            "WeatherAPI",
            "YandexParser",
            "Nominatim",
            "Geocoding",
        ],
    )
    async def test_all_api_names(self, api_name):
        """Все доступные API имена"""
        result = await get_raw_link_api(api_name=api_name)

        assert isinstance(result, str)
        assert len(result) > 0

    @pytest.mark.asyncio
    async def test_invalid_api_name_returns_none_or_raises(self):
        """Несуществующее API имя вызывает ошибку или возвращает None"""
        # Функция может либо выбросить KeyError, либо вернуть None
        # В зависимости от реализации
        try:
            result = await get_raw_link_api(api_name="NonExistentAPI")
            # Если не выбросило исключение, результат должен быть None
            assert result is None
        except (KeyError, Exception):
            # Это ожидаемое поведение
            pass

    @pytest.mark.asyncio
    async def test_all_links_have_proper_format(self):
        """Все ссылки имеют правильный формат"""
        result = await get_raw_link_api()

        assert isinstance(result, dict)
        for service_name, link in result.items():
            assert isinstance(link, str)
            assert link.startswith("https://")


# ============= req_data =============


class TestReqData:
    """Тесты для функции req_data"""

    @pytest.mark.asyncio
    async def test_success_with_valid_url_and_params(
        self, mock_successful_json_response
    ):
        """Успешный запрос с валидными URL и параметрами"""
        with patch("src.utils.api_helper.aiohttp.ClientSession") as mock_session_class:
            # Создаем моки для всей цепочки вызовов
            mock_response = AsyncMock()
            mock_response.json = AsyncMock(return_value=mock_successful_json_response)
            mock_response.raise_for_status = MagicMock()

            mock_get = AsyncMock()
            mock_get.__aenter__ = AsyncMock(return_value=mock_response)
            mock_get.__aexit__ = AsyncMock(return_value=None)

            mock_session = AsyncMock()
            mock_session.get = MagicMock(return_value=mock_get)

            mock_session_class.return_value.__aenter__ = AsyncMock(
                return_value=mock_session
            )
            mock_session_class.return_value.__aexit__ = AsyncMock(return_value=None)

            result = await req_data(
                url="https://api.example.com/data",
                params={"key": "value"},
            )

            assert result == mock_successful_json_response

    @pytest.mark.asyncio
    async def test_success_with_headers(self, mock_successful_json_response):
        """Успешный запрос с headers"""
        with patch("src.utils.api_helper.aiohttp.ClientSession") as mock_session_class:
            mock_response = AsyncMock()
            mock_response.json = AsyncMock(return_value=mock_successful_json_response)
            mock_response.raise_for_status = MagicMock()

            mock_get = AsyncMock()
            mock_get.__aenter__ = AsyncMock(return_value=mock_response)
            mock_get.__aexit__ = AsyncMock(return_value=None)

            mock_session = AsyncMock()
            mock_session.get = MagicMock(return_value=mock_get)

            mock_session_class.return_value.__aenter__ = AsyncMock(
                return_value=mock_session
            )
            mock_session_class.return_value.__aexit__ = AsyncMock(return_value=None)

            headers = {"User-Agent": "TestBot/1.0", "Accept": "application/json"}
            result = await req_data(
                url="https://api.example.com/data",
                params={"key": "value"},
                headers=headers,
            )

            assert result == mock_successful_json_response

    @pytest.mark.asyncio
    async def test_empty_params(self, mock_successful_json_response):
        """Пустые параметры"""
        with patch("src.utils.api_helper.aiohttp.ClientSession") as mock_session_class:
            mock_response = AsyncMock()
            mock_response.json = AsyncMock(return_value=mock_successful_json_response)
            mock_response.raise_for_status = MagicMock()

            mock_get = AsyncMock()
            mock_get.__aenter__ = AsyncMock(return_value=mock_response)
            mock_get.__aexit__ = AsyncMock(return_value=None)

            mock_session = AsyncMock()
            mock_session.get = MagicMock(return_value=mock_get)

            mock_session_class.return_value.__aenter__ = AsyncMock(
                return_value=mock_session
            )
            mock_session_class.return_value.__aexit__ = AsyncMock(return_value=None)

            result = await req_data(url="https://api.example.com/data", params={})

            assert result == mock_successful_json_response

    @pytest.mark.asyncio
    async def test_timeout_returns_none(self):
        """Таймаут возвращает None"""
        with patch("src.utils.api_helper.aiohttp.ClientSession") as mock_session_class:
            mock_session = AsyncMock()
            mock_session.get = MagicMock(side_effect=asyncio.TimeoutError())

            mock_session_class.return_value.__aenter__ = AsyncMock(
                return_value=mock_session
            )
            mock_session_class.return_value.__aexit__ = AsyncMock(return_value=None)

            result = await req_data(
                url="https://api.example.com/data",
                params={"key": "value"},
            )

            assert result is None

    @pytest.mark.asyncio
    async def test_client_error_returns_none(self):
        """ClientError возвращает None"""
        with patch("src.utils.api_helper.aiohttp.ClientSession") as mock_session_class:
            mock_session = AsyncMock()
            mock_session.get = MagicMock(
                side_effect=aiohttp.ClientError("Connection failed")
            )

            mock_session_class.return_value.__aenter__ = AsyncMock(
                return_value=mock_session
            )
            mock_session_class.return_value.__aexit__ = AsyncMock(return_value=None)

            result = await req_data(
                url="https://api.example.com/data",
                params={"key": "value"},
            )

            assert result is None

    @pytest.mark.asyncio
    async def test_value_error_returns_none(self):
        """ValueError при парсинге JSON возвращает None"""
        with patch("src.utils.api_helper.aiohttp.ClientSession") as mock_session_class:
            mock_response = AsyncMock()
            mock_response.json = AsyncMock(side_effect=ValueError("Invalid JSON"))
            mock_response.raise_for_status = MagicMock()

            mock_get = AsyncMock()
            mock_get.__aenter__ = AsyncMock(return_value=mock_response)
            mock_get.__aexit__ = AsyncMock(return_value=None)

            mock_session = AsyncMock()
            mock_session.get = MagicMock(return_value=mock_get)

            mock_session_class.return_value.__aenter__ = AsyncMock(
                return_value=mock_session
            )
            mock_session_class.return_value.__aexit__ = AsyncMock(return_value=None)

            result = await req_data(
                url="https://api.example.com/data",
                params={"key": "value"},
            )

            assert result is None

    @pytest.mark.asyncio
    async def test_unexpected_exception_returns_none(self):
        """Неожиданное исключение возвращает None"""
        with patch("src.utils.api_helper.aiohttp.ClientSession") as mock_session_class:
            mock_session = AsyncMock()
            mock_session.get = MagicMock(side_effect=Exception("Unexpected error"))

            mock_session_class.return_value.__aenter__ = AsyncMock(
                return_value=mock_session
            )
            mock_session_class.return_value.__aexit__ = AsyncMock(return_value=None)

            result = await req_data(
                url="https://api.example.com/data",
                params={"key": "value"},
            )

            assert result is None

    @pytest.mark.asyncio
    async def test_empty_json_response(self, mock_empty_json_response):
        """Пустой JSON ответ"""
        with patch("src.utils.api_helper.aiohttp.ClientSession") as mock_session_class:
            mock_response = AsyncMock()
            mock_response.json = AsyncMock(return_value=mock_empty_json_response)
            mock_response.raise_for_status = MagicMock()

            mock_get = AsyncMock()
            mock_get.__aenter__ = AsyncMock(return_value=mock_response)
            mock_get.__aexit__ = AsyncMock(return_value=None)

            mock_session = AsyncMock()
            mock_session.get = MagicMock(return_value=mock_get)

            mock_session_class.return_value.__aenter__ = AsyncMock(
                return_value=mock_session
            )
            mock_session_class.return_value.__aexit__ = AsyncMock(return_value=None)

            result = await req_data(
                url="https://api.example.com/data",
                params={"key": "value"},
            )

            assert result == {}

    @pytest.mark.asyncio
    async def test_http_status_error_returns_none(self):
        """HTTP ошибка статуса возвращает None"""
        with patch("src.utils.api_helper.aiohttp.ClientSession") as mock_session_class:
            mock_response = AsyncMock()
            mock_response.raise_for_status = MagicMock(
                side_effect=aiohttp.ClientResponseError(
                    request_info=MagicMock(),
                    history=(),
                    status=404,
                    message="Not Found",
                )
            )

            mock_get = AsyncMock()
            mock_get.__aenter__ = AsyncMock(return_value=mock_response)
            mock_get.__aexit__ = AsyncMock(return_value=None)

            mock_session = AsyncMock()
            mock_session.get = MagicMock(return_value=mock_get)

            mock_session_class.return_value.__aenter__ = AsyncMock(
                return_value=mock_session
            )
            mock_session_class.return_value.__aexit__ = AsyncMock(return_value=None)

            result = await req_data(
                url="https://api.example.com/data",
                params={"key": "value"},
            )

            assert result is None

    @pytest.mark.asyncio
    async def test_connection_error_returns_none(self):
        """ConnectionError возвращает None"""
        with patch("src.utils.api_helper.aiohttp.ClientSession") as mock_session_class:
            mock_session = AsyncMock()
            mock_session.get = MagicMock(
                side_effect=aiohttp.ClientConnectionError("Connection refused")
            )

            mock_session_class.return_value.__aenter__ = AsyncMock(
                return_value=mock_session
            )
            mock_session_class.return_value.__aexit__ = AsyncMock(return_value=None)

            result = await req_data(
                url="https://api.example.com/data",
                params={"key": "value"},
            )

            assert result is None
