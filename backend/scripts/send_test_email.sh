#!/bin/bash

docker compose build backend
docker compose down -v --remove-orphans # Remove possibly previous broken stacks left hanging after an error
docker compose up -d backend

docker compose exec -T backend python tests/test_email.py "$@"

docker compose down -v --remove-orphans
