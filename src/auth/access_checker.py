from src.api.deps import CurrentUser
from src.exceptions.forbidden_403 import NotEnoughPrivileges403Exception
from src.models.user import UserGroup


class AccessChecker:
    def __init__(self, allowed_groups: list[UserGroup]):
        self._allowed_groups = allowed_groups

    def __call__(self, user: CurrentUser) -> None:
        allowed_groups = [role.value for role in self._allowed_groups]
        if user.user_group not in allowed_groups:
            raise NotEnoughPrivileges403Exception(
                "User does not have enough privileges"
            )
