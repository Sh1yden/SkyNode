from fastapi import Request, HTTPException, status


# ==== Database ====
async def get_repos(request: Request):
    repos = getattr(request.app.state, "repos", None)
    if not repos:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Repositories not initialized",
        )
    return repos


async def get_user_repos(request: Request):
    repos = await get_repos(request)
    return repos["user_repo"]


async def get_weather_repo(request: Request):
    repos = await get_repos(request)
    return repos["weather_repo"]
