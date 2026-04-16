from fastapi import APIRouter

from api.schemas import DefaultSchema

router = APIRouter()


@router.get("/", response_model=DefaultSchema)
def default_response() -> dict:
    if router:
        return {
            "api_status": True,
            "hi_message": "Hi Api User!!!",
        }

    return {
        "api_status": False,
        "hi_message": "Api Was Closed(((",
    }
