#!/bin/bash

docker compose build backend
docker compose down -v --remove-orphans # Remove possibly previous broken stacks left hanging after an error
docker compose up -d backend

docker compose exec -T --user $(id -u):$(id -g) backend /bin/bash ./scripts/generate_openapi_schema.sh "$@"

docker compose down -v --remove-orphans

mv backend/src/openapi.json frontend/

cd frontend || exit
yarn run generate-client
npx biome format --write ./src/client
