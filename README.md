# Academy Backend Starter

> API на **FastAPI + Postgres + SQLAlchemy** с готовой верификацией Telegram initData. Один из трёх связанных репозиториев Vibe Coding Academy — поднимаются вместе.

## Связка из трёх репо

Telegram-приложение в нашем стеке = три отдельных сервиса, общающиеся по HTTP. Поднимать нужно **все три**.

| Репозиторий | Что это | Стек |
|---|---|---|
| 🤖 [academy-bot-starter](https://github.com/markokhman/academy-bot-starter) | Telegram-бот, точка входа в продукт | Python + aiogram |
| 📱 [academy-miniapp-starter](https://github.com/markokhman/academy-miniapp-starter) | Миниапка, основной UI | React + Vite + TS |
| 🔌 **academy-backend-starter** ← *ты здесь* | API, бизнес-логика, БД | FastAPI + Postgres |

---

## Архитектура связки

```
                   ┌─────────────┐
                   │   Telegram   │
                   └──────┬──────┘
                          │ long-poll (бот) / initData (миниап)
              ┌───────────┼───────────────┐
              ▼                           ▼
      ┌──────────────┐            ┌──────────────┐
      │     bot      │            │   miniapp    │
      │ (Python)     │            │  (React TS)  │
      └──────┬───────┘            └──────┬───────┘
             │                           │
             │  HTTP                     │ HTTP (Authorization: initData)
             │  (push events)            │
             ▼                           ▼
             └──────────────► backend ◄──┘
                            (этот репо)
                                  │
                                  ▼
                            PostgreSQL
```

Этот репо отвечает за:
- Верификацию подписи Telegram initData через `BOT_TOKEN`.
- Регистрацию/чтение юзеров в БД.
- Бизнес-логику (когда добавится).
- Отправку пушей через бот (HTTP к боту с shared internal-токеном).

---

## Зачем эта болванка

Главная ценность — **готовая верификация Telegram initData**. Это пара к `academy-miniapp-starter`: миниапка шлёт initData, бэкенд проверяет HMAC-подпись от `BOT_TOKEN`, регистрирует юзера.

Без болванки ученик упрётся в формат `data_check_string`, sorted keys, TTL, hash от `WebAppData` и т.д. Здесь это уже сделано (`src/utils/token_helper.py`).

---

## Что внутри

- FastAPI 0.111, асинхронно.
- SQLAlchemy 2 (async) + asyncpg + Alembic.
- pydantic-settings — все ENV в одном `Config`.
- Автодискаверинг роутов в `routes/api/`.
- ApiResult-обёртка для всех ответов (`{success, message, data}`).
- aiogram-клиент для отправки пушей в Telegram (используется бэкендом, не отдельный процесс).
- `docker-compose.yml` для локального Postgres.
- Makefile с командами `make dev`, `make migrate`, `make db-up`.

### Эндпоинты

| Метод | Путь | Что делает |
|---|---|---|
| `POST` | `/api/auth/verify` | Проверяет initData, регистрирует/возвращает юзера, отдаёт токен. |
| `GET` | `/api/me` | Текущий юзер (требует Authorization). |
| `POST` | `/api/push/send` | Шлёт сообщение через бот (нужен X-Internal-Token). |
| `GET` | `/_health` | Пинг. |
| `GET` | `/docs` | OpenAPI (только при `DEBUG=true`). |

---

## Quickstart (вся связка из трёх репо)

Перед запуском нужны: Python 3.11, Node 20+, Docker (для Postgres), [ngrok](https://ngrok.com).

1. **Создай бота** в [@BotFather](https://t.me/BotFather), скопируй `BOT_TOKEN`.
2. **Backend** (этот репо): см. ниже.
3. **Bot** (другой репо): `python src/main.py` — long-poll стартует.
4. **Miniapp** (другой репо): `pnpm dev` + `ngrok http 3000`.
5. В **@BotFather** → Menu Button → вставь ngrok-URL.
6. Открой бота → `/start` → кнопка → миниапка → бэкенд верифицирует → имя.

**Критичный инвариант:** `BOT_TOKEN` в `bot-starter/.env` и `backend-starter/.env` — **один и тот же**. Иначе подпись initData не сойдётся.

---

## Quickstart (только этот репо)

```bash
# 1. Poetry
curl -sSL https://install.python-poetry.org | python3 -
poetry config virtualenvs.in-project true

# 2. Зависимости
make install

# 3. Postgres локально
make db-up

# 4. Конфиг
cp .env.example .env
# Заполни: BOT_TOKEN, DATABASE_URL, PUSH_INTERNAL_TOKEN

# 5. Миграции
make migrate

# 6. Запуск
make dev
```

API стартует на `http://localhost:8000`. Swagger — `http://localhost:8000/docs` (если `DEBUG=true`).

### Тестовая проверка

```bash
curl http://localhost:8000/_health           # {"status":"ok"}
curl http://localhost:8000/api/me            # 401 без auth
```

«Вживую» — открыть миниапку через бота. Если профиль показался — связка работает.

---

## Структура

```
src/
├── app.py                # FastAPI app, CORS, routers, lifespan
├── config.py             # pydantic-settings — все ENV
├── dependencies.py       # DI-хелперы (get_session, get_user_service)
├── database/
│   ├── database.py       # SQLAlchemyManager
│   └── migrations/       # Alembic
├── models/               # SQLAlchemy ORM + pydantic
├── routes/api/           # авто-сборка из файлов
├── services/             # бизнес-логика
├── schemas/              # pydantic ответы
└── utils/token_helper.py # HMAC-проверка Telegram initData
```

---

## Ключевые архитектурные решения

- **Один `BOT_TOKEN` на бот и бэкенд** — иначе подпись initData не верифицируется.
- **БД = Postgres (локальный в docker-compose).** Если нужно — поменять `DATABASE_URL` на Supabase Connection Pooler.
- **Пуш `backend → bot` через HTTP** с shared `X-Internal-Token`. В проде у APPSS — RabbitMQ. Для академии overkill.
- **Запуск из `src/`** (это в `Makefile` и `Dockerfile`). Не из корня — иначе импорты сломаются. `.cursorrules` это явно прописывает.
- **DEV-bypass для миниапки**: при `ENVIRONMENT=development` принимается mock-hash. Чтобы ученик мог тестить без TG.

Подробности — в `_DECISIONS.md`.

---

## Для Claude / Cursor

Правила проекта — в `.cursorrules`. Там запуск из `src/`, авто-роуты, ApiResult, миграции, как добавлять новые модели/эндпоинты.

Если ты — агент и делаешь фичу, требующую изменений в боте или миниапке — открывай соседние репо (см. шапку).

---

## Что доделать перед продом

> На текущем этапе академии — деплой не делаем, работаем только локально. Эти пункты пригодятся на колах 5-6.

- Убрать DEV-bypass для mock-hash в проде (отключается по `ENVIRONMENT`).
- Кастомный OpenAPI со scrubbing для прода (вырезано в стартере, есть в `appss-back`).
- Sentry / структурированное логирование.
- Заменить HTTP-пуши на очередь, если будет нагрузка.
- Закоммитить `poetry.lock` после первого `poetry install`.
- Деплой через `Dockerfile` (Railway / Fly.io / Render).

---

## Часть программы

Артефакт **Кола 2** программы Vibe Coding Academy — «Подготовка + первый запуск». На этом коле поднимаем связку **локально** (Postgres в Docker, FastAPI на `:8000`). Деплой — позже.
