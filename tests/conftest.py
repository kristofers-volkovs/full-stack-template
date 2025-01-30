from collections.abc import Generator
from glob import glob

import pytest
from fastapi.testclient import TestClient
from sqlalchemy_utils import (  # type: ignore[import-untyped]
    create_database,
    database_exists,
    drop_database,
)
from sqlmodel import Session, create_engine

from src.db.deps import get_db
from src.main.app import server
from src.main.settings import settings
from src.models import SQLModel as Base  # type: ignore[attr-defined]


def _refactor_as_module(fixture_path: str) -> str:
    return fixture_path.replace("/", ".").replace("\\", ".").replace(".py", "")


# Imports all fixtures defined outside conftest.py
pytest_plugins = [
    _refactor_as_module(fixture)
    for fixture in glob("tests/fixtures/*.py")
    if "__" not in fixture
]

test_engine = create_engine(str(settings.SQLALCHEMY_TEST_DATABASE_URI))


def create_test_db() -> None:
    if not database_exists(test_engine.url):
        create_database(test_engine.url)


def drop_test_db() -> None:
    if database_exists(test_engine.url):
        drop_database(test_engine.url)


@pytest.fixture(scope="session", autouse=True)
def setup_test_db() -> Generator[None]:
    create_test_db()
    Base.metadata.create_all(bind=test_engine)
    yield
    drop_test_db()


@pytest.fixture(scope="function")
def db() -> Generator[Session]:
    session = Session(test_engine)
    yield session
    session.rollback()
    session.close()


@pytest.fixture(scope="function")
def client(db: Session) -> Generator[TestClient]:
    def override_get_db() -> Generator[Session]:
        yield db

    server.dependency_overrides[get_db] = override_get_db

    with TestClient(server) as c:
        yield c

    server.dependency_overrides.clear()
