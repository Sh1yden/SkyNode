__all__ = ["router"]

from aiogram import Router
from .message import router as message_router
from .callback import router as callback_router

from common.core import get_logger

_lg = get_logger()

router = Router()
router.include_routers(message_router, callback_router)

_lg.debug("User router initialized with message and callback sub-routers")
