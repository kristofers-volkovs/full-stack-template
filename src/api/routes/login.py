import uuid
from typing import Annotated

from fastapi import APIRouter
from fastapi.params import Depends, Header
from fastapi.security import OAuth2PasswordRequestForm

from src.auth.oauth import OAuth
from src.db.deps import SessionDep
from src.email.email_sender import EmailSender
from src.exceptions.bad_request_400 import (
    InvalidCredentials400Exception,
)
from src.exceptions.forbidden_403 import InvalidToken403Exception
from src.main.settings import settings
from src.models.message import Message
from src.models.token import RefreshToken, Tokens
from src.models.user import PasswordReset, UserUpdate
from src.repositories.token_repository import token_repository
from src.repositories.user_repository import user_repository
from src.services.user_service import user_service

router = APIRouter(tags=["Login"])


@router.post(
    "/login",
    response_model=Tokens,
)
def login(
    db: SessionDep, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
) -> Tokens:
    user = user_repository.get_by_email(db=db, email=form_data.username)

    if (
        user is None
        or not user.is_active
        or not OAuth.verify_password(
            password=form_data.password, hashed_password=user.hashed_password
        )
    ):
        raise InvalidCredentials400Exception("Incorrect email or password")

    # To prevent potential thefts resets refresh tokens if there are 5 or more
    max_amount_of_refresh_tokens = 5
    if len(user.tokens) >= max_amount_of_refresh_tokens:
        for token in user.tokens:
            token_repository.remove(db=db, db_obj=token)

    # Refresh tokens are saved to track which ones are valid
    refresh_token = OAuth.create_refresh_token(subject=str(user.id))
    token_create = RefreshToken(
        refresh_token=refresh_token,
        user_id=user.id,
    )
    token_repository.create_token(db=db, token_create=token_create)

    return Tokens(
        access_token=OAuth.create_access_token(subject=str(user.id)),
        refresh_token=refresh_token,
    )


@router.post(
    "/refresh",
    response_model=Tokens,
)
def refresh(db: SessionDep, x_token: Annotated[str, Header()]) -> Tokens:
    db_refresh_token = token_repository.get_by_token(db=db, token=x_token)
    if db_refresh_token is None:
        # When a valid refresh token that is not in the DB is supplied
        # It means that it's an old token and potentially has been stolen
        refresh_token_payload = OAuth.validate_user_token(
            token=x_token,
            secret_key=settings.AUTH_REFRESH_TOKEN_KEY,
        )
        refresh_token_list = token_repository.get_by_user_id(
            db=db, user_id=uuid.UUID(refresh_token_payload.sub)
        )
        # Invalidates all tokens so that the user needs to log in again
        # and the potential attacker loses access
        for token in refresh_token_list:
            token_repository.remove(db=db, db_obj=token)

        raise InvalidToken403Exception(
            "Invalid refresh token", headers={"WWW-Authenticate": "Bearer"}
        )
    else:
        token_repository.remove(db=db, db_obj=db_refresh_token)

        refresh_token_payload = OAuth.validate_user_token(
            token=x_token,
            secret_key=settings.AUTH_REFRESH_TOKEN_KEY,
        )
        user_id = refresh_token_payload.sub

        refresh_token = OAuth.create_refresh_token(subject=user_id)
        token_create = RefreshToken(
            refresh_token=refresh_token,
            user_id=uuid.UUID(user_id),
        )
        token_repository.create_token(db=db, token_create=token_create)

        return Tokens(
            access_token=OAuth.create_access_token(subject=user_id),
            refresh_token=refresh_token,
        )


@router.post(
    "/logout",
    response_model=Message,
)
def logout(db: SessionDep, x_token: Annotated[str, Header()]) -> Message:
    db_refresh_token = token_repository.get_by_token(db=db, token=x_token)
    if db_refresh_token is not None:
        token_repository.remove(db=db, db_obj=db_refresh_token)

    return Message(msg="Logout successful")


@router.post(
    "/password-recovery/{email}",
    response_model=Message,
)
def recover_password(db: SessionDep, email: str) -> Message:
    user = user_service.get_active_user_by_email(db=db, user_email=email)
    password_reset_token = OAuth.create_password_reset_token(email=email)
    EmailSender.send_password_reset_email(
        email_receiver=user.email,
        token=password_reset_token,
    )

    return Message(msg="Password recovery email sent")


@router.post(
    "/reset-password",
    response_model=Message,
)
def reset_password(db: SessionDep, password_in: PasswordReset) -> Message:
    email = OAuth.validate_password_reset_token(token=password_in.token)
    user = user_service.get_active_user_by_email(db=db, user_email=email)

    user_update = UserUpdate(password=password_in.new_password)
    user_repository.update_user(db=db, db_user=user, user_in=user_update)

    return Message(msg="Password updated successfully")
