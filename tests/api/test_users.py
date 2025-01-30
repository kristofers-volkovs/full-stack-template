from sqlmodel import Session
from starlette.testclient import TestClient

from src.auth.oauth import OAuth
from src.main.settings import settings
from src.models.user import (
    User,
    UserCreate,
    UserGroup,
    UserPublic,
    UserRegister,
    UserUpdate,
    UserUpdatePassword,
)
from src.repositories.user_repository import user_repository
from tests.factories.user import UserFactory
from tests.utils.random import RandomStrings
from tests.validators.user import UserValidator


def test_get_all_users(client_admin: TestClient, db: Session) -> None:
    user_list_db: list[User] = []
    for _ in range(3):
        user_params = UserFactory.create_random_user(db=db)
        user_list_db.append(user_params.user)

    response = client_admin.get(f"{settings.API_V1_STR}/users")
    assert response.status_code == 200

    content = response.json()
    user_list_public: list[UserPublic] = content["users"]
    admin_user = 1
    assert len(user_list_db) + admin_user == len(user_list_public)


def test_get_2_users(client_admin: TestClient, db: Session) -> None:
    user_list_db: list[User] = []
    for _ in range(3):
        user_params = UserFactory.create_random_user(db=db)
        user_list_db.append(user_params.user)

    params = {"limit": 2}
    response = client_admin.get(f"{settings.API_V1_STR}/users", params=params)
    assert response.status_code == 200

    content = response.json()
    user_list_public: list[UserPublic] = content["users"]
    assert len(user_list_public) == 2


def test_create_user(client_admin: TestClient, db: Session) -> None:
    user_create = UserCreate(
        email=RandomStrings.random_email(),
        password=RandomStrings.random_string(),
        user_group=UserGroup.USER.value,
    )
    json = user_create.model_dump(exclude_unset=True)
    response = client_admin.post(f"{settings.API_V1_STR}/users", json=json)
    assert response.status_code == 200

    UserValidator.validate_user_amount(db=db, amount=2)  # created user + admin user = 2


def test_create_user_with_existing_email(client_admin: TestClient, db: Session) -> None:
    user_params = UserFactory.create_random_user(db=db)

    user_create = UserCreate(
        email=user_params.email,
        password=RandomStrings.random_string(),
        user_group=UserGroup.USER.value,
    )
    json = user_create.model_dump(exclude_unset=True)
    response = client_admin.post(f"{settings.API_V1_STR}/users", json=json)
    assert response.status_code == 400

    UserValidator.validate_user_amount(
        db=db, amount=2
    )  # existing user + admin user = 2


def test_register_new_user(client: TestClient, db: Session) -> None:
    user_register = UserRegister(
        email=RandomStrings.random_email(),
        password=RandomStrings.random_string(),
    )
    json = user_register.model_dump(exclude_unset=True)
    response = client.post(f"{settings.API_V1_STR}/users/signup", json=json)
    assert response.status_code == 200

    UserValidator.validate_user_amount(db=db, amount=1)


def test_register_new_user_with_existing_email(client: TestClient, db: Session) -> None:
    user_params = UserFactory.create_random_user(db=db)

    user_register = UserRegister(
        email=user_params.email,
        password=RandomStrings.random_string(),
    )
    json = user_register.model_dump(exclude_unset=True)
    response = client.post(f"{settings.API_V1_STR}/users/signup", json=json)
    assert response.status_code == 400

    UserValidator.validate_user_amount(db=db, amount=1)


def test_get_specific_user(client_admin: TestClient, db: Session) -> None:
    user_params = UserFactory.create_random_user(db=db)
    user_id = user_params.user.id
    response = client_admin.get(f"{settings.API_V1_STR}/users/{user_id}")
    assert response.status_code == 200


def test_update_specific_user(client_admin: TestClient, db: Session) -> None:
    user_params = UserFactory.create_random_user(db=db)
    user_id = user_params.user.id

    new_email = RandomStrings.random_email()
    new_password = RandomStrings.random_string()
    new_user_group = UserGroup.ADMIN.value
    user_update = UserUpdate(
        email=new_email,
        password=new_password,
        user_group=new_user_group,
    )
    json = user_update.model_dump(exclude_unset=True)
    response = client_admin.patch(f"{settings.API_V1_STR}/users/{user_id}", json=json)
    assert response.status_code == 200

    user_public = UserPublic.model_validate(response.json())
    assert user_public.email == new_email
    assert user_public.user_group == new_user_group

    UserValidator.validate_user_amount(
        db=db, amount=2
    )  # existing user + admin user = 2


