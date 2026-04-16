"""Unit тестирование синхронного модуля auto_tuna_tunnel.py."""

import subprocess
import json

import pytest
from unittest.mock import Mock, patch, MagicMock

from bot.src.utils import save_tuna_token, check_tuna_auth, start_tuna


# ============= save_tuna_token =============
class TestSaveTunaToken:
    """Тесты для функции save_tuna_token"""

    def test_success_with_valid_token(self, mock_valid_token, mock_successful_run):
        """Успешное сохранение валидного токена"""
        result = save_tuna_token()

        assert result is True
        mock_successful_run.assert_called_once_with(
            ["tuna", "config", "save-token", "valid_test_token_12345"],
            capture_output=True,
            text=True,
            timeout=10,
        )

    def test_empty_token_returns_false(self, mock_empty_token, mock_subprocess_run):
        """Пустой токен возвращает False без вызова команды"""
        result = save_tuna_token()

        assert result is False
        mock_subprocess_run.assert_not_called()

    def test_none_token_returns_false(self, mock_subprocess_run):
        """None токен возвращает False"""
        with patch("src.utils.auto_tuna_tunnel.settings") as mock_settings:
            mock_settings.TUNA_TOKEN = None

            result = save_tuna_token()

            assert result is False
            mock_subprocess_run.assert_not_called()

    def test_command_failure_returns_false(self, mock_valid_token, mock_failed_run):
        """Неудачное выполнение команды возвращает False"""
        result = save_tuna_token()

        assert result is False

    def test_timeout_returns_false(self, mock_valid_token, mock_subprocess_run):
        """Таймаут команды возвращает False"""
        mock_subprocess_run.side_effect = subprocess.TimeoutExpired(
            cmd="tuna", timeout=10
        )

        result = save_tuna_token()

        assert result is False

    def test_unexpected_exception_returns_false(
        self, mock_valid_token, mock_subprocess_run
    ):
        """Неожиданное исключение возвращает False"""
        mock_subprocess_run.side_effect = Exception("Unexpected error")

        result = save_tuna_token()

        assert result is False

    @pytest.mark.parametrize(
        "returncode,expected",
        [
            (0, True),
            (1, False),
            (127, False),
            (255, False),
        ],
    )
    def test_various_return_codes(
        self, mock_valid_token, mock_subprocess_run, returncode, expected
    ):
        """Различные коды возврата команды"""
        mock_subprocess_run.return_value = Mock(
            returncode=returncode, stdout="", stderr=""
        )

        result = save_tuna_token()

        assert result == expected

    def test_token_with_special_characters(self, mock_subprocess_run):
        """Токен со спецсимволами"""
        with patch("src.utils.auto_tuna_tunnel.settings") as mock_settings:
            mock_settings.TUNA_TOKEN = "token!@#$%^&*()"
            mock_subprocess_run.return_value = Mock(returncode=0, stdout="", stderr="")

            result = save_tuna_token()

            assert result is True

    def test_very_long_token(self, mock_subprocess_run):
        """Очень длинный токен"""
        with patch("src.utils.auto_tuna_tunnel.settings") as mock_settings:
            mock_settings.TUNA_TOKEN = "a" * 1000
            mock_subprocess_run.return_value = Mock(returncode=0, stdout="", stderr="")

            result = save_tuna_token()

            assert result is True


# ============= check_tuna_auth =============


