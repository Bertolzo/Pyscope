"""API routes — importa de domain."""

from domain.models import User
from domain.exceptions import NotFoundError


def get_user(user_id: int) -> User:
    if user_id <= 0:
        raise NotFoundError(f"User {user_id} not found")
    return User(id=user_id, name="test")
