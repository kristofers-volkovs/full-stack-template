#!/bin/bash

alembic -c ./src/db/alembic.ini upgrade head
alembic -c ./src/db/alembic.ini revision --autogenerate -m "$1"
