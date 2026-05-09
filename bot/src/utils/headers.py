import sys
from pathlib import Path

if __name__ == "__main__":
    bot_dir = Path(__file__).parent.parent.parent
    sys.path.insert(0, str(bot_dir))

import random
from enum import Enum
from typing import Dict, List, Optional

from common.core import get_logger

_lg = get_logger()


class Browser(Enum):
    CHROME = "chrome"
    FIREFOX = "firefox"
    SAFARI = "safari"
    EDGE = "edge"


class Platform(Enum):
    WINDOWS = "windows"
    MACOS = "macos"
    LINUX = "linux"


class Language(Enum):
    RU = "ru-RU"
    EN_US = "en-US"
    EN_GB = "en-GB"
    DE = "de-DE"
    FR = "fr-FR"
    ES = "es-ES"
    ZH = "zh-CN"


DEFAULT_HEADERS_CONFIG = {
    Browser.CHROME: {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Cache-Control": "max-age=0",
    },
    Browser.FIREFOX: {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "TE": "trailers",
    },
    Browser.SAFARI: {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
    },
    Browser.EDGE: {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
    },
}

USER_AGENTS = {
    Browser.CHROME: {
        Platform.WINDOWS: "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        Platform.MACOS: "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        Platform.LINUX: "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    },
    Browser.FIREFOX: {
        Platform.WINDOWS: "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
        Platform.MACOS: "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0",
        Platform.LINUX: "Mozilla/5.0 (X11; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0",
    },
    Browser.SAFARI: {
        Platform.MACOS: "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
    },
    Browser.EDGE: {
        Platform.WINDOWS: "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
        Platform.MACOS: "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
    },
}

DEFAULT_USER_AGENT = USER_AGENTS[Browser.CHROME][Platform.WINDOWS]
DEFAULT_ACCEPT = "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
DEFAULT_ACCEPT_ENCODING = "gzip, deflate, br"
DEFAULT_ACCEPT_LANGUAGE = "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7"
DEFAULT_CONNECTION = "keep-alive"


async def get_user_agent(browser: Browser, platform: Platform) -> str:
    """Получить user agent для конкретного браузера и платформы"""
    try:
        return USER_AGENTS[browser][platform]
    except (KeyError, Exception) as e:
        _lg.error(f"Error getting user agent: {e}, using default")
        return DEFAULT_USER_AGENT


async def get_random_ua() -> str:
    """Получить случайный user agent"""
    try:
        browser = random.choice(list(Browser))
        available_platforms = list(USER_AGENTS[browser].keys())
        platform = random.choice(available_platforms)
        return USER_AGENTS[browser][platform]
    except Exception as e:
        _lg.error(f"Error getting random user agent: {e}, using default")
        return DEFAULT_USER_AGENT


async def get_accept_header(browser: Browser) -> str:
    """Генерация Accept header для браузера"""
    try:
        accepts = {
            Browser.CHROME: "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            Browser.FIREFOX: "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            Browser.SAFARI: "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            Browser.EDGE: "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        }
        return accepts.get(browser, DEFAULT_ACCEPT)
    except Exception as e:
        _lg.error(f"Error getting accept header: {e}, using default")
        return DEFAULT_ACCEPT


async def get_accept_encoding(browser: Browser) -> str:
    """Генерация Accept-Encoding header"""
    try:
        return "gzip, deflate, br"
    except Exception as e:
        _lg.error(f"Error getting accept encoding: {e}, using default")
        return DEFAULT_ACCEPT_ENCODING


async def get_accept_language(
    lang: Language = Language.RU, additional_langs: Optional[List[Language]] = None
) -> str:
    """Генерация Accept-Language header"""
    try:
        languages = [f"{lang.value};q=1.0"]

        if additional_langs:
            for i, additional in enumerate(additional_langs, start=2):
                quality = max(0.1, 1.0 - (i * 0.1))
                languages.append(f"{additional.value};q={quality:.1f}")
        else:
            languages.extend(
                ["ru;q=0.9", "en-US;q=0.8", "en;q=0.7", "de;q=0.6", "fr;q=0.5"]
            )

        return ", ".join(languages)
    except Exception as e:
        _lg.error(f"Error getting accept language: {e}, using default")
        return DEFAULT_ACCEPT_LANGUAGE


async def get_connection_header(keep_alive: bool = True) -> str:
    """Генерация Connection header"""
    try:
        return "keep-alive" if keep_alive else "close"
    except Exception as e:
        _lg.error(f"Error getting connection header: {e}, using default")
        return DEFAULT_CONNECTION


async def create_browser_headers(
    browser: Browser,
    platform: Platform,
    lang: Language = Language.RU,
    extra_headers: Optional[Dict[str, str]] = None,
) -> Dict[str, str]:
    """Создать полный набор headers для конкретного браузера и платформы"""
    try:
        headers = {
            "User-Agent": await get_user_agent(browser, platform),
            "Accept": await get_accept_header(browser),
            "Accept-Encoding": await get_accept_encoding(browser),
            "Accept-Language": await get_accept_language(lang),
            "Connection": await get_connection_header(keep_alive=True),
        }

        if browser in DEFAULT_HEADERS_CONFIG:
            browser_specific = DEFAULT_HEADERS_CONFIG[browser].copy()
            browser_specific.pop("Accept", None)
            browser_specific.pop("Accept-Encoding", None)
            browser_specific.pop("Connection", None)
            headers.update(browser_specific)

        if extra_headers:
            headers.update(extra_headers)

        return headers
    except Exception as e:
        _lg.error(f"Error creating browser headers: {e}, using minimal headers")
        return {
            "User-Agent": DEFAULT_USER_AGENT,
            "Accept": DEFAULT_ACCEPT,
            "Accept-Encoding": DEFAULT_ACCEPT_ENCODING,
            "Accept-Language": DEFAULT_ACCEPT_LANGUAGE,
            "Connection": DEFAULT_CONNECTION,
        }


async def create_random_headers(
    lang: Language = Language.RU, include_modern: bool = True
) -> Dict[str, str]:
    """Создать случайный набор headers"""
    try:
        browser = random.choice(list(Browser))
        available_platforms = list(USER_AGENTS[browser].keys())
        platform = random.choice(available_platforms)

        headers = await create_browser_headers(browser, platform, lang)

        if include_modern and browser in [Browser.CHROME, Browser.EDGE]:
            headers.update(
                {
                    "Sec-Ch-Ua": '"Not_A Brand";v="8", "Chromium";v="120"',
                    "Sec-Ch-Ua-Mobile": "?0",
                    "Sec-Ch-Ua-Platform": f'"{platform.value.capitalize()}"',
                }
            )

        return headers
    except Exception as e:
        _lg.error(f"Error creating random headers: {e}, using minimal headers")
        return {
            "User-Agent": DEFAULT_USER_AGENT,
            "Accept": DEFAULT_ACCEPT,
            "Accept-Encoding": DEFAULT_ACCEPT_ENCODING,
            "Accept-Language": DEFAULT_ACCEPT_LANGUAGE,
            "Connection": DEFAULT_CONNECTION,
        }


async def create_api_headers(
    content_type: str = "application/json", auth_token: Optional[str] = None
) -> Dict[str, str]:
    """Создать headers для API запросов"""
    try:
        headers = {
            "User-Agent": "ApiClient/1.0.0",
            "Accept": "application/json",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "en-US,en;q=0.9",
            "Connection": "keep-alive",
            "Content-Type": content_type,
            "Cache-Control": "no-cache",
        }

        if auth_token:
            headers["Authorization"] = f"Bearer {auth_token}"

        return headers
    except Exception as e:
        _lg.error(f"Error creating API headers: {e}, using minimal headers")
        return {
            "User-Agent": "ApiClient/1.0.0",
            "Accept": "application/json",
            "Content-Type": content_type,
        }


async def headers_factory(
    browser: Optional[Browser] = None,
    platform: Optional[Platform] = None,
    lang: Language = Language.RU,
    is_api: bool = False,
) -> Dict[str, str]:
    """Фабрика функций для создания headers"""
    try:
        if is_api:
            return await create_api_headers()

        if browser and platform:
            return await create_browser_headers(browser, platform, lang)

        return await create_random_headers(lang)
    except Exception as e:
        _lg.error(f"Error in headers factory: {e}, using minimal headers")
        return {
            "User-Agent": DEFAULT_USER_AGENT,
            "Accept": DEFAULT_ACCEPT,
            "Accept-Encoding": DEFAULT_ACCEPT_ENCODING,
            "Accept-Language": DEFAULT_ACCEPT_LANGUAGE,
            "Connection": DEFAULT_CONNECTION,
        }


if __name__ == "__main__":
    import asyncio

    async def main():
        from common.core import setup_logging
        from bot.src.utils import get_raw_link_api, get_soup, parse_data

        setup_logging(level="DEBUG")

        url = await get_raw_link_api(api_name="YandexParser")

        if url is None:
            return None

        url = url.replace("{lang}", "ru")

        _lg.debug(f"Url is - {url}")

        params = {
            "lat": 51.730848,
            "lon": 36.193015,
        }

        headers = await headers_factory(
            platform=Platform.WINDOWS,
            lang=Language.RU,
            is_api=False,
        )

        _lg.debug(f"Headers is - {headers}")

        par_data = await parse_data(
            url=url,
            params=params,
            headers=headers,
        )

        soup = await get_soup(par_data)

        _lg.debug(f"Par_data is - {par_data}")
        _lg.debug(f"Soup is - {soup}")

    asyncio.run(main())
