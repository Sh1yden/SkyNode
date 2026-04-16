from fastapi import Depends, APIRouter, HTTPException, status

from api.schemas import (
    UserSchema,
    UserLocation,
    UserCreate,
    ActionStatus,
    UpdateStatus,
)
from api.dependencies import get_user_repos

from bot.src.core import get_logger


router = APIRouter(prefix="/users", tags=["users"])
_lg = get_logger()


# ? GET
@router.get("", response_model=list[int])
async def all_ids(
    limit: int | None = 100,
    offset: int | None = 0,
    repo: dict = Depends(get_user_repos),
):
    return await repo.get_all_user_ids(limit=limit, offset=offset)


@router.get("/exists/{user_id}", response_model=bool)
async def is_exist(
    user_id: int,
    repo: dict = Depends(get_user_repos),
):
    return await repo.exists(user_id)


@router.get("/{user_id}", response_model=UserSchema)
async def all_info(
    user_id: int,
    repo: dict = Depends(get_user_repos),
) -> dict:
    user_info = await repo.get_by_id(user_id)

    if user_info is None:
        _lg.warning(f"User with id {user_id} Not Found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} Not Found",
        )

    return user_info


@router.get("/location/{user_id}", response_model=UserLocation)
async def loc_info(
    user_id: int,
    repo: dict = Depends(get_user_repos),
):
    user_info = await repo.get_by_id(user_id)

    if user_info is None:
        _lg.warning(f"User with id {user_id} Not Found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} Not Found",
        )

    is_user_loc = bool(user_info["city"]) and (
        bool(user_info["latitude"]) and bool(user_info["longitude"])
    )

    return UserLocation(
        is_location=is_user_loc,
        city=user_info["city"],
        latitude=user_info["latitude"],
        longitude=user_info["longitude"],
    )


# * POST
@router.post(
    "/create_one",
    response_model=ActionStatus,
    status_code=status.HTTP_201_CREATED,
)
async def create_one(
    data: UserCreate,
    repo: dict = Depends(get_user_repos),
):
    created, msg = await repo.save(data.model_dump())
    return ActionStatus(success=created, detail=msg)


# ^ PUT
@router.put("/{user_id}", response_model=UpdateStatus)
async def update_some_data(
    user_id: int,
    data: dict,
    repo: dict = Depends(get_user_repos),
):
    data.pop("user_id", None)

    updated, msg, upd_fields = await repo.update(user_id, data)
    return UpdateStatus(success=updated, detail=msg, updated_fields=upd_fields)


# ! DELETE
@router.delete("/delete_one/{user_id}", response_model=ActionStatus)
async def delete_one(
    user_id: int,
    repo: dict = Depends(get_user_repos),
):
    deleted, msg = await repo.delete(user_id)
    return ActionStatus(success=deleted, detail=msg)
