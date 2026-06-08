"""Application use cases — importa de domain."""

from domain.models import User, Order
from domain.events import UserCreated


def create_user_with_welcome(name: str, email: str) -> User:
    user = User(id=0, name=name, email=email)
    event = UserCreated(user_id=user.id, username=name)
    return user
