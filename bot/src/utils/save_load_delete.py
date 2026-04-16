import sys
from pathlib import Path

# Для прямого запуска файла
if __name__ == "__main__":
    # Добавляем bot/ в sys.path
    bot_dir = Path(__file__).parent.parent.parent
    sys.path.insert(0, str(bot_dir))

import asyncio
import json
from pathlib import Path
from typing import Any

import aiofiles

from bot.src.core import get_logger

_lg = get_logger()


async def load_from_file(file_path: Path | str, mode: str = "rt") -> Any | None:
    """Load data from JSON or your file and return its contents(universal)"""
    try:
        async with aiofiles.open(file_path, mode, encoding="utf-8") as f:
            content = await f.read()
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                # If not valid JSON, return as plain string
                return content
    except Exception as e:
        _lg.critical(f"Internal error: {e}.")
        return None


async def save_to_file(
    file_path: Path | str,
    var: Any,
    jsonl: bool = False,
    mode: str = "wt",
) -> None:
    """Save value to JSON or JSONL or your file(universal)"""
    try:
        if jsonl:
            async with aiofiles.open(file_path, "at", encoding="utf-8") as f:
                await f.write(json.dumps(var, ensure_ascii=False) + "\n")
        else:
            if isinstance(var, str):
                async with aiofiles.open(file_path, mode, encoding="utf-8") as f:
                    await f.write(var)
            else:
                async with aiofiles.open(file_path, mode, encoding="utf-8") as f:
                    await f.write(json.dumps(var, indent=2, ensure_ascii=False))
    except Exception as e:
        _lg.critical(f"Internal error: {e}.")


if __name__ == "__main__":

    async def main():
        from bot.src.core import setup_logging

        setup_logging(level="DEBUG")

        test1 = 42 + 42
        await save_to_file("test.txt", test1)

        test2 = await load_from_file("test.txt")
        _lg.debug(test2)

    asyncio.run(main())
