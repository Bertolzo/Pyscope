"""Infra database — VIOLAÇÃO: importa de domain (infra→domain)."""

from domain.models import User


class Database:
    def __init__(self) -> None:
        self._users: dict[int, User] = {}

    def query_user(self, user_id: int) -> User:
        if user_id not in self._users:
            return User(id=user_id, name="unknown")
        return self._users[user_id]

    def save_user(self, user: User) -> User:
        self._users[user.id] = user
        return user
