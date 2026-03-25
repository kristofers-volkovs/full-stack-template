import uuid
from typing import Annotated

from fastapi.params import Depends
from fastapi.security import OAuth2PasswordBearer

from src.auth.oauth import OAuth
from src.db.deps import SessionDep
from src.main.settings import settings
from src.models.user import User
from src.services.user_service import user_service

reusable_oauth2 = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/login")

TokenDep = Annotated[str, Depends(reusable_oauth2)]


def get_current_user(db: SessionDep, token: TokenDep) -> User:
    refresh_token_list = OAuth.validate_user_token(
        token=token, secret_key=settings.AUTH_ACCESS_TOKEN_KEY
    )
    user = user_service.get_active_user_by_id(
        db=db, user_id=uuid.UUID(refresh_token_list.sub)
    )
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]
