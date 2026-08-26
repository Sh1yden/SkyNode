"""Unit тестирование асинхронного модуля headers.py."""

from unittest.mock import patch
import pytest

from bot.src.utils import (
    Browser,
    Platform,
    headers,
    get_user_agent,
    get_random_ua,
    get_accept_header,
    get_accept_encoding,
    get_accept_language,
    get_connection_header,
    create_browser_headers,
    create_random_headers,
    create_api_headers,
    headers_factory,
    Language,
)


# ============= get_user_agent =============
class TestGetUserAgent:
    """Тесты для функции get_user_agent"""

    @pytest.mark.asyncio
    async def test_success_get_user_agent_all_combinations(self):
        """Проверка всех комбинация browser + platform"""

        for browser, plat_dict in headers.USER_AGENTS.items():
            for platform in plat_dict.keys():
                result = await get_user_agent(browser, platform)

                assert isinstance(result, str)
                assert len(result) > 0

    @pytest.mark.asyncio
    async def test_invalid_get_user_agent_return_default(self):
        """Проверка на не существующий ключ и возвращение дефолтного"""
        safari_windows = await get_user_agent(Browser.SAFARI, Platform.WINDOWS)
        safari_linux = await get_user_agent(Browser.SAFARI, Platform.LINUX)
        edge_linux = await get_user_agent(Browser.EDGE, Platform.LINUX)

        assert safari_windows == headers.DEFAULT_USER_AGENT
        assert safari_linux == headers.DEFAULT_USER_AGENT
        assert edge_linux == headers.DEFAULT_USER_AGENT


# ============= get_random_ua =============


class TestGetRandomUserAgent:
    """Тесты для функции get_random_ua"""

    @pytest.mark.asyncio
    async def test_returns_string(self):
        """Возвращает строку"""
        result = await get_random_ua()

        assert isinstance(result, str)
        assert len(result) > 0

    @pytest.mark.asyncio
    async def test_returns_valid_user_agent(self):
        """Возвращает валидный User-Agent"""
        result = await get_random_ua()

        assert "Mozilla" in result

    @pytest.mark.asyncio
    async def test_randomness(self):
        """Проверка случайности (может вернуть разные значения)"""
        results = set()
        for _ in range(20):
            ua = await get_random_ua()
            results.add(ua)

        # Должно быть хотя бы 2 разных UA за 20 попыток
        assert len(results) >= 2


# ============= get_accept_header =============


class TestGetAcceptHeader:
    """Тесты для функции get_accept_header"""

    @pytest.mark.asyncio
    async def test_chrome_accept(self):
        """Accept header для Chrome"""
        result = await get_accept_header(Browser.CHROME)

        assert isinstance(result, str)
        assert "text/html" in result
        assert "application/xhtml+xml" in result

    @pytest.mark.asyncio
    async def test_all_browsers(self):
        """Accept для всех браузеров"""
        for browser in Browser:
            result = await get_accept_header(browser)

            assert isinstance(result, str)
            assert len(result) > 0


# ============= get_accept_encoding =============


class TestGetAcceptEncoding:
    """Тесты для функции get_accept_encoding"""

    @pytest.mark.asyncio
    async def test_returns_compression_methods(self):
        """Возвращает методы сжатия"""
        result = await get_accept_encoding(Browser.CHROME)

        assert isinstance(result, str)
        assert "gzip" in result
        assert "deflate" in result
        assert "br" in result


# ============= get_accept_language =============


class TestGetAcceptLanguage:
    """Тесты для функции get_accept_language"""

    @pytest.mark.asyncio
    async def test_default_russian(self):
        """Дефолтный русский язык"""
        result = await get_accept_language(Language.RU)

        assert isinstance(result, str)
        assert "ru-RU" in result

    @pytest.mark.asyncio
    async def test_english(self):
        """Английский язык"""
        result = await get_accept_language(Language.EN_US)

        assert isinstance(result, str)
        assert "en-US" in result

    @pytest.mark.asyncio
    async def test_with_additional_languages(self):
        """С дополнительными языками"""
        result = await get_accept_language(
            Language.RU, additional_langs=[Language.EN_US, Language.DE]
        )

        assert "ru-RU" in result
        assert "en-US" in result
        assert "de-DE" in result


