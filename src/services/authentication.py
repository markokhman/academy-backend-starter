"""
FastAPI-зависимости для авторизации.

В роутах используй типы:
    user: Authentication   — TgUser, прошедший проверку initData
    InternalAuth           — для internal-эндпоинтов (push)

Если нужен User из БД — внутри роута получай его через user_service.
Это упрощённая версия паттерна из appss-back/src/services/authentication.py.
"""

from typing import Annotated

from fastapi import Depends, HTTPException, Request
from fastapi.security import APIKeyHeader

from config import get_config
from models.telegram import InitData, TgUser
from utils.token_helper import authenticate_token

token_header = APIKeyHeader(name="Authorization", scheme_name="Authorization")
internal_token_header = APIKeyHeader(name="X-Internal-Token")


async def authenticate(request: Request, token: str = Depends(token_header)) -> TgUser:
    """Проверка initData. Возвращает TgUser (из подписанного Telegram-payload)."""
    init_data = authenticate_token(token)
    request.state.init_data = init_data
    return init_data.user


def get_init_data(request: Request) -> InitData:
    return request.state.init_data


async def authenticate_internal(
    token: str = Depends(internal_token_header),
) -> None:
    """Авторизация internal-эндпоинтов (push, webhook от бота итд)."""
    if token != get_config().tg.push_internal_token:
        raise HTTPException(status_code=401, detail="Unauthorized")


Authentication = Annotated[TgUser, Depends(authenticate)]
CurrentInitData = Annotated[InitData, Depends(get_init_data)]
InternalAuth = Annotated[None, Depends(authenticate_internal)]
