FROM python:3.13.0-bullseye as build-env

ENV APP_ROOT=/app
ENV PYTHONUNBUFFERED=1

WORKDIR $APP_ROOT

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV	UV_COMPILE_BYTECODE=1 \
	UV_LINK_MODE=copy


# Install dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=backend/uv.lock,target=backend/uv.lock \
    --mount=type=bind,source=backend/pyproject.toml,target=backend/pyproject.toml \
    uv sync --directory=backend --frozen --no-install-project

ENV PYTHONPATH=/app

# Copy dependency requirements
COPY backend/pyproject.toml backend/uv.lock $APP_ROOT/

# Sync the project
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync

FROM build-env as dev

ENV APP_ROOT=/app
ENV PYTHONUNBUFFERED=1
ENV PATH="/app/.venv/bin:$PATH"

WORKDIR $APP_ROOT

# Copy the code
COPY backend/src $APP_ROOT/src/

# Copy scripts
COPY ../backend/scripts $APP_ROOT/scripts/

# Copy tests
COPY backend/tests $APP_ROOT/tests/

FROM python:3.13.0-slim-bullseye as prod

ENV APP_ROOT=/app
ENV PYTHONUNBUFFERED=1 \
	VIRTUAL_ENV=$APP_ROOT/.venv \
	PATH="/app/.venv/bin:$PATH"

COPY --from=build-env ${VIRTUAL_ENV} ${VIRTUAL_ENV}

WORKDIR $APP_ROOT

# Copy the code
COPY backend/src $APP_ROOT/src/

# Copy startup script
COPY ../backend/scripts $APP_ROOT/scripts/

# Copy tests
COPY backend/tests $APP_ROOT/tests/
