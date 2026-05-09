from fastapi import Depends, APIRouter, HTTPException, status

from api.schemas import (
    UserSchema,
    UserLocation,
    UserCreate,
    ActionStatus,
    UpdateStatus,
)

from api.dependencies import get_weather_repo

from common.core import get_logger

router = APIRouter(prefix="/weather", tags=["weather"])
_lg = get_logger()


# ? GET
@router.get("/cache/{weather_id}", response_model=str)
async def wnm_by_id(
    weather_id: str,
    repo: dict = Depends(get_weather_repo),
):
    wn = await repo.get_by_id(weather_id)

    if wn is None:
        _lg.warning(f"Weather with id {weather_id} Not Found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Weather with id {weather_id} Not Found",
        )

    return wn["weather_now_msg"]


@router.get("/cache/exists/{weather_id}", response_model=bool)
async def is_exists(
    weather_id: str,
    repo: dict = Depends(get_weather_repo),
):
    return await repo.exists(weather_id)


# ! DELETE
@router.delete("/cache/{weather_id}", response_model=ActionStatus)
async def delete_one(
    weather_id: str,
    repo: dict = Depends(get_weather_repo),
):
    deleted, msg = await repo.delete(weather_id)
    return ActionStatus(success=deleted, detail=msg)