class TestCheckTunaAuth:
    """Тесты для функции check_tuna_auth"""

    def test_authenticated_with_forwarding_message(self, mock_auth_success_popen):
        """Авторизация успешна при сообщении Forwarding"""
        result = check_tuna_auth()

        assert result is True
        mock_auth_success_popen.return_value.terminate.assert_called_once()

    def test_authenticated_with_account_message(
        self, mock_subprocess_popen, tuna_json_output
    ):
        """Авторизация успешна при сообщении Account"""
        mock_process = MagicMock()
        mock_process.stdout = tuna_json_output(
            [("info", "Account: test@example.com", None)]
        )
        mock_subprocess_popen.return_value = mock_process

        result = check_tuna_auth()

        assert result is True

    def test_not_authenticated_with_unknown_token(self, mock_auth_failed_popen):
        """Не авторизован при ошибке Unknown token"""
        result = check_tuna_auth()

        assert result is False

    def test_not_authenticated_with_must_be_specified(
        self, mock_subprocess_popen, tuna_json_output
    ):
        """Не авторизован при ошибке must be specified"""
        mock_process = MagicMock()
        mock_process.stdout = tuna_json_output(
            [("error", "Token must be specified", None)]
        )
        mock_subprocess_popen.return_value = mock_process

        result = check_tuna_auth()

        assert result is False

    def test_not_authenticated_with_authorization_required(
        self, mock_subprocess_popen, tuna_json_output
    ):
        """Не авторизован при ошибке AuthorizationRequired"""
        mock_process = MagicMock()
        mock_process.stdout = tuna_json_output(
            [("fatal", "AuthorizationRequired", None)]
        )
        mock_subprocess_popen.return_value = mock_process

        result = check_tuna_auth()

        assert result is False

    def test_timeout_returns_false(self, mock_subprocess_popen):
        """Таймаут возвращает False"""
        mock_process = MagicMock()
        mock_process.stdout = [
            json.dumps({"level": "debug", "msg": "Some message"}) for _ in range(100)
        ]
        mock_subprocess_popen.return_value = mock_process

        result = check_tuna_auth()

        assert result is False

    def test_invalid_json_returns_false(self, mock_subprocess_popen):
        """Невалидный JSON возвращает False"""
        mock_process = MagicMock()
        mock_process.stdout = [
            "This is not JSON",
            "{invalid json}",
            "Another invalid line",
        ]
        mock_subprocess_popen.return_value = mock_process

        result = check_tuna_auth()

        assert result is False

    def test_mixed_valid_and_invalid_json(self, mock_subprocess_popen):
        """Смешанный валидный и невалидный JSON"""
        mock_process = MagicMock()
        mock_process.stdout = [
            "Invalid line",
            json.dumps({"level": "info", "msg": "Starting"}),
            "{bad json}",
            json.dumps(
                {"level": "info", "msg": "Forwarding", "url": "https://test.tuna.am"}
            ),
        ]
        mock_subprocess_popen.return_value = mock_process

        result = check_tuna_auth()

        assert result is True

    def test_empty_stdout(self, mock_subprocess_popen):
        """Пустой stdout возвращает False"""
        mock_process = MagicMock()
        mock_process.stdout = []
        mock_subprocess_popen.return_value = mock_process

        result = check_tuna_auth()

        assert result is False

    def test_only_whitespace_lines(self, mock_subprocess_popen):
        """Только пустые строки возвращает False"""
        mock_process = MagicMock()
        mock_process.stdout = ["", "  ", "\n", "\t"]
        mock_subprocess_popen.return_value = mock_process

        result = check_tuna_auth()

        assert result is False

    def test_process_terminates_on_success(
        self, mock_subprocess_popen, tuna_json_output
    ):
        """Процесс завершается при успешной авторизации"""
        mock_process = MagicMock()
        mock_process.stdout = tuna_json_output(
            [("info", "Forwarding", "https://test.tuna.am")]
        )
        mock_subprocess_popen.return_value = mock_process

        check_tuna_auth()

        mock_process.terminate.assert_called_once()

    def test_process_terminates_on_failure(
        self, mock_subprocess_popen, tuna_json_output
    ):
        """Процесс завершается при неудачной авторизации"""
        mock_process = MagicMock()
        mock_process.stdout = tuna_json_output([("error", "Unknown token", None)])
        mock_subprocess_popen.return_value = mock_process

        check_tuna_auth()

        mock_process.terminate.assert_called_once()

    @pytest.mark.parametrize(
        "error_msg",
        [
            "Unknown token",
            "must be specified",
            "AuthorizationRequired",
            "Token must be specified",
            "Invalid credentials",
        ],
    )
    def test_various_auth_error_messages(
        self, mock_subprocess_popen, tuna_json_output, error_msg
    ):
        """Различные сообщения об ошибках авторизации"""
        mock_process = MagicMock()
        mock_process.stdout = tuna_json_output([("error", error_msg, None)])
        mock_subprocess_popen.return_value = mock_process

        result = check_tuna_auth()

        assert result is False

    @pytest.mark.parametrize(
        "success_msg,url",
        [
            ("Forwarding", "https://test.tuna.am"),
            ("Account: user@test.com", None),
            ("Account: another@example.com", None),
        ],
    )
    def test_various_success_messages(
        self, mock_subprocess_popen, tuna_json_output, success_msg, url
    ):
        """Различные сообщения об успешной авторизации"""
        mock_process = MagicMock()
        mock_process.stdout = tuna_json_output([("info", success_msg, url)])
        mock_subprocess_popen.return_value = mock_process

        result = check_tuna_auth()

        assert result is True


# ============= start_tuna =============


