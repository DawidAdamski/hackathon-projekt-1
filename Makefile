SHELL := /bin/bash

DC := docker compose

.PHONY: up down logs backend-shell migrate downgrade makemigration reset-db build

build:
	$(DC) up -d --build

up:
	$(DC) up -d

down:
	$(DC) down

logs:
	$(DC) logs -f backend worker

backend-shell:
	$(DC) exec backend bash

migrate:
	$(DC) exec backend alembic upgrade head

downgrade:
	$(DC) exec backend alembic downgrade -1

makemigration:
	$(DC) exec backend alembic revision --autogenerate -m "$m"

reset-db:
	$(DC) stop backend worker || true
	$(DC) exec db bash -c "psql -U hacknation -d hacknation -c 'DROP SCHEMA public CASCADE; CREATE SCHEMA public;'" || true
	$(DC) start backend worker || true
	$(DC) exec backend alembic upgrade head
