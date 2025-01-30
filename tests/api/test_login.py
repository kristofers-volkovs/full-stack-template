import uuid

from sqlmodel import Session
from starlette.testclient import TestClient

from src.auth.oauth import OAuth
from src.main.settings import settings
from src.models.user import PasswordReset
from src.repositories.user_repository import user_repository
from tests.factories.token import TokenFactory
from tests.factories.user import UserFactory
from tests.utils.random import RandomStrings
from tests.validators.token import TokenValidator


def test_user_login(client: TestClient, db: Session) -> None:
    user_params = UserFactory.create_random_user(db=db)
    data = {"username": user_params.email, "password": user_params.password}
    response = client.post(f"{settings.API_V1_STR}/login", data=data)
    assert response.status_code == 200

    user = user_params.user
    content = response.json()

    access_token = content["access_token"]
    TokenValidator.validate_access_token(
        access_token=access_token, user_id=str(user.id)
    )

    refresh_token = content["refresh_token"]
    TokenValidator.validate_refresh_token(
        refresh_token=refresh_token, user_id=str(user.id)
    )
    TokenValidator.validate_refresh_token_amount(db=db, amount=1)


def test_user_wrong_email(client: TestClient, db: Session) -> None:
    user_params = UserFactory.create_random_user(db=db)

    data = {"username": "wrong", "password": user_params.password}
    response = client.post(f"{settings.API_V1_STR}/login", data=data)
    assert response.status_code == 400


def test_user_wrong_password(client: TestClient, db: Session) -> None:
    user_params = UserFactory.create_random_user(db=db)

    data = {"username": user_params.email, "password": "wrong"}
    response = client.post(f"{settings.API_V1_STR}/login", data=data)
    assert response.status_code == 400


def test_user_refresh_token_invalidation_login(client: TestClient, db: Session) -> None:
    user_params = UserFactory.create_random_user(db=db)
    user = user_params.user

    # Create the max amount of refresh tokens
    for _ in range(5):
        TokenFactory.create_refresh_token(db=db, user_id=user.id)

    data = {"username": user_params.email, "password": user_params.password}
    response = client.post(f"{settings.API_V1_STR}/login", data=data)
    assert response.status_code == 200

    TokenValidator.validate_refresh_token_amount(db=db, amount=1)


def test_user_token_refresh(client: TestClient, db: Session) -> None:
    user_params = UserFactory.create_random_user(db=db)

    data = {"username": user_params.email, "password": user_params.password}
    response = client.post(f"{settings.API_V1_STR}/login", data=data)
    assert response.status_code == 200

    content = response.json()
    refresh_token = content["refresh_token"]

    headers = {"X-Token": refresh_token}
    response = client.post(f"{settings.API_V1_STR}/refresh", headers=headers)
    assert response.status_code == 200

    TokenValidator.validate_refresh_token_amount(db=db, amount=1)


def test_user_old_token_refresh(client: TestClient, db: Session) -> None:
    user_params = UserFactory.create_random_user(db=db)
    user = user_params.user

    # Create the max amount of refresh tokens
    for _ in range(4):
        TokenFactory.create_refresh_token(db=db, user_id=user.id)
    refresh_token = TokenFactory.create_refresh_token(db=db, user_id=user.id)

    headers = {"X-Token": refresh_token.refresh_token}
    response = client.post(f"{settings.API_V1_STR}/refresh", headers=headers)
    assert response.status_code == 200

    TokenValidator.validate_refresh_token_amount(db=db, amount=5)

    response = client.post(f"{settings.API_V1_STR}/refresh", headers=headers)
    assert response.status_code == 403

    TokenValidator.validate_refresh_token_amount(db=db, amount=0)


def test_invalid_token(client: TestClient) -> None:
    refresh_token = OAuth.create_refresh_token(subject=str(uuid.uuid4()))
    headers = {"X-Token": refresh_token}
    response = client.post(f"{settings.API_V1_STR}/refresh", headers=headers)
    assert response.status_code == 403


def test_user_expired_token(client: TestClient, db: Session) -> None:
    user_params = UserFactory.create_random_user(db=db)
    user = user_params.user

    refresh_token = TokenFactory.create_refresh_token(
        db=db, user_id=user.id, delta_minutes=-100
    )

    headers = {"X-Token": refresh_token.refresh_token}
    response = client.post(f"{settings.API_V1_STR}/refresh", headers=headers)
    assert response.status_code == 403


def test_user_logout(client: TestClient, db: Session) -> None:
    user_params = UserFactory.create_random_user(db=db)

    data = {"username": user_params.email, "password": user_params.password}
    response = client.post(f"{settings.API_V1_STR}/login", data=data)
    assert response.status_code == 200

    content = response.json()
    refresh_token = content["refresh_token"]

    headers = {"X-Token": refresh_token}
    response = client.post(f"{settings.API_V1_STR}/logout", headers=headers)
    assert response.status_code == 200

    TokenValidator.validate_refresh_token_amount(db=db, amount=0)


def test_user_reset_password(client: TestClient, db: Session) -> None:
    user_params = UserFactory.create_random_user(db=db)

    password_token = OAuth.create_password_reset_token(email=user_params.email)
    new_password = RandomStrings.random_string()
    password_reset = PasswordReset(
        token=password_token,
        new_password=new_password,
    )
    json = password_reset.model_dump(exclude_unset=True)
    response = client.post(f"{settings.API_V1_STR}/reset-password", json=json)
    assert response.status_code == 200

    user_db = user_repository.get_by_id(db=db, obj_id=user_params.user.id)
    assert OAuth.verify_password(
        password=new_password, hashed_password=user_db.hashed_password
    )


def test_user_reset_password_wrong_email(client: TestClient) -> None:
    password_token = OAuth.create_password_reset_token(
        email=RandomStrings.random_email()
    )
    new_password = RandomStrings.random_string()
    password_reset = PasswordReset(
        token=password_token,
        new_password=new_password,
    )
    json = password_reset.model_dump(exclude_unset=True)
    response = client.post(f"{settings.API_V1_STR}/reset-password", json=json)
    assert response.status_code == 404