class TestStartTuna:
    """Тесты для функции start_tuna"""

    def test_successful_tunnel_start(self, mock_subprocess_popen):
        """Успешный запуск туннеля"""
        with (
            patch("src.utils.auto_tuna_tunnel.save_tuna_token", return_value=True),
            patch("src.utils.auto_tuna_tunnel.check_tuna_auth", return_value=True),
        ):
            mock_process = MagicMock()
            mock_process.stdout = [
                json.dumps(
                    {
                        "level": "info",
                        "msg": "Forwarding",
                        "url": "https://test123.tuna.am",
                    }
                )
            ]
            mock_subprocess_popen.return_value = mock_process

            url, process = start_tuna(port=8080)

            assert url == "https://test123.tuna.am"
            assert process == mock_process
            mock_subprocess_popen.assert_called_once_with(
                ["tuna", "http", "8080", "--log-format", "json", "--log", "stdout"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
            )

    def test_token_save_failure_raises_error(self):
        """Ошибка сохранения токена вызывает RuntimeError"""
        with patch("src.utils.auto_tuna_tunnel.save_tuna_token", return_value=False):
            with pytest.raises(RuntimeError, match="Failed to save Tuna token"):
                start_tuna(port=8080)

    def test_auth_failure_raises_error(self):
        """Ошибка авторизации вызывает RuntimeError"""
        with (
            patch("src.utils.auto_tuna_tunnel.save_tuna_token", return_value=True),
            patch("src.utils.auto_tuna_tunnel.check_tuna_auth", return_value=False),
        ):
            with pytest.raises(RuntimeError, match="authentication failed"):
                start_tuna(port=8080)

    def test_timeout_raises_error(self, mock_subprocess_popen):
        """Таймаут получения URL вызывает RuntimeError"""
        with (
            patch("src.utils.auto_tuna_tunnel.save_tuna_token", return_value=True),
            patch("src.utils.auto_tuna_tunnel.check_tuna_auth", return_value=True),
            patch("time.time") as mock_time,
        ):
            mock_process = MagicMock()
            mock_process.stdout = [
                json.dumps({"level": "info", "msg": "Starting"}),
                json.dumps({"level": "debug", "msg": "Connecting"}),
            ]
            mock_subprocess_popen.return_value = mock_process

            start_time = 1000.0
            mock_time.side_effect = [
                start_time,
                start_time + 0.1,
                start_time + 2.0,
            ]

            with pytest.raises(RuntimeError, match="timeout"):
                start_tuna(port=8080, timeout=1)

    def test_auth_error_during_startup_raises_error(self, mock_subprocess_popen):
        """Ошибка авторизации во время запуска вызывает RuntimeError"""
        with (
            patch("src.utils.auto_tuna_tunnel.save_tuna_token", return_value=True),
            patch("src.utils.auto_tuna_tunnel.check_tuna_auth", return_value=True),
        ):
            mock_process = MagicMock()
            mock_process.stdout = [
                json.dumps(
                    {"level": "fatal", "msg": "Unknown token - check credentials"}
                )
            ]
            mock_subprocess_popen.return_value = mock_process

            with pytest.raises(RuntimeError, match="authentication error"):
                start_tuna(port=8080)

    def test_missing_url_in_forwarding_message_raises_error(
        self, mock_subprocess_popen
    ):
        """Отсутствие URL в сообщении Forwarding вызывает RuntimeError"""
        with (
            patch("src.utils.auto_tuna_tunnel.save_tuna_token", return_value=True),
            patch("src.utils.auto_tuna_tunnel.check_tuna_auth", return_value=True),
        ):
            mock_process = MagicMock()
            mock_process.stdout = [json.dumps({"level": "info", "msg": "Forwarding"})]
            mock_subprocess_popen.return_value = mock_process

            with pytest.raises(RuntimeError, match="публичный URL"):
                start_tuna(port=8080, timeout=1)

    def test_invalid_json_during_startup(self, mock_subprocess_popen):
        """Невалидный JSON во время запуска игнорируется"""
        with (
            patch("src.utils.auto_tuna_tunnel.save_tuna_token", return_value=True),
            patch("src.utils.auto_tuna_tunnel.check_tuna_auth", return_value=True),
        ):
            mock_process = MagicMock()
            mock_process.stdout = [
                "Invalid JSON line",
                json.dumps(
                    {
                        "level": "info",
                        "msg": "Forwarding",
                        "url": "https://test.tuna.am",
                    }
                ),
            ]
            mock_subprocess_popen.return_value = mock_process

            url, process = start_tuna(port=8080)

            assert url == "https://test.tuna.am"

    def test_custom_port(self, mock_subprocess_popen):
        """Кастомный порт передаётся корректно"""
        with (
            patch("src.utils.auto_tuna_tunnel.save_tuna_token", return_value=True),
            patch("src.utils.auto_tuna_tunnel.check_tuna_auth", return_value=True),
        ):
            mock_process = MagicMock()
            mock_process.stdout = [
                json.dumps(
                    {
                        "level": "info",
                        "msg": "Forwarding",
                        "url": "https://test.tuna.am",
                    }
                )
            ]
            mock_subprocess_popen.return_value = mock_process

            start_tuna(port=9999)

            mock_subprocess_popen.assert_called_once()
            call_args = mock_subprocess_popen.call_args[0][0]
            assert "9999" in call_args

    def test_custom_timeout(self, mock_subprocess_popen):
        """Кастомный таймаут работает"""
        with (
            patch("src.utils.auto_tuna_tunnel.save_tuna_token", return_value=True),
            patch("src.utils.auto_tuna_tunnel.check_tuna_auth", return_value=True),
            patch("time.time") as mock_time,
        ):
            mock_process = MagicMock()
            mock_process.stdout = [
                json.dumps({"level": "info", "msg": "Starting"}) for _ in range(10)
            ]
            mock_subprocess_popen.return_value = mock_process

            start_time = 1000.0
            mock_time.side_effect = [
                start_time,
                start_time + 0.1,
                start_time + 0.2,
                start_time + 3.0,
            ]

            with pytest.raises(RuntimeError, match="timeout"):
                start_tuna(port=8080, timeout=2)

    def test_actual_timeout_with_time_mock(self, mock_subprocess_popen):
        """Реальный таймаут с моком времени"""
        with (
            patch("src.utils.auto_tuna_tunnel.save_tuna_token", return_value=True),
            patch("src.utils.auto_tuna_tunnel.check_tuna_auth", return_value=True),
            patch("time.time") as mock_time,
        ):
            mock_process = MagicMock()

            def generate_lines():
                for i in range(5):
                    yield json.dumps({"level": "info", "msg": f"Message {i}"})

            mock_process.stdout = generate_lines()
            mock_subprocess_popen.return_value = mock_process

            start_time = 1000.0
            mock_time.side_effect = [
                start_time,
                start_time + 0.5,
                start_time + 1.5,
                start_time + 35.0,
            ]

            with pytest.raises(RuntimeError, match="timeout"):
                start_tuna(port=8080, timeout=30)

    def test_no_url_received_raises_error(self, mock_subprocess_popen):
        """Не получен URL - RuntimeError"""
        with (
            patch("src.utils.auto_tuna_tunnel.save_tuna_token", return_value=True),
            patch("src.utils.auto_tuna_tunnel.check_tuna_auth", return_value=True),
        ):
            mock_process = MagicMock()
            mock_process.stdout = [
                json.dumps({"level": "info", "msg": "Starting"}),
                json.dumps({"level": "debug", "msg": "Connecting"}),
            ]
            mock_subprocess_popen.return_value = mock_process

            with pytest.raises(RuntimeError, match="публичный URL"):
                start_tuna(port=8080, timeout=1)

    def test_process_not_created_raises_error(self):
        """Ошибка создания процесса вызывает RuntimeError"""
        with (
            patch("src.utils.auto_tuna_tunnel.save_tuna_token", return_value=True),
            patch("src.utils.auto_tuna_tunnel.check_tuna_auth", return_value=True),
            patch("subprocess.Popen", return_value=None),
        ):
            with pytest.raises(RuntimeError, match="Failed to create Tuna process"):
                start_tuna(port=8080)

    @pytest.mark.parametrize("port", [80, 443, 3000, 8000, 8080, 9000])
    def test_various_ports(self, mock_subprocess_popen, port):
        """Различные порты"""
        with (
            patch("src.utils.auto_tuna_tunnel.save_tuna_token", return_value=True),
            patch("src.utils.auto_tuna_tunnel.check_tuna_auth", return_value=True),
        ):
            mock_process = MagicMock()
            mock_process.stdout = [
                json.dumps(
                    {
                        "level": "info",
                        "msg": "Forwarding",
                        "url": f"https://test-{port}.tuna.am",
                    }
                )
            ]
            mock_subprocess_popen.return_value = mock_process

            url, process = start_tuna(port=port)

            assert str(port) in mock_subprocess_popen.call_args[0][0]
            assert f"test-{port}" in url

    def test_multiple_messages_before_forwarding(self, mock_subprocess_popen):
        """Несколько сообщений перед Forwarding обрабатываются корректно"""
        with (
            patch("src.utils.auto_tuna_tunnel.save_tuna_token", return_value=True),
            patch("src.utils.auto_tuna_tunnel.check_tuna_auth", return_value=True),
        ):
            mock_process = MagicMock()
            mock_process.stdout = [
                json.dumps({"level": "info", "msg": "Starting tunnel"}),
                json.dumps({"level": "debug", "msg": "Connecting to server"}),
                json.dumps({"level": "info", "msg": "Connection established"}),
                json.dumps(
                    {
                        "level": "info",
                        "msg": "Forwarding",
                        "url": "https://test.tuna.am",
                    }
                ),
            ]
            mock_subprocess_popen.return_value = mock_process

            url, process = start_tuna(port=8080)

            assert url == "https://test.tuna.am"
