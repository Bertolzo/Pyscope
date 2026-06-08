"""Infra cache — sem imports externos."""


class Cache:
    def __init__(self) -> None:
        self._store: dict[str, object] = {}

    def get(self, key: str) -> object | None:
        return self._store.get(key)

    def set(self, key: str, value: object) -> None:
        self._store[key] = value

    def delete(self, key: str) -> None:
        self._store.pop(key, None)