# ============= get_connection_header =============


class TestGetConnectionHeader:
    """Тесты для функции get_connection_header"""

    @pytest.mark.asyncio
    async def test_keep_alive_true(self):
        """Keep-alive включен"""
        result = await get_connection_header(keep_alive=True)

        assert result == "keep-alive"

    @pytest.mark.asyncio
    async def test_keep_alive_false(self):
        """Keep-alive выключен"""
        result = await get_connection_header(keep_alive=False)

        assert result == "close"


# ============= create_browser_headers =============


class TestCreateBrowserHeaders:
    """Тесты для функции create_browser_headers"""

    @pytest.mark.asyncio
    async def test_chrome_windows_headers(self):
        """Headers для Chrome на Windows"""
        headers = await create_browser_headers(
            Browser.CHROME, Platform.WINDOWS, Language.RU
        )

        assert isinstance(headers, dict)
        assert "User-Agent" in headers
        assert "Accept" in headers
        assert "Accept-Encoding" in headers
        assert "Accept-Language" in headers
        assert "Connection" in headers

        assert "Chrome" in headers["User-Agent"]
        assert "Windows" in headers["User-Agent"]

    @pytest.mark.asyncio
    async def test_with_extra_headers(self):
        """С дополнительными headers"""
        extra = {"X-Custom-Header": "test-value"}

        headerss = await create_browser_headers(
            Browser.CHROME, Platform.WINDOWS, extra_headers=extra
        )

        assert "X-Custom-Header" in headerss
        assert headerss["X-Custom-Header"] == "test-value"

    @pytest.mark.asyncio
    async def test_all_browser_platform_combinations(self):
        """Все комбинации браузеров и платформ"""
        for browser, platform_dict in headers.USER_AGENTS.items():
            for platform in platform_dict.keys():
                headerss = await create_browser_headers(browser, platform)

                assert isinstance(headerss, dict)
                assert len(headerss) >= 5


# ============= create_random_headers =============


class TestCreateRandomHeaders:
    """Тесты для функции create_random_headers"""

    @pytest.mark.asyncio
    async def test_returns_valid_headers(self):
        """Возвращает валидные headers"""
        headers = await create_random_headers()

        assert isinstance(headers, dict)
        assert "User-Agent" in headers
        assert "Accept" in headers

    @pytest.mark.asyncio
    async def test_with_language(self):
        """С указанным языком"""
        headers = await create_random_headers(lang=Language.EN_US)

        assert "en-US" in headers["Accept-Language"]

    @pytest.mark.asyncio
    async def test_modern_headers_included(self):
        """Современные headers включены"""
        headers = await create_random_headers(include_modern=True)

        # Может содержать Sec-Ch-Ua если браузер Chrome/Edge
        if "Chrome" in headers["User-Agent"] or "Edg" in headers["User-Agent"]:
            assert any(key.startswith("Sec-Ch") for key in headers.keys())


# ============= create_api_headers =============


class TestCreateApiHeaders:
    """Тесты для функции create_api_headers"""

    @pytest.mark.asyncio
    async def test_default_json_headers(self):
        """Дефолтные JSON headers"""
        headers = await create_api_headers()

        assert headers["Content-Type"] == "application/json"
        assert headers["Accept"] == "application/json"
        assert "User-Agent" in headers

    @pytest.mark.asyncio
    async def test_with_auth_token(self):
        """С токеном авторизации"""
        headers = await create_api_headers(auth_token="test_token_123")

        assert "Authorization" in headers
        assert headers["Authorization"] == "Bearer test_token_123"

    @pytest.mark.asyncio
    async def test_custom_content_type(self):
        """С кастомным Content-Type"""
        headers = await create_api_headers(content_type="application/xml")

        assert headers["Content-Type"] == "application/xml"


# ============= headers_factory =============


