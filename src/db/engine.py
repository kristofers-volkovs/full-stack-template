from sqlalchemy_utils import (  # type: ignore[import-untyped]
    create_database,
    database_exists,
)
from sqlmodel import create_engine

from src.main.settings import settings

engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))

if not database_exists(engine.url):
    create_database(engine.url)
