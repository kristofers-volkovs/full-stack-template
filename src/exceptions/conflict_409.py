from src.exceptions.base_exception import BaseHTTPException


class Base409Exception(BaseHTTPException):
    status_code: int = 409


# === Custom exceptions


class DuplicatingUser409Exception(Base409Exception):
    pass
