from collections.abc import Generator

import pytest
from sqlmodel import Session
from starlette.testclient import TestClient

from src.auth.oauth import OAuth
from tests.factories.user import UserFactory


@pytest.fixture(scope="function")
def client_admin(db: Session, client: TestClient) -> Generator[TestClient]:
    admin_params = UserFactory.create_admin_user(db=db)
    access_token = OAuth.create_access_token(subject=str(admin_params.user.id))
    header = {"Authorization": f"Bearer {access_token}"}

    # Modifies the client to include the header in every request
    client.headers.update(header)
    yield client
    # Cleanup - removes headers
    client.headers.clear()


@pytest.fixture(scope="function")
def client_user(db: Session, client: TestClient) -> Generator[TestClient]:
    user_params = UserFactory.create_random_user(db=db)
    access_token = OAuth.create_access_token(subject=str(user_params.user.id))
    header = {"Authorization": f"Bearer {access_token}"}

    # Modifies the client to include the header in every request
    client.headers.update(header)
    yield client
    # Cleanup - removes headers
    client.headers.clear()
