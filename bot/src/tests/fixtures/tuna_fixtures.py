"""Фикстуры для тестирования auto_tunnel_tunnel.py"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import json


@pytest.fixture
def mock_valid_token():
    """Мок валидного токена в settings"""
    with patch("src.utils.auto_tuna_tunnel.settings") as mock_settings:
        mock_settings.TUNA_TOKEN = "valid_test_token_12345"
        yield mock_settings


@pytest.fixture
def mock_empty_token():
    """Мок пустого токена"""
    with patch("src.utils.auto_tuna_tunnel.settings") as mock_settings:
        mock_settings.TUNA_TOKEN = ""
        yield mock_settings


@pytest.fixture
def mock_subprocess_run():
    """Мок для subprocess.run"""
    with patch("subprocess.run") as mock:
        yield mock


@pytest.fixture
def mock_subprocess_popen():
    """Мок для subprocess.Popen"""
    with patch("subprocess.Popen") as mock:
        yield mock


@pytest.fixture
def mock_successful_run():
    """Мок успешного выполнения subprocess.run"""
    with patch("subprocess.run") as mock:
        mock.return_value = Mock(
            returncode=0, stdout="Token saved successfully", stderr=""
        )
        yield mock


@pytest.fixture
def mock_failed_run():
    """Мок неудачного выполнения subprocess.run"""
    with patch("subprocess.run") as mock:
        mock.return_value = Mock(returncode=1, stdout="", stderr="Error: Invalid token")
        yield mock


@pytest.fixture
def mock_auth_success_popen():
    """Мок успешной авторизации"""
    with patch("subprocess.Popen") as mock:
        mock_process = MagicMock()
        mock_process.stdout = [
            json.dumps(
                {"level": "info", "msg": "Forwarding", "url": "https://test.tuna.am"}
            ),
        ]
        mock.return_value = mock_process
        yield mock


@pytest.fixture
def mock_auth_failed_popen():
    """Мок неудачной авторизации"""
    with patch("subprocess.Popen") as mock:
        mock_process = MagicMock()
        mock_process.stdout = [
            json.dumps({"level": "error", "msg": "Unknown token"}),
        ]
        mock.return_value = mock_process
        yield mock


@pytest.fixture
def tuna_json_output():
    """Генератор JSON выводов Tuna для тестов"""

    def _generate(messages):
        """
        Args:
            messages: list of tuples (level, msg, url)

        Example:
            output = tuna_json_output([
                ("info", "Starting", None),
                ("info", "Forwarding", "https://test.tuna.am")
            ])
        """
        result = []
        for item in messages:
            level = item[0]
            msg = item[1]
            data = {"level": level, "msg": msg}

            if len(item) > 2 and item[2]:
                data["url"] = item[2]

            result.append(json.dumps(data))

        return result

    return _generate