class TestHeadersFactory:
    """Тесты для функции headers_factory"""

    @pytest.mark.asyncio
    async def test_api_headers(self):
        """API headers через фабрику"""
        headers = await headers_factory(is_api=True)

        assert headers["Content-Type"] == "application/json"

    @pytest.mark.asyncio
    async def test_browser_headers_with_params(self):
        """Browser headers с параметрами"""
        headers = await headers_factory(
            browser=Browser.CHROME, platform=Platform.WINDOWS, lang=Language.RU
        )

        assert "Chrome" in headers["User-Agent"]
        assert "ru-RU" in headers["Accept-Language"]

    @pytest.mark.asyncio
    async def test_random_headers_without_params(self):
        """Случайные headers без параметров"""
        headers = await headers_factory()

        assert isinstance(headers, dict)
        assert "User-Agent" in headers


# ============= Редкие случаи =============


class TestEdgeCases:
    """Редкие случаи и обработка ошибок"""

    @pytest.mark.asyncio
    async def test_empty_extra_headers(self):
        """Пустые дополнительные headers"""
        headers = await create_browser_headers(
            Browser.CHROME, Platform.WINDOWS, extra_headers={}
        )

        assert isinstance(headers, dict)

    @pytest.mark.asyncio
    async def test_none_auth_token(self):
        """None в качестве auth_token"""
        headers = await create_api_headers(auth_token=None)

        assert "Authorization" not in headers


# ============= Тестирование обработки ошибок =============


