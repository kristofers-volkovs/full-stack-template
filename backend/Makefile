.PHONY: check test test-email migrations

check:
	uv run -- ruff format src/ tests/ scripts/cleanup_openapi_schema.py && \
	uv run -- ruff check src/ tests/ scripts/cleanup_openapi_schema.py --fix && \
	bash scripts/run_mypy

test:
	bash scripts/init_test.sh

test-email:
	bash scripts/send_test_email.sh

title="title unset"
migrations:
	bash scripts/init_migrations.sh "${title}"
