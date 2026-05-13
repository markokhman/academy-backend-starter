"""
Проверка подписи Telegram WebApp initData.

КАК ЭТО РАБОТАЕТ
================

Telegram при открытии миниапки передаёт строку initData (urlencoded query):
  user=...&auth_date=...&query_id=...&hash=<подпись>

Подпись — HMAC-SHA256, где:
  secret_key = HMAC-SHA256(key="WebAppData", message=BOT_TOKEN)
  signature  = HMAC-SHA256(key=secret_key, message=data_check_string)

data_check_string собирается так:
  - все пары kv кроме hash
  - отсортированы по ключу
  - формат "key=value", соединены через \n

Если наша подпись совпадает с тем что прислал TG — значит данные пришли
из настоящего Telegram, никакой man-in-the-middle их не подменил.

Дополнительно проверяем срок: initData моложе INIT_DATA_TTL_HOURS часов.

Источник: код appss-back/src/utils/token_helper.py (упрощённая версия,
без UTM/referral логики, специфичной для APPSS).
"""

import base64
import hashlib
import hmac
import json
import logging
import time
from urllib import parse

from fastapi import HTTPException

from config import get_config
from models.telegram import InitData, TgUser


log = logging.getLogger(__name__)


def decode_init_data(init_data_raw: str, ttl_seconds: int) -> tuple[InitData, dict]:
    """
    Распарсить initData (raw query string) → InitData + raw dict (нужен для проверки подписи).
    """
    init_data_dict: dict = dict(parse.parse_qsl(init_data_raw))

    if "user" not in init_data_dict or init_data_dict["user"] == "":
        raise HTTPException(status_code=401, detail="User is required")

    auth_date = init_data_dict.get("auth_date")
    if auth_date is None:
        raise HTTPException(status_code=401, detail="auth_date is required")

    if time.time() - int(auth_date) > ttl_seconds:
        raise HTTPException(status_code=401, detail="initData expired")

    user_dict: dict = json.loads(init_data_dict["user"])
    user = TgUser(
        id=user_dict["id"],
        first_name=user_dict["first_name"],
        last_name=user_dict.get("last_name"),
        username=user_dict.get("username"),
        language_code=user_dict.get("language_code"),
        is_premium=user_dict.get("is_premium", False),
        allows_write_to_pm=user_dict.get("allows_write_to_pm", False),
        added_to_attachment_menu=user_dict.get("added_to_attachment_menu", False),
        photo_url=user_dict.get("photo_url"),
    )

    init_data = InitData(
        user=user,
        query_id=init_data_dict.get("query_id"),
        chat=init_data_dict.get("chat"),
        chat_type=init_data_dict.get("chat_type"),
        chat_instance=init_data_dict.get("chat_instance"),
        start_param=init_data_dict.get("start_param"),
        can_send_after=init_data_dict.get("can_send_after"),
        auth_date=auth_date,
        hash=init_data_dict.get("hash"),
    )

    return init_data, init_data_dict


def check_token_against_bot(init_data_dict: dict, init_data: InitData, bot_token: str) -> None:
    """Проверка HMAC-подписи Telegram WebApp."""
    init_data_pairs = sorted(
        (key, parse.unquote(value))
        for key, value in init_data_dict.items()
        if key != "hash"
    )
    data_check_string = "\n".join(f"{k}={v}" for k, v in init_data_pairs)

    secret_key = hmac.new(
        b"WebAppData",
        bot_token.encode(),
        hashlib.sha256,
    ).digest()

    expected_hash = hmac.new(
        secret_key,
        data_check_string.encode(),
        hashlib.sha256,
    ).hexdigest()

    if init_data.hash is None or not hmac.compare_digest(init_data.hash, expected_hash):
        log.warning("initData hash mismatch")
        raise HTTPException(status_code=401, detail="Invalid initData signature")


def authenticate_token(token: str) -> InitData:
    """
    Главная функция: принимает Authorization-заголовок (base64 от initData),
    возвращает InitData, либо кидает 401.
    """
    if not token:
        raise HTTPException(status_code=401, detail="Not authorized token")

    config = get_config()

    try:
        init_data_raw = base64.b64decode(token + "=" * (-len(token) % 4)).decode()
    except (UnicodeDecodeError, ValueError):
        raise HTTPException(status_code=401, detail="Invalid token format")

    ttl_seconds = config.tg.init_data_ttl_hours * 3600
    init_data, init_data_dict = decode_init_data(init_data_raw, ttl_seconds)

    # В development режиме можно пропускать проверку подписи (для мок-юзера из миниапки)
    if config.general.environment == "development" and init_data_dict.get("hash") == "mock_hash":
        log.warning("DEV mode: skipping signature check (mock initData)")
        return init_data

    check_token_against_bot(init_data_dict, init_data, config.tg.bot_token)

    return init_data
