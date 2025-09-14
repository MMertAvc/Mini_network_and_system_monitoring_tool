.PHONY: up dbinit api worker sched lint test fmt

up:
	docker compose up -d

dbinit:
	alembic upgrade head

api:
	uvicorn app.api.main:app --host 0.0.0.0 --port $${EXPORTER_PORT:-8000}

worker:
	celery -A app.workers.celery_app.app worker -l info --concurrency 4 --max-tasks-per-child=100

sched:
	python -m app.workers.scheduler

lint:
	ruff check .
	mypy app

fmt:
	ruff check . --fix
	black .
	isort .

test:
	pytest -q