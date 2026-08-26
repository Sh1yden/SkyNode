from aiogram.types import FSInputFile

from common.core import get_logger

_lg = get_logger()

FILE_CACHE = {
    "SkyNode Welcome Message": "AgACAgIAAxkBAAIC-Gnvevb5m7PWdCU8qjLbq9kb2khSAALEGmsbwLt5S24Wm4Qd_vC_AQADAgADdwADOwQ",
    "SkyNode Help Message": "AgACAgIAAxkBAAIC-WnvevZ6wNVFOu12R_JEhcSKoEDjAALFGmsbwLt5S_Qvbun2euk_AQADAgADdwADOwQ",
}


async def send_photo_save(cache_key: str) -> str | FSInputFile:
    try:
        cache = FILE_CACHE[cache_key]
        _lg.debug(f"Good cache! Photo cache is: {cache}")
        return cache

    except Exception as e:
        _lg.error(f"Internal error: {e}")
        return FSInputFile(f"assets/images/messages/{cache_key}.png")
