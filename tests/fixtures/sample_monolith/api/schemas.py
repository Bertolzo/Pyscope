"""API schemas — importa de domain."""

from domain.models import User


def user_to_schema(user: User) -> dict:
    return {"id": user.id, "name": user.name}
