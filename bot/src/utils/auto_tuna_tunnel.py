import json
import subprocess
import time
from typing import Tuple

from bot.src.utils import settings
from bot.src.core import get_logger

_lg = get_logger()


def save_tuna_token() -> bool:
    """Save Tuna token using subprocess.run"""
    try:
        token = settings.TUNA_TOKEN

        if not token:
            _lg.error("TUNA_TOKEN is empty in settings")
            return False

        _lg.debug(f"Saving Tuna token (length: {len(token)} chars)...")

        result = subprocess.run(
            ["tuna", "config", "save-token", token],
            capture_output=True,
            text=True,
            timeout=10,
        )

        if result.returncode == 0:
            _lg.debug("✓ Tuna token saved successfully")
            if result.stdout:
                _lg.debug(f"stdout: {result.stdout}")
            return True
        else:
            _lg.error(f"✗ Failed to save Tuna token (exit code: {result.returncode})")
            if result.stderr:
                _lg.error(f"stderr: {result.stderr}")
            if result.stdout:
                _lg.error(f"stdout: {result.stdout}")
            return False

    except subprocess.TimeoutExpired:
        _lg.error("Timeout while saving Tuna token")
        return False
    except Exception as e:
        _lg.error(f"Error saving Tuna token: {e}")
        return False


def check_tuna_auth() -> bool:
    """Check if Tuna is authenticated"""
    try:
        _lg.debug("Checking Tuna authentication status...")

        # Пробуем запустить туннель на случайном порту
        process = subprocess.Popen(
            ["tuna", "http", "9999", "--log-format", "json", "--log", "stdout"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )

        is_authenticated = None
        timeout = 5
        start_time = time.time()

        if process.stdout:
            for line in process.stdout:
                if time.time() - start_time > timeout:
                    break

                line = line.strip()
                if not line:
                    continue

                try:
                    data = json.loads(line)
                    msg = data.get("msg", "")
                    level = data.get("level", "")

                    _lg.debug(f"Auth check: level={level}, msg={msg[:50]}...")

                    # Ошибка авторизации - НЕ авторизован
                    if (
                        "must be specified" in msg
                        or "Unknown token" in msg
                        or "AuthorizationRequired" in msg
                    ):
                        _lg.debug("Found auth error - NOT authenticated")
                        is_authenticated = False
                        break

                    # Нашли "Forwarding" или "Account:" - авторизован
                    if msg == "Forwarding" or msg.startswith("Account:"):
                        _lg.debug("Found success indicator - authenticated")
                        is_authenticated = True
                        break

                except json.JSONDecodeError:
                    continue

        process.terminate()
        try:
            process.wait(timeout=2)
        except subprocess.TimeoutExpired:
            process.kill()

        # Если не определили статус - считаем что не авторизован
        if is_authenticated is None:
            _lg.warning("Could not determine auth status, assuming NOT authenticated")
            is_authenticated = False

        _lg.debug(f"Tuna auth check result: {is_authenticated}")
        return is_authenticated

    except Exception as e:
        _lg.error(f"Error checking Tuna auth: {e}")
        return False


def start_tuna(port: int, timeout: int = 30) -> Tuple[str, subprocess.Popen]:
    """Start Tuna tunnel and extract public URL"""
    try:
        # ВСЕГДА сохраняем токен перед запуском
        _lg.debug("Ensuring Tuna token is saved...")
        if not save_tuna_token():
            raise RuntimeError("Failed to save Tuna token")

        time.sleep(1)

        # Проверяем что токен применился
        if not check_tuna_auth():
            _lg.error("Tuna still not authenticated after saving token")
            _lg.error("This might indicate an invalid token")
            raise RuntimeError("Tuna authentication failed - check your TUNA_TOKEN")

        _lg.info(f"✓ Tuna authenticated, starting tunnel on port {port}...")

        process = subprocess.Popen(
            ["tuna", "http", str(port), "--log-format", "json", "--log", "stdout"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )

        if not process:
            raise RuntimeError("Failed to create Tuna process")

        _lg.debug("Tuna process created successfully")

        public_url = None
        start_time = time.time()

        if process.stdout:
            for line in process.stdout:
                if time.time() - start_time > timeout:
                    _lg.error(f"Tuna timeout after {timeout} seconds")
                    process.terminate()
                    raise RuntimeError(f"Tuna startup timeout ({timeout}s)")

                line = line.strip()

                if not line:
                    continue

                _lg.debug(f"Tuna output: {line}")

                try:
                    data = json.loads(line)
                    level = data.get("level", "")
                    msg = data.get("msg", "")

                    if level == "fatal" and (
                        "Unknown token" in msg or "AuthorizationRequired" in msg
                    ):
                        _lg.error("Tuna authentication failed during tunnel startup")
                        _lg.error(f"Error: {msg}")
                        process.terminate()
                        raise RuntimeError("Tuna authentication error - invalid token")

                    # Ищем URL в сообщении Forwarding
                    if msg == "Forwarding" and "url" in data:
                        public_url = data["url"]
                        _lg.debug(f"✓ Found Tuna URL: {public_url}")
                        break

                except json.JSONDecodeError:
                    continue

        if not public_url:
            _lg.error("Failed to get public URL from Tuna")
            process.terminate()
            raise RuntimeError("Не удалось получить публичный URL от tuna")

        return public_url, process

    except Exception as e:
        _lg.critical(f"Failed to start Tuna: {e}", exc_info=True)
        raise
