from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from starlette.middleware.cors import CORSMiddleware

from src.api.router import api_router
from src.exceptions.base_exception import BaseHTTPException
from src.exceptions.handler import ExceptionHandler
from src.main.settings import settings


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    settings.enforce_non_default_secrets()
    yield


server = FastAPI(
    default_response_class=ORJSONResponse,
    title="Template API",
    version="0.0.1",
    lifespan=lifespan,
)

server.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_origins=["*"],
)

server.add_exception_handler(BaseHTTPException, ExceptionHandler())  # type: ignore

server.include_router(api_router, prefix=settings.API_V1_STR)
