"""Domain models — entidades centrais (sem imports externos)."""

from dataclasses import dataclass


@dataclass
class User:
    id: int
    name: str
    email: str = ""


@dataclass
class Order:
    id: int
    user_id: int
    total: float
