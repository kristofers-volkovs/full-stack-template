import uuid
from typing import Any

from fastapi import APIRouter
from fastapi.params import Depends

from src.api.deps import CurrentUser
from src.auth.access_checker import AccessChecker
from src.auth.oauth import OAuth
from src.db.deps import SessionDep
from src.email.email_sender import EmailSender
from src.exceptions.bad_request_400 import (
    DuplicatingUser400Exception,
    InvalidPassword400Exception,
)
from src.exceptions.conflict_409 import DuplicatingUser409Exception
from src.exceptions.forbidden_403 import ForbiddenAction403Exception
from src.main.settings import settings
from src.models.message import Message
from src.models.user import (
    UserCreate,
    UserGroup,
    UserPublic,
    UserRegister,
    UsersPublic,
    UserUpdate,
    UserUpdateMe,
    UserUpdatePassword,
)
from src.repositories.user_repository import user_repository
from src.services.user_service import user_service

router = APIRouter(prefix="/users", tags=["Users"])


@router.get(
    "/",
    dependencies=[Depends(AccessChecker([UserGroup.ADMIN]))],
    response_model=UsersPublic,
)
def get_users(db: SessionDep, skip: int = 0, limit: int = 100) -> Any:
    users = user_repository.get_range(db=db, skip=skip, limit=limit)
    return UsersPublic(users=users)


@router.post(
    "/",
    dependencies=[Depends(AccessChecker([UserGroup.ADMIN]))],
    response_model=UserPublic,
)
def create_user(db: SessionDep, user_in: UserCreate) -> Any:
    user = user_repository.get_by_email(db=db, email=user_in.email)
    if user is not None:
        raise DuplicatingUser400Exception("A user with this email already exists")
    user = user_repository.create_user(db=db, user_create=user_in)

    if settings.SMTP_USER is not None:
        EmailSender.send_new_account_email(
            email_receiver=user.email,
        )

    return user


@router.post("/signup", response_model=UserPublic)
def register_user(db: SessionDep, user_in: UserRegister) -> Any:
    user = user_repository.get_by_email(db=db, email=user_in.email)
    if user is not None:
        raise DuplicatingUser400Exception("A user with this email already exists")
    user_create = UserCreate.model_validate(user_in)
    user = user_repository.create_user(db=db, user_create=user_create)
    return user


@router.get(
    "/me",
    dependencies=[Depends(AccessChecker([UserGroup.ADMIN, UserGroup.USER]))],
    response_model=UserPublic,
)
def get_user_me(user: CurrentUser) -> Any:
    return user


@router.patch(
    "/me",
    dependencies=[Depends(AccessChecker([UserGroup.ADMIN, UserGroup.USER]))],
    response_model=UserPublic,
)
def update_user_me(db: SessionDep, user: CurrentUser, user_in: UserUpdateMe) -> Any:
    if user_in.email is not None:
        existing_user = user_repository.get_by_email(db=db, email=user_in.email)
        if existing_user is not None and existing_user.id != user.id:
            raise DuplicatingUser409Exception("User with this email already exists")

    user_update = UserUpdate(email=user_in.email)
    user = user_repository.update_user(db=db, db_user=user, user_in=user_update)
    return user


@router.patch(
    "/me/password",
    dependencies=[Depends(AccessChecker([UserGroup.ADMIN, UserGroup.USER]))],
    response_model=UserPublic,
)
def update_password_me(
    db: SessionDep, user: CurrentUser, user_in: UserUpdatePassword
) -> Any:
    if not OAuth.verify_password(
        password=user_in.current_password, hashed_password=user.hashed_password
    ):
        raise InvalidPassword400Exception("Incorrect password")
    if user_in.current_password == user_in.new_password:
        raise InvalidPassword400Exception(
            "The new password cannot be the same as the current one"
        )

    user_update = UserUpdate(password=user_in.new_password)
    user = user_repository.update_user(db=db, db_user=user, user_in=user_update)
    return user


@router.delete(
    "/me",
    dependencies=[Depends(AccessChecker([UserGroup.ADMIN, UserGroup.USER]))],
    response_model=Message,
)
def delete_user_me(db: SessionDep, user: CurrentUser) -> Message:
    if user.user_group == UserGroup.ADMIN.value:
        raise ForbiddenAction403Exception("Admins are not allowed to delete themselves")

    user_repository.disable(db=db, db_obj=user)
    return Message(msg="User deleted successfully")


@router.get(
    "/{user_id}",
    dependencies=[Depends(AccessChecker([UserGroup.ADMIN]))],
    response_model=UserPublic,
)
def get_user_by_id(db: SessionDep, user_id: uuid.UUID) -> Any:
    user = user_service.get_user_by_id(db=db, user_id=user_id)
    return user


@router.patch(
    "/{user_id}",
    dependencies=[Depends(AccessChecker([UserGroup.ADMIN]))],
    response_model=UserPublic,
)
def update_user_by_id(db: SessionDep, user_id: uuid.UUID, user_in: UserUpdate) -> Any:
    user = user_service.get_user_by_id(db=db, user_id=user_id)

    if user_in.email is not None:
        existing_user = user_repository.get_by_email(db=db, email=user_in.email)
        if existing_user is not None and existing_user.id != user_id:
            raise DuplicatingUser409Exception("User with this email already exists")

    user = user_repository.update_user(db=db, db_user=user, user_in=user_in)
    return user


@router.delete(
    "/{user_id}",
    dependencies=[Depends(AccessChecker([UserGroup.ADMIN]))],
    response_model=Message,
)
def delete_user_by_id(db: SessionDep, user: CurrentUser, user_id: uuid.UUID) -> Message:
    db_user = user_service.get_active_user_by_id(db=db, user_id=user_id)
    if user == db_user:
        raise ForbiddenAction403Exception("Admins are not allowed to delete themselves")

    user_repository.disable(db=db, db_obj=db_user)
    return Message(msg="User deleted successfully")
