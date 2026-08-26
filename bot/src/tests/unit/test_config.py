"""Unit тесты для модуля config"""

import pytest
from unittest.mock import patch

from common.utils import SettingsSchema


class TestSettingsSchema:
    """Тесты для класса SettingsSchema"""

    def test_settings_schema_fields_exist(self):
        """Проверка что все обязательные поля определены"""
        expected_fields = [
            "PROJECT_STATUS",  # Добавили новое поле
            "TELEGRAM_BOT_TOKEN",
            "TELEGRAM_WEBHOOK_SECRET",
            "TUNA_TOKEN",
            "TUNA_API_TOKEN",
            "VISUAL_CROSSING_KEY",
            "WEATHER_API_KEY",
            "OPEN_WEATHER_MAP_API_KEY",
        ]

        for field in expected_fields:
            assert field in SettingsSchema.model_fields

    def test_all_fields_are_strings(self):
        """Все поля должны быть строками или Literal"""
        from typing import Literal, get_origin, get_args

        for field_name, field_info in SettingsSchema.model_fields.items():
            annotation = field_info.annotation

            # Проверяем что это либо str, либо Literal со строками
            if get_origin(annotation) is Literal:
                # Для Literal проверяем что все значения - строки
                literal_values = get_args(annotation)
                assert all(
                    isinstance(v, str) for v in literal_values
                ), f"Field {field_name} Literal values must be strings"
            else:
                assert (
                    annotation == str
                ), f"Field {field_name} must be str or Literal[str, ...]"

    def test_model_config_exists(self):
        """Проверка конфигурации модели"""
        config = SettingsSchema.model_config

        assert config is not None
        # env_file теперь динамический, проверяем что он есть
        assert "env_file" in config
        assert config.get("extra") == "allow"


class TestSettingsLoading:
    """Тесты загрузки настроек"""

    def test_load_settings_from_env_vars(self):
        """Загрузка настроек из переменных окружения"""
        test_env = {
            "TELEGRAM_BOT_TOKEN": "test_bot_token",
            "TELEGRAM_WEBHOOK_SECRET": "test_webhook_secret",
            "TUNA_TOKEN": "test_tuna_token",
            "TUNA_API_TOKEN": "test_tuna_api_token",
            "VISUAL_CROSSING_KEY": "test_visual_key",
            "WEATHER_API_KEY": "test_weather_key",
            "OPEN_WEATHER_MAP_API_KEY": "test_owm_key",
        }

        with patch.dict("os.environ", test_env, clear=True):
            # Мокаем чтение .env файла
            with patch(
                "pydantic_settings.sources.DotEnvSettingsSource.__call__",
                return_value={},
            ):
                settings = SettingsSchema()

                assert settings.TELEGRAM_BOT_TOKEN == "test_bot_token"
                assert settings.TELEGRAM_WEBHOOK_SECRET == "test_webhook_secret"
                assert settings.TUNA_TOKEN == "test_tuna_token"
                assert settings.TUNA_API_TOKEN == "test_tuna_api_token"
                assert settings.VISUAL_CROSSING_KEY == "test_visual_key"
                assert settings.WEATHER_API_KEY == "test_weather_key"
                assert settings.OPEN_WEATHER_MAP_API_KEY == "test_owm_key"

    def test_missing_required_field_raises_error(self):
        """Отсутствие обязательного поля вызывает ошибку"""
        incomplete_env = {
            # Намеренно пропускаем TELEGRAM_BOT_TOKEN
            "TELEGRAM_WEBHOOK_SECRET": "test_secret",
            "TUNA_TOKEN": "test_token",
            "TUNA_API_TOKEN": "test_api_token",
            "VISUAL_CROSSING_KEY": "test_key",
            "WEATHER_API_KEY": "test_key",
            "OPEN_WEATHER_MAP_API_KEY": "test_key",
        }

        from pydantic import ValidationError

        with patch.dict("os.environ", incomplete_env, clear=True):
            # Блокируем чтение .env файла
            with patch(
                "pydantic_settings.sources.DotEnvSettingsSource.__call__",
                return_value={},
            ):
                with pytest.raises(ValidationError) as exc_info:
                    SettingsSchema()

                # Проверяем что ошибка именно по полю TELEGRAM_BOT_TOKEN
                assert "TELEGRAM_BOT_TOKEN" in str(exc_info.value)