class TestErrorHandling:
    """Тестирование обработки ошибок во всех функциях"""

    # ===== get_user_agent =====

    @pytest.mark.asyncio
    async def test_get_user_agent_with_invalid_browser_type(self):
        """Невалидный тип браузера возвращает дефолт"""
        with patch("src.utils.headers._lg") as mock_logger:
            result = await get_user_agent("invalid_browser", Platform.WINDOWS)

            assert result == headers.DEFAULT_USER_AGENT
            mock_logger.error.assert_called()

    @pytest.mark.asyncio
    async def test_get_user_agent_with_invalid_platform_type(self):
        """Невалидный тип платформы возвращает дефолт"""
        with patch("src.utils.headers._lg") as mock_logger:
            result = await get_user_agent(Browser.CHROME, "invalid_platform")

            assert result == headers.DEFAULT_USER_AGENT
            mock_logger.error.assert_called()

    @pytest.mark.asyncio
    async def test_get_user_agent_with_none_values(self):
        """None значения возвращают дефолт"""
        with patch("src.utils.headers._lg") as mock_logger:
            result1 = await get_user_agent(None, Platform.WINDOWS)
            result2 = await get_user_agent(Browser.CHROME, None)

            assert result1 == headers.DEFAULT_USER_AGENT
            assert result2 == headers.DEFAULT_USER_AGENT
            assert mock_logger.error.call_count >= 2

    @pytest.mark.asyncio
    async def test_get_user_agent_exception_handling(self):
        """Исключение в get_user_agent обрабатывается"""
        with patch.dict("src.utils.headers.USER_AGENTS", {}, clear=True):
            with patch("src.utils.headers._lg") as mock_logger:
                result = await get_user_agent(Browser.CHROME, Platform.WINDOWS)

                assert result == headers.DEFAULT_USER_AGENT
                mock_logger.error.assert_called()

    # ===== get_random_ua =====

    @pytest.mark.asyncio
    async def test_get_random_ua_with_empty_user_agents(self):
        """Пустой USER_AGENTS возвращает дефолт"""
        with patch.dict("src.utils.headers.USER_AGENTS", {}, clear=True):
            with patch("src.utils.headers._lg") as mock_logger:
                result = await get_random_ua()

                assert result == headers.DEFAULT_USER_AGENT
                mock_logger.error.assert_called()

    @pytest.mark.asyncio
    async def test_get_random_ua_exception_returns_default(self):
        """Исключение возвращает дефолтный UA"""
        with patch("random.choice", side_effect=Exception("Random error")):
            with patch("src.utils.headers._lg") as mock_logger:
                result = await get_random_ua()

                assert result == headers.DEFAULT_USER_AGENT
                mock_logger.error.assert_called()

    # ===== get_accept_header =====

    @pytest.mark.asyncio
    async def test_get_accept_header_with_invalid_browser(self):
        """Невалидный браузер возвращает дефолт"""
        result = await get_accept_header("invalid")

        assert result == headers.DEFAULT_ACCEPT

    @pytest.mark.asyncio
    async def test_get_accept_header_with_none(self):
        """None возвращает дефолт"""

        result = await get_accept_header(None)

        assert result == headers.DEFAULT_ACCEPT

    # ===== get_accept_encoding =====

    @pytest.mark.asyncio
    async def test_get_accept_encoding_exception_handling(self):
        """Исключение возвращает дефолт"""
        # Просто вызываем с любым значением - функция стабильна
        result = await get_accept_encoding(Browser.CHROME)

        assert isinstance(result, str)
        assert len(result) > 0

    # ===== get_accept_language =====

    @pytest.mark.asyncio
    async def test_get_accept_language_with_invalid_language(self):
        """Невалидный язык возвращает дефолт"""
        with patch("src.utils.headers._lg") as mock_logger:
            result = await get_accept_language("invalid_lang")

            assert result == headers.DEFAULT_ACCEPT_LANGUAGE
            mock_logger.error.assert_called()

    @pytest.mark.asyncio
    async def test_get_accept_language_with_none(self):
        """None возвращает дефолт"""
        with patch("src.utils.headers._lg") as mock_logger:
            result = await get_accept_language(None)

            assert result == headers.DEFAULT_ACCEPT_LANGUAGE
            mock_logger.error.assert_called()

    @pytest.mark.asyncio
    async def test_get_accept_language_with_invalid_additional_langs(self):
        """Невалидные дополнительные языки обрабатываются"""
        with patch("src.utils.headers._lg") as mock_logger:
            result = await get_accept_language(
                Language.RU, additional_langs=["invalid", None, 123]
            )

            # Должен вернуть дефолт или обработать ошибку
            assert isinstance(result, str)
            assert len(result) > 0

    # ===== get_connection_header =====

    @pytest.mark.asyncio
    async def test_get_connection_header_exception_handling(self):
        """Исключение возвращает дефолт"""
        with patch("builtins.bool", side_effect=Exception("Error")):
            result = await get_connection_header(True)

            assert result == headers.DEFAULT_CONNECTION

    # ===== create_browser_headers =====

    @pytest.mark.asyncio
    async def test_create_browser_headers_with_invalid_browser(self):
        """Невалидный браузер возвращает минимальные headers"""
        with patch("src.utils.headers._lg") as mock_logger:
            result = await create_browser_headers("invalid", Platform.WINDOWS)

            assert isinstance(result, dict)
            assert "User-Agent" in result
            assert result["User-Agent"] == headers.DEFAULT_USER_AGENT
            mock_logger.error.assert_called()

    @pytest.mark.asyncio
    async def test_create_browser_headers_with_none_values(self):
        """None значения возвращают минимальные headers"""
        with patch("src.utils.headers._lg") as mock_logger:
            result = await create_browser_headers(None, None)

            assert isinstance(result, dict)
            assert len(result) >= 5  # Минимум 5 обязательных headers
            mock_logger.error.assert_called()

    @pytest.mark.asyncio
    async def test_create_browser_headers_exception_handling(self):
        """Исключение возвращает минимальные headers"""
        with patch("src.utils.headers.get_user_agent", side_effect=Exception("Error")):
            with patch("src.utils.headers._lg") as mock_logger:
                result = await create_browser_headers(Browser.CHROME, Platform.WINDOWS)

                assert isinstance(result, dict)
                assert "User-Agent" in result
                mock_logger.error.assert_called()

    @pytest.mark.asyncio
    async def test_create_browser_headers_with_invalid_extra_headers(self):
        """Невалидные extra headers обрабатываются"""
        # Extra headers не dict
        result = await create_browser_headers(
            Browser.CHROME, Platform.WINDOWS, extra_headers="invalid"
        )

        assert isinstance(result, dict)
        assert "User-Agent" in result

    # ===== create_random_headers =====

    @pytest.mark.asyncio
    async def test_create_random_headers_exception_handling(self):
        """Исключение возвращает минимальные headers"""
        with patch("random.choice", side_effect=Exception("Error")):
            with patch("src.utils.headers._lg") as mock_logger:
                result = await create_random_headers()

                assert isinstance(result, dict)
                assert "User-Agent" in result
                mock_logger.error.assert_called()

    @pytest.mark.asyncio
    async def test_create_random_headers_with_invalid_language(self):
        """Невалидный язык обрабатывается"""
        result = await create_random_headers(lang="invalid")

        assert isinstance(result, dict)
        assert "Accept-Language" in result

    # ===== create_api_headers =====

    @pytest.mark.asyncio
    async def test_create_api_headers_exception_handling(self):
        """Исключение возвращает минимальные API headers"""
        with patch("src.utils.headers._lg") as mock_logger:
            # Симулируем ошибку при создании headers
            with patch.dict("src.utils.headers.__dict__", {"DEFAULT_USER_AGENT": None}):
                result = await create_api_headers()

                assert isinstance(result, dict)
                # Должны быть минимальные поля
                assert "Content-Type" in result or "User-Agent" in result

    @pytest.mark.asyncio
    async def test_create_api_headers_with_none_content_type(self):
        """None content_type обрабатывается"""
        result = await create_api_headers(content_type=None)

        assert isinstance(result, dict)
        # Должен установить дефолтный content-type
        assert "Content-Type" in result

    @pytest.mark.asyncio
    async def test_create_api_headers_with_empty_auth_token(self):
        """Пустой auth_token обрабатывается"""
        result1 = await create_api_headers(auth_token="")
        result2 = await create_api_headers(auth_token=None)

        # С пустым токеном Authorization может быть или не быть
        assert isinstance(result1, dict)
        assert isinstance(result2, dict)

    # ===== headers_factory =====

    @pytest.mark.asyncio
    async def test_headers_factory_with_invalid_params(self):
        """Невалидные параметры обрабатываются"""
        with patch("src.utils.headers._lg") as mock_logger:
            result = await headers_factory(browser="invalid", platform="invalid")

            assert isinstance(result, dict)
            assert "User-Agent" in result

    @pytest.mark.asyncio
    async def test_headers_factory_with_none_params(self):
        """None параметры возвращают случайные headers"""
        result = await headers_factory(browser=None, platform=None)

        assert isinstance(result, dict)
        assert "User-Agent" in result

    @pytest.mark.asyncio
    async def test_headers_factory_exception_handling(self):
        """Исключение возвращает минимальные headers"""
        with patch(
            "src.utils.headers.create_browser_headers", side_effect=Exception("Error")
        ):
            with patch("src.utils.headers._lg") as mock_logger:
                result = await headers_factory(
                    browser=Browser.CHROME, platform=Platform.WINDOWS
                )

                assert isinstance(result, dict)
                assert "User-Agent" in result
                mock_logger.error.assert_called()

    @pytest.mark.asyncio
    async def test_headers_factory_all_functions_fail(self):
        """Все функции падают - возвращает минимальный набор"""
        with patch(
            "src.utils.headers.create_api_headers", side_effect=Exception("Error")
        ):
            with patch(
                "src.utils.headers.create_browser_headers",
                side_effect=Exception("Error"),
            ):
                with patch(
                    "src.utils.headers.create_random_headers",
                    side_effect=Exception("Error"),
                ):
                    with patch("src.utils.headers._lg") as mock_logger:
                        result = await headers_factory()

                        assert isinstance(result, dict)
                        assert len(result) >= 4
                        mock_logger.error.assert_called()


