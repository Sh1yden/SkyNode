from pydantic import BaseModel, ConfigDict


class BaseUserSchema(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )


class UserLocation(BaseModel):
    is_location: bool
    city: str | None
    latitude: str | None
    longitude: str | None


class UserSchema(BaseUserSchema):
    # SYSTEM
    user_id: int
    is_bot: bool
    is_premium: bool | None = None
    language_code: str | None = None
    supports_inline_queries: bool | None = None

    # NAME
    username: str | None = None
    first_name: str
    last_name: str | None = None

    # FOR LOCATION
    city: str | None = None
    latitude: str | None = None
    longitude: str | None = None


class UserCreate(BaseModel):
    user_id: int
    is_bot: bool
    first_name: str
    username: str | None = None


class ActionStatus(BaseUserSchema):
    success: bool
    detail: str


class UpdateStatus(ActionStatus):
    update_fields: dict | None = None
