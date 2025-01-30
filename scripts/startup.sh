#!/bin/bash

# Check if the DB is alive
python src/db/ping.py

# Apply migrations
alembic -c ./src/db/alembic.ini upgrade head

# Checks if the migrations head is latest
python src/db/migration_head.py
ret=$?
if [ $ret -ne 0 ]; then
  exit
fi

# Create the initial DB data
python src/db/seed.py

# Run the backend service
if [ $1 = "--dev" ]; then
  fastapi run --reload src/main/app.py
else
  fastapi run --workers 4 src/main/app.py
fi
