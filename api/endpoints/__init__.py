__all__ = ["router"]

from fastapi import APIRouter
from .default import router as default_router
from .user import router as user_router
from .weather import router as weather_router

router = APIRouter()

router.include_router(default_router)
router.include_router(user_router)
router.include_router(weather_router)
