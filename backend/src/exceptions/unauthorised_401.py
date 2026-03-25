from src.exceptions.base_exception import BaseHTTPException


class Base401Exception(BaseHTTPException):
    status_code: int = 401


# === Custom exceptions


class InvalidToken401Exception(Base401Exception):
    pass
