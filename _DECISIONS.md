# Решения и откуда взято

## Стек

Один-в-один с `appss-back` (упрощённо):
- FastAPI 0.111.1
- SQLAlchemy 2.0.31 + asyncpg 0.29.0
- Alembic 1.13.2
- pydantic 2.7.0 + pydantic-settings 2.8.1
- aiogram 3.8.0 (только httpx-клиент к боту, без полноценной инициализации)

## Структура

Скопировал каркас `appss-back/src/`:
- `app.py` — главный entry
- `config.py` — все ENV в одном объекте
- `database/database.py` — SQLAlchemyManager, get_session
- `routes/api/` — авто-сборка роутов из файлов
- `services/` — бизнес-логика
- `schemas/` — pydantic для API
- `utils/token_helper.py` — проверка подписи Telegram

Что НЕ перенёс:
- Sentry, MixPanel, PostHog — добавится по мере необходимости.
- RabbitMQ / Redis — нету в стартере.
- Strapi-интеграция — это специфика APPSS.
- S3 / aioboto3 — не нужно для hello world.
- Множество JWT-аутентификаций (admin, appss-pro, jwt) — оставлена только initData + internal.
- Soft-delete mixin — добавится в большом проекте.

## Проверка подписи (СЕРДЦЕ авторизации)

`utils/token_helper.py` — упрощённая копия `appss-back/src/utils/token_helper.py`:
- Парсит initData (urlencoded query).
- Считает HMAC-SHA256 по data_check_string и сравнивает с `hash`.
- Проверяет TTL (по умолчанию 24 часа из .env).

Что упростил vs оригинала:
- Убрал парсинг `start_param` с UTM/referral — это специфика APPSS.
- Убрал поддержку множественных `bot_tokens` (через `|`). Только один BOT_TOKEN.
- Добавил mock-fallback для DEV-режима с `hash == "mock_hash"`. Это позволяет миниапке работать из браузера без живой подписи (см. mockTelegramEnv в `miniapp-starter/src/shared/utils/launchParams.ts`).

**Важно:** mock-bypass работает ТОЛЬКО при `ENVIRONMENT=development` в `.env`.
В production такой initData будет отвергнут.

## БД — Postgres, не Supabase

В references стандартный Postgres (managed на DO).
Я оставил Postgres-подключение через asyncpg, но указал в README про Supabase как альтернативу — у Supabase под капотом Postgres, connection string совместим.

ВАЖНО: для Supabase нужен `?sslmode=require` в DATABASE_URL и **Transaction Pooler**, а не Direct connection (по их рекомендации для serverless).

## Связь с ботом — HTTP, не AMQP

В APPSS бот ↔ бэкенд = RabbitMQ. Для академии — overkill. HTTP с shared-токеном проще, понятнее и достаточно для всех учебных задач.

## ApiResult

Стандартизированный ответ `{success, message, data}` — из appss-back. Это единый формат, фронт ожидает `data.data`.

## Версии — pinned

Точно как в pyproject.toml `appss-back`. Это нужно, чтобы у учеников не разъезжалось окружение.

## Что подтвердить у Марка

- Поддерживаем ли мы Supabase как альтернативу самостоятельному Postgres? Я только упомянул в README, но если выбран Supabase как стандарт — поменять DATABASE_URL дефолт и расширить README.
- В appss-back используется `openapi_prefix="/stats"` и custom `create_openapi` со scrubbing. Я выкинул всё это для простоты — `/docs` доступен только в DEBUG. Норм?
- Mock-bypass подписи в DEV — компромисс между удобством и безопасностью. Альтернативы:
  1. Ученик каждый раз делает initData реальной (через ngrok + Telegram).
  2. Полностью отключить проверку в DEV (что я сделал).
  3. Подкладывать переменную VITE_LOCAL_TOKEN в миниапке. Тогда подпись реальная, и DEV-bypass не нужен.

  По-моему вариант 3 — самый честный, и я его описал в README миниапки. Но bypass оставил на случай если ученик забудет про VITE_LOCAL_TOKEN.

## Открытые вопросы

- Стоит ли вынести `services/bot.py` в `gateways/` или оставить в `services/`? В оригинале `appss-back` есть и `services/`, и `gateways/` — разделение неочевидное.
- Pre-commit hooks? В оригинале `.pre-commit-config.yaml` для ruff. Можно добавить, но это +1 шаг в README — баланс.