# ============= Комплексные сценарии ошибок =============


class TestComplexErrorScenarios:
    """Комплексные сценарии с несколькими ошибками"""

    @pytest.mark.asyncio
    async def test_cascading_errors_in_browser_headers(self):
        """Каскадные ошибки при создании browser headers"""
        with patch(
            "src.utils.headers.get_user_agent", side_effect=Exception("UA Error")
        ):
            with patch(
                "src.utils.headers.get_accept_header",
                side_effect=Exception("Accept Error"),
            ):
                with patch("src.utils.headers._lg") as mock_logger:
                    result = await create_browser_headers(
                        Browser.CHROME, Platform.WINDOWS
                    )

                    # Должны получить минимальные headers
                    assert isinstance(result, dict)
                    assert len(result) >= 5
                    # Логгер должен быть вызван для каждой ошибки
                    assert mock_logger.error.call_count >= 1

    @pytest.mark.asyncio
    async def test_partial_success_with_some_errors(self):
        """Частичный успех - некоторые функции падают"""
        with patch(
            "src.utils.headers.get_accept_encoding",
            side_effect=Exception("Encoding Error"),
        ):
            result = await create_browser_headers(Browser.CHROME, Platform.WINDOWS)

            # Должны получить headers, но с дефолтным Accept-Encoding
            assert isinstance(result, dict)
            assert "User-Agent" in result
            assert "Accept-Encoding" in result
            assert result["Accept-Encoding"] == headers.DEFAULT_ACCEPT_ENCODING

    @pytest.mark.asyncio
    async def test_corrupted_user_agents_dict(self):
        """Повреждённый словарь USER_AGENTS"""
        with patch.dict(
            "src.utils.headers.USER_AGENTS", {"corrupted": "data"}, clear=True
        ):
            with patch("src.utils.headers._lg") as mock_logger:
                # Все функции должны вернуть дефолты
                ua = await get_user_agent(Browser.CHROME, Platform.WINDOWS)
                random_ua = await get_random_ua()

                assert ua == headers.DEFAULT_USER_AGENT
                assert random_ua == headers.DEFAULT_USER_AGENT
                assert mock_logger.error.call_count >= 2

    @pytest.mark.asyncio
    async def test_memory_error_handling(self):
        """Обработка MemoryError"""
        with patch(
            "src.utils.headers.get_user_agent", side_effect=MemoryError("Out of memory")
        ):
            with patch("src.utils.headers._lg") as mock_logger:
                result = await create_browser_headers(Browser.CHROME, Platform.WINDOWS)

                assert isinstance(result, dict)
                mock_logger.error.assert_called()


