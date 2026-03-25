#!/bin/bash

docker compose build backend
docker compose down -v --remove-orphans # Remove possibly previous broken stacks left hanging after an error
docker compose up -d backend

docker compose exec -T --user $(id -u):$(id -g) backend /bin/bash ./scripts/run_migrations.sh "$1" "$@"

docker compose down -v --remove-orphans