class TestSettingsValidation:
    """Тесты валидации настроек"""

    def test_empty_string_tokens_valid(self):
        """Пустые строки валидны"""
        empty_env = {
            "TELEGRAM_BOT_TOKEN": "",
            "TELEGRAM_WEBHOOK_SECRET": "",
            "TUNA_TOKEN": "",
            "TUNA_API_TOKEN": "",
            "VISUAL_CROSSING_KEY": "",
            "WEATHER_API_KEY": "",
            "OPEN_WEATHER_MAP_API_KEY": "",
        }

        with patch.dict("os.environ", empty_env, clear=True):
            with patch(
                "pydantic_settings.sources.DotEnvSettingsSource.__call__",
                return_value={},
            ):
                settings = SettingsSchema()

                assert settings.TELEGRAM_BOT_TOKEN == ""
                assert settings.TUNA_TOKEN == ""

    def test_special_characters_in_tokens(self):
        """Специальные символы в токенах"""
        special_token = "token!@#$%^&*()_+-={}[]|:;<>,.?/"

        test_env = {
            "TELEGRAM_BOT_TOKEN": special_token,
            "TELEGRAM_WEBHOOK_SECRET": special_token,
            "TUNA_TOKEN": special_token,
            "TUNA_API_TOKEN": special_token,
            "VISUAL_CROSSING_KEY": special_token,
            "WEATHER_API_KEY": special_token,
            "OPEN_WEATHER_MAP_API_KEY": special_token,
        }

        with patch.dict("os.environ", test_env, clear=True):
            with patch(
                "pydantic_settings.sources.DotEnvSettingsSource.__call__",
                return_value={},
            ):
                settings = SettingsSchema()

                assert settings.TELEGRAM_BOT_TOKEN == special_token

    def test_very_long_tokens(self):
        """Очень длинные токены"""
        long_token = "a" * 10000

        test_env = {
            "TELEGRAM_BOT_TOKEN": long_token,
            "TELEGRAM_WEBHOOK_SECRET": long_token,
            "TUNA_TOKEN": long_token,
            "TUNA_API_TOKEN": long_token,
            "VISUAL_CROSSING_KEY": long_token,
            "WEATHER_API_KEY": long_token,
            "OPEN_WEATHER_MAP_API_KEY": long_token,
        }

        with patch.dict("os.environ", test_env, clear=True):
            with patch(
                "pydantic_settings.sources.DotEnvSettingsSource.__call__",
                return_value={},
            ):
                settings = SettingsSchema()

                assert len(settings.TELEGRAM_BOT_TOKEN) == 10000


class TestSettingsInstance:
    """Тесты глобального экземпляра settings"""

    def test_settings_instance_exists(self):
        """Глобальный экземпляр settings существует"""
        from common.utils.config import settings

        assert settings is not None
        assert isinstance(settings, SettingsSchema)

    def test_settings_has_all_fields(self):
        """У settings есть все поля"""
        from common.utils.config import settings

        assert hasattr(settings, "TELEGRAM_BOT_TOKEN")
        assert hasattr(settings, "TELEGRAM_WEBHOOK_SECRET")
        assert hasattr(settings, "TUNA_TOKEN")
        assert hasattr(settings, "TUNA_API_TOKEN")
        assert hasattr(settings, "VISUAL_CROSSING_KEY")
        assert hasattr(settings, "WEATHER_API_KEY")
        assert hasattr(settings, "OPEN_WEATHER_MAP_API_KEY")

    def test_settings_values_are_strings(self):
        """Все значения settings - строки"""
        from common.utils.config import settings

        assert isinstance(settings.TELEGRAM_BOT_TOKEN, str)
        assert isinstance(settings.TELEGRAM_WEBHOOK_SECRET, str)
        assert isinstance(settings.TUNA_TOKEN, str)


class TestSettingsReload:
    """Тесты перезагрузки настроек"""

    def test_create_new_instance_with_different_env(self):
        """Новый экземпляр с другими переменными"""
        # Первый экземпляр
        env1 = {
            "TELEGRAM_BOT_TOKEN": "token1",
            "TELEGRAM_WEBHOOK_SECRET": "secret1",
            "TUNA_TOKEN": "tuna1",
            "TUNA_API_TOKEN": "api1",
            "VISUAL_CROSSING_KEY": "key1",
            "WEATHER_API_KEY": "key1",
            "OPEN_WEATHER_MAP_API_KEY": "key1",
        }

        with patch.dict("os.environ", env1, clear=True):
            with patch(
                "pydantic_settings.sources.DotEnvSettingsSource.__call__",
                return_value={},
            ):
                settings1 = SettingsSchema()
                assert settings1.TELEGRAM_BOT_TOKEN == "token1"

        # Второй экземпляр с другими значениями
        env2 = {
            "TELEGRAM_BOT_TOKEN": "token2",
            "TELEGRAM_WEBHOOK_SECRET": "secret2",
            "TUNA_TOKEN": "tuna2",
            "TUNA_API_TOKEN": "api2",
            "VISUAL_CROSSING_KEY": "key2",
            "WEATHER_API_KEY": "key2",
            "OPEN_WEATHER_MAP_API_KEY": "key2",
        }

        with patch.dict("os.environ", env2, clear=True):
            with patch(
                "pydantic_settings.sources.DotEnvSettingsSource.__call__",
                return_value={},
            ):
                settings2 = SettingsSchema()
                assert settings2.TELEGRAM_BOT_TOKEN == "token2"


