"""
Авто-подключение всех роутеров из routes/api/.
Каждый файл должен экспортить `router: APIRouter`.

Паттерн взят из appss-back/src/routes/api/appss/__init__.py.
"""

import importlib
from pathlib import Path

from fastapi import APIRouter

router = APIRouter(prefix="/api")
modules_dir = Path(__file__).parent

for f in sorted(modules_dir.glob("*.py")):
    if f.stem == "__init__":
        continue
    module = importlib.import_module(f".{f.stem}", package=__name__)
    if hasattr(module, "router") and isinstance(module.router, APIRouter):
        router.include_router(module.router)
