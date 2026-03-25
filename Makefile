.PHONY: dev build prod shell

dev:
	docker compose up backend

build:
	docker compose build backend

prod:
	docker compose -f docker-compose.yml up backend

shell:
	docker compose run --rm backend /bin/bash

generate-client:
	bash scripts/generate_frontend_client.sh
