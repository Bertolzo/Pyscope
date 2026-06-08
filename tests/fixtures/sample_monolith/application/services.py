"""Application services — importa de domain E infra (cross-module + layer violation)."""

from domain.models import User
from infra.db import Database


class UserService:
    def __init__(self, db: Database) -> None:
        self.db = db

    def get_user(self, user_id: int) -> User:
        return self.db.query_user(user_id)

    def create_user(self, name: str, email: str) -> User:
        user = User(id=0, name=name, email=email)
        return self.db.save_user(user)
