"""
Точка входа FastAPI-приложения.

Структура — копия appss-back/src/app.py (упрощённая):
  - lifespan для корректного закрытия engine.
  - CORS middleware.
  - Подключение main_router из routes/.
  - Health check на /_health.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import get_config
from database.database import SQLAlchemyManager
from routes import main_router


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
log = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    log.info("Backend starting…")
    yield
    log.info("Shutting down: disposing database engine")
    if SQLAlchemyManager._engine is not None:
        await SQLAlchemyManager._engine.dispose()


config = get_config()

app = FastAPI(
    title="Vibe Coding Academy — backend starter",
    docs_url="/docs" if config.general.debug else None,
    redoc_url="/redoc" if config.general.debug else None,
    lifespan=lifespan,
)

origins = (
    [config.general.cors_allow_origins]
    if config.general.cors_allow_origins != "*"
    else ["*"]
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    max_age=86400,
)


@app.get("/_health")
async def health() -> dict:
    return {"status": "ok"}


app.include_router(main_router)
