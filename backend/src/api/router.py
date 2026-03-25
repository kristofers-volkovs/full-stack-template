from fastapi import APIRouter

from src.api.routes import health, login, users

api_router = APIRouter()

api_router.include_router(health.router)

api_router.include_router(login.router)
api_router.include_router(users.router)
