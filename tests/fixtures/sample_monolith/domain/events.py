"""Domain events — importa de shared.events (ciclo potencial)."""

from shared.events import Event


@dataclass
class UserCreated(Event):
    user_id: int
    username: str


@dataclass
class OrderPlaced(Event):
    order_id: int
    user_id: int
    total: float