def test_update_specific_user_with_existing_email(
    client_admin: TestClient, db: Session
) -> None:
    user_params_1 = UserFactory.create_random_user(db=db)
    user_params_2 = UserFactory.create_random_user(db=db)
    user_2_id = user_params_2.user.id

    user_update = UserUpdate(
        email=user_params_1.email,
    )
    json = user_update.model_dump(exclude_unset=True)
    response = client_admin.patch(f"{settings.API_V1_STR}/users/{user_2_id}", json=json)
    assert response.status_code == 409


def test_delete_user(client_admin: TestClient, db: Session) -> None:
    user_params = UserFactory.create_random_user(db=db)
    user_id = user_params.user.id

    response = client_admin.delete(f"{settings.API_V1_STR}/users/{user_id}")
    assert response.status_code == 200

    UserValidator.validate_user_amount(db=db, amount=2)  # disabled user & admin user


def test_delete_admin(client_admin: TestClient, db: Session) -> None:
    user_list = user_repository.get_range(db=db)
    assert len(user_list) == 1
    admin_user = user_list[0]
    user_id = admin_user.id

    response = client_admin.delete(f"{settings.API_V1_STR}/users/{user_id}")
    assert response.status_code == 403


def test_get_me(client_user: TestClient, db: Session) -> None:
    user_list = user_repository.get_range(db=db)
    assert len(user_list) == 1
    user_db = user_list[0]

    response = client_user.get(f"{settings.API_V1_STR}/users/me")
    assert response.status_code == 200

    user_api = UserPublic.model_validate(response.json())
    assert user_api.id == user_db.id
    assert user_api.email == user_db.email
    assert user_api.user_group == user_db.user_group


def test_update_email_me(client_user: TestClient) -> None:
    user_update = UserUpdate(
        email=RandomStrings.random_email(),
    )
    json = user_update.model_dump(exclude_unset=True)
    response = client_user.patch(f"{settings.API_V1_STR}/users/me", json=json)
    assert response.status_code == 200


def test_update_me_with_existing_email(client_user: TestClient, db: Session) -> None:
    user_params = UserFactory.create_random_user(db=db)

    user_update = UserUpdate(
        email=user_params.email,
    )
    json = user_update.model_dump(exclude_unset=True)
    response = client_user.patch(f"{settings.API_V1_STR}/users/me", json=json)
    assert response.status_code == 409


def test_update_password_me(client: TestClient, db: Session) -> None:
    user_params = UserFactory.create_random_user(db=db)

    access_token = OAuth.create_access_token(subject=str(user_params.user.id))
    header = {"Authorization": f"Bearer {access_token}"}

    user_update_password = UserUpdatePassword(
        current_password=user_params.password,
        new_password=RandomStrings.random_string(),
    )
    json = user_update_password.model_dump(exclude_unset=True)
    response = client.patch(
        f"{settings.API_V1_STR}/users/me/password", json=json, headers=header
    )
    assert response.status_code == 200


def test_update_me_incorrect_password(client_user: TestClient) -> None:
    user_update_password = UserUpdatePassword(
        current_password=RandomStrings.random_string(),
        new_password=RandomStrings.random_string(),
    )
    json = user_update_password.model_dump(exclude_unset=True)
    response = client_user.patch(f"{settings.API_V1_STR}/users/me/password", json=json)
    assert response.status_code == 400


def test_update_me_same_password(client: TestClient, db: Session) -> None:
    user_params = UserFactory.create_random_user(db=db)

    access_token = OAuth.create_access_token(subject=str(user_params.user.id))
    header = {"Authorization": f"Bearer {access_token}"}

    user_update_password = UserUpdatePassword(
        current_password=user_params.password,
        new_password=user_params.password,
    )
    json = user_update_password.model_dump(exclude_unset=True)
    response = client.patch(
        f"{settings.API_V1_STR}/users/me/password", json=json, headers=header
    )
    assert response.status_code == 400


def test_delete_me(client_user: TestClient, db: Session) -> None:
    response = client_user.delete(f"{settings.API_V1_STR}/users/me")
    assert response.status_code == 200

    user_list = user_repository.get_range(db=db)
    assert len(user_list) == 1
    user_db = user_list[0]
    assert not user_db.is_active


def test_admin_delete_me(client_admin: TestClient) -> None:
    response = client_admin.delete(f"{settings.API_V1_STR}/users/me")
    assert response.status_code == 403