class TestEdgeCases:
    """Граничные случаи"""

    def test_whitespace_in_tokens(self):
        """Пробелы в токенах сохраняются"""
        test_env = {
            "TELEGRAM_BOT_TOKEN": "  token with spaces  ",
            "TELEGRAM_WEBHOOK_SECRET": "secret",
            "TUNA_TOKEN": "token",
            "TUNA_API_TOKEN": "api",
            "VISUAL_CROSSING_KEY": "key",
            "WEATHER_API_KEY": "key",
            "OPEN_WEATHER_MAP_API_KEY": "key",
        }

        with patch.dict("os.environ", test_env, clear=True):
            with patch(
                "pydantic_settings.sources.DotEnvSettingsSource.__call__",
                return_value={},
            ):
                settings = SettingsSchema()

                assert settings.TELEGRAM_BOT_TOKEN == "  token with spaces  "

    def test_numeric_string_tokens(self):
        """Числовые строки как токены"""
        test_env = {
            "TELEGRAM_BOT_TOKEN": "123456789",
            "TELEGRAM_WEBHOOK_SECRET": "987654321",
            "TUNA_TOKEN": "111222333",
            "TUNA_API_TOKEN": "444555666",
            "VISUAL_CROSSING_KEY": "777888999",
            "WEATHER_API_KEY": "000111222",
            "OPEN_WEATHER_MAP_API_KEY": "333444555",
        }

        with patch.dict("os.environ", test_env, clear=True):
            with patch(
                "pydantic_settings.sources.DotEnvSettingsSource.__call__",
                return_value={},
            ):
                settings = SettingsSchema()

                assert settings.TELEGRAM_BOT_TOKEN == "123456789"
                assert isinstance(settings.TELEGRAM_BOT_TOKEN, str)

    def test_unicode_in_tokens(self):
        """Unicode символы в токенах"""
        test_env = {
            "TELEGRAM_BOT_TOKEN": "токен_кириллица_🔑",
            "TELEGRAM_WEBHOOK_SECRET": "секрет",
            "TUNA_TOKEN": "token",
            "TUNA_API_TOKEN": "api",
            "VISUAL_CROSSING_KEY": "key",
            "WEATHER_API_KEY": "key",
            "OPEN_WEATHER_MAP_API_KEY": "key",
        }

        with patch.dict("os.environ", test_env, clear=True):
            with patch(
                "pydantic_settings.sources.DotEnvSettingsSource.__call__",
                return_value={},
            ):
                settings = SettingsSchema()

                assert "кириллица" in settings.TELEGRAM_BOT_TOKEN
                assert "🔑" in settings.TELEGRAM_BOT_TOKEN


class TestModelDump:
    """Тесты для метода model_dump"""

    def test_model_dump_returns_dict(self):
        """model_dump возвращает словарь"""
        test_env = {
            "TELEGRAM_BOT_TOKEN": "token",
            "TELEGRAM_WEBHOOK_SECRET": "secret",
            "TUNA_TOKEN": "tuna",
            "TUNA_API_TOKEN": "api",
            "VISUAL_CROSSING_KEY": "key",
            "WEATHER_API_KEY": "key",
            "OPEN_WEATHER_MAP_API_KEY": "key",
        }

        with patch.dict("os.environ", test_env, clear=True):
            with patch(
                "pydantic_settings.sources.DotEnvSettingsSource.__call__",
                return_value={},
            ):
                settings = SettingsSchema()
                dumped = settings.model_dump()

                assert isinstance(dumped, dict)
                assert "TELEGRAM_BOT_TOKEN" in dumped
                assert dumped["TELEGRAM_BOT_TOKEN"] == "token"

    def test_model_dump_exclude_secrets(self):
        """Исключение секретов из дампа"""
        test_env = {
            "TELEGRAM_BOT_TOKEN": "secret_token",
            "TELEGRAM_WEBHOOK_SECRET": "secret",
            "TUNA_TOKEN": "tuna",
            "TUNA_API_TOKEN": "api",
            "VISUAL_CROSSING_KEY": "key",
            "WEATHER_API_KEY": "key",
            "OPEN_WEATHER_MAP_API_KEY": "key",
        }

        with patch.dict("os.environ", test_env, clear=True):
            with patch(
                "pydantic_settings.sources.DotEnvSettingsSource.__call__",
                return_value={},
            ):
                settings = SettingsSchema()
                dumped = settings.model_dump(
                    exclude={"TELEGRAM_BOT_TOKEN", "TUNA_TOKEN"}
                )

                assert "TELEGRAM_BOT_TOKEN" not in dumped
                assert "TUNA_TOKEN" not in dumped
                assert "WEATHER_API_KEY" in dumped
