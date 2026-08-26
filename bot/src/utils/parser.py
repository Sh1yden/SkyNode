import sys
from pathlib import Path

# Для прямого запуска файла
if __name__ == "__main__":
    # Добавляем bot/ в sys.path
    bot_dir = Path(__file__).parent.parent.parent
    sys.path.insert(0, str(bot_dir))

import asyncio

import aiohttp
from bs4 import BeautifulSoup

from common.core import get_logger

_lg = get_logger(__name__)


async def parse_data(
    url: str | dict,
    params: dict,
    headers: dict | None = None,
):
    async with aiohttp.ClientSession(
        timeout=aiohttp.ClientTimeout(total=10)
    ) as session:
        response = await session.get(
            url,  # type: ignore
            headers=headers,
            params=params,
        )
        response.raise_for_status()

        _lg.debug(f"Response is - {bool(await response.text())}")

        return await response.text()


async def get_soup(response):
    try:
        soup = BeautifulSoup(response, "html.parser")

        return soup

    except Exception as e:
        _lg.debug(f"Internal error: {e}")


if __name__ == "__main__":

    async def main():
        pass

    asyncio.run(main())
