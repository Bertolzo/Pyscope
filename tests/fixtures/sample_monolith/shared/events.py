"""Shared events — base para eventos. VIOLAÇÃO: importa de domain (shared→domain)."""

from dataclasses import dataclass
from datetime import datetime

from domain.models import User


@dataclass
class Event:
    timestamp: str = ""
    event_type: str = ""

    def __post_init__(self) -> None:
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()


class EventBus:
    def __init__(self) -> None:
        self._handlers: list = []

    def publish(self, event: Event) -> None:
        for handler in self._handlers:
            handler(event)

    def subscribe(self, handler: callable) -> None:
        self._handlers.append(handler)
