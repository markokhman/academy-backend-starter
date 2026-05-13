FROM python:3.11-slim

WORKDIR /app

ENV PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false

RUN pip install poetry

COPY pyproject.toml ./
RUN poetry install --no-root

COPY . .

EXPOSE 8000

# Запускаем из src/ — все внутренние импорты пишутся без префикса src.
WORKDIR /app/src
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
