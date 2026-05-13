"""
Pydantic-модели для Telegram initData.
Используются при парсинге и валидации того что пришло от миниапки.
"""

from pydantic import BaseModel


class TgUser(BaseModel):
    id: int
    first_name: str
    last_name: str | None = None
    username: str | None = None
    language_code: str | None = None
    is_premium: bool = False
    allows_write_to_pm: bool = False
    added_to_attachment_menu: bool = False
    photo_url: str | None = None


class InitData(BaseModel):
    user: TgUser
    query_id: str | None = None
    chat: str | None = None
    chat_type: str | None = None
    chat_instance: str | None = None
    start_param: str | None = None
    can_send_after: str | None = None
    auth_date: str | None = None
    hash: str | None = None
