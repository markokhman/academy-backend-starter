.PHONY: install dev migrate makemigration db-up db-down

# Установка зависимостей
install:
	poetry install

# Запуск API (с авто-перезагрузкой). Запускается из src/, поэтому импорты пишем без префикса.
dev:
	cd src && poetry run uvicorn app:app --host 0.0.0.0 --port 8000 --reload

# Применить миграции
migrate:
	poetry run alembic upgrade head

# Создать новую миграцию из изменений в моделях
# Использование: make makemigration message="add posts table"
makemigration:
	poetry run alembic revision --autogenerate -m "$(message)"

# Поднять локальную базу через docker compose
db-up:
	docker compose -f db.docker-compose.yml up -d

# Остановить локальную базу
db-down:
	docker compose -f db.docker-compose.yml down
