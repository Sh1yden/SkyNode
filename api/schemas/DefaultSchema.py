from pydantic import BaseModel


class DefaultSchema(BaseModel):
    api_status: bool
    hi_message: str | None
