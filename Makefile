.PHONY: dev prod shell-dev check test migrate

dev:
	docker compose up backend

build:
	docker compose build backend

prod:
	docker compose -f docker-compose.yml up backend

shell:
	docker compose run --rm backend /bin/bash

check:
	uv run -- ruff format src/ tests/ && \
	uv run -- ruff check src/ tests/ --fix && \
	bash scripts/run_mypy

test:
	bash scripts/init_test.sh

test-email:
	bash scripts/send_test_email.sh

title="title unset"
migrations:
	bash scripts/init_migrations.sh "${title}"
