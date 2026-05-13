"""
POST /api/push/send  (internal)
-------------------------------
Отправить юзеру сообщение в Telegram через бота.

Этот эндпоинт защищён shared-токеном X-Internal-Token.
Подразумевается что его дёргают серверные процессы (cron, worker, другой backend),
а не миниапка.

Пример:
    curl -X POST http://localhost:8000/api/push/send \
         -H "X-Internal-Token: <PUSH_INTERNAL_TOKEN>" \
         -H "Content-Type: application/json" \
         -d '{"tg_id": 874423521, "text": "<b>Привет!</b>"}'
"""

from fastapi import APIRouter
from pydantic import BaseModel, Field

from schemas import ApiResult
from services.authentication import InternalAuth
from services.bot import bot_push_client

router = APIRouter(prefix="/push", tags=["Push"])


class SendPushPayload(BaseModel):
    tg_id: int = Field(..., description="Telegram ID получателя")
    text: str = Field(..., description="Текст сообщения (HTML allowed)")


@router.post("/send")
async def send_push(payload: SendPushPayload, _: InternalAuth) -> ApiResult[bool]:
    ok = await bot_push_client.send_message(payload.tg_id, payload.text)
    return ApiResult(success=ok, data=ok)
