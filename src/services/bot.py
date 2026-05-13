"""
Клиент для отправки пушей через бота.

Сам бэкенд НЕ держит aiogram-инстанс — это разделение ответственности.
Бот живёт в отдельном процессе (стартер bot-starter) и выставляет HTTP-эндпоинт /push.

Бэкенд просто делает HTTP-запрос: "Отправь юзеру X сообщение Y".
"""

import logging

import httpx

from config import get_config

log = logging.getLogger(__name__)


class BotPushClient:
    def __init__(self) -> None:
        config = get_config()
        self._url = config.tg.bot_push_url.rstrip("/") + "/push"
        self._token = config.tg.push_internal_token
        self._client = httpx.AsyncClient(timeout=10.0)

    async def send_message(self, tg_id: int, text: str) -> bool:
        """Отправить сообщение юзеру через бота. Возвращает True если успешно."""
        try:
            response = await self._client.post(
                self._url,
                json={"tg_id": tg_id, "text": text},
                headers={"X-Internal-Token": self._token},
            )
            response.raise_for_status()
            return True
        except httpx.HTTPError as e:
            log.exception("Failed to send push to %s: %s", tg_id, e)
            return False

    async def close(self) -> None:
        await self._client.aclose()


bot_push_client = BotPushClient()