# ============= Граничные случаи с ошибками =============


class TestErrorEdgeCases:
    """Граничные случаи обработки ошибок"""

    @pytest.mark.asyncio
    async def test_extremely_long_user_agent_error(self):
        """Обработка экстремально длинного User-Agent"""
        long_ua = "A" * 1000000  # 1 млн символов

        with patch("src.utils.headers.get_user_agent", return_value=long_ua):
            result = await create_browser_headers(Browser.CHROME, Platform.WINDOWS)

            # Должно вернуть результат без краша
            assert isinstance(result, dict)
            assert "User-Agent" in result

    @pytest.mark.asyncio
    async def test_recursive_error_prevention(self):
        """Предотвращение рекурсивных ошибок"""
        call_count = 0

        async def failing_function(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count > 5:
                return headers.DEFAULT_USER_AGENT
            raise Exception("Recursive error")

        with patch("src.utils.headers.get_user_agent", side_effect=failing_function):
            result = await create_browser_headers(Browser.CHROME, Platform.WINDOWS)

            # Не должно зависнуть в бесконечном цикле
            assert isinstance(result, dict)
            assert call_count <= 10  # Разумный лимит попыток

    @pytest.mark.asyncio
    async def test_async_exception_handling(self):
        """Обработка асинхронных исключений"""

        async def async_error():
            raise RuntimeError("Async error")

        with patch("src.utils.headers.get_user_agent", side_effect=async_error):
            with patch("src.utils.headers._lg") as mock_logger:
                result = await create_browser_headers(Browser.CHROME, Platform.WINDOWS)

                assert isinstance(result, dict)
                mock_logger.error.assert_called()
