from datetime import datetime

from pydantic import BaseModel, ConfigDict


class UserBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    tg_id: int
    first_name: str
    last_name: str | None = None
    username: str | None = None
    language_code: str | None = None
    is_premium: bool = False
    photo_url: str | None = None
    created_at: datetime
    updated_at: datetime
