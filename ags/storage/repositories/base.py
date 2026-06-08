"""
BaseRepository — Métodos comuns para todos os repositories.
"""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any, Dict, List, Optional, TypeVar

from ags.storage.database import Database

T = TypeVar("T")


class BaseRepository:
    """Base class para repositories."""

    def __init__(self, db: Database) -> None:
        self.db = db

    def _now(self) -> str:
        return datetime.now().isoformat()

    def _to_json(self, obj: Any) -> str:
        if obj is None:
            return "{}"
        if hasattr(obj, "model_dump"):
            return json.dumps(obj.model_dump(), ensure_ascii=False, default=str)
        if hasattr(obj, "dict"):
            return json.dumps(obj.dict(), ensure_ascii=False, default=str)
        if isinstance(obj, dict):
            return json.dumps(obj, ensure_ascii=False, default=str)
        return json.dumps(str(obj), ensure_ascii=False)

    def _save(self, table: str, data: Dict[str, Any]) -> int:
        columns = ", ".join(data.keys())
        placeholders = ", ".join(["?"] * len(data))
        sql = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        cursor = self.db.execute(sql, list(data.values()))
        self.db.commit()
        return cursor.lastrowid or 0

    def _get_latest(self, table: str) -> Optional[Dict[str, Any]]:
        row = self.db.fetchone(f"SELECT * FROM {table} ORDER BY id DESC LIMIT 1")
        return dict(row) if row else None

    def _get_history(self, table: str, limit: int = 50) -> List[Dict[str, Any]]:
        rows = self.db.fetchall(
            f"SELECT * FROM {table} ORDER BY id DESC LIMIT ?", (limit,)
        )
        return [dict(r) for r in rows]

    def _get_range(
        self, table: str, start: str, end: str
    ) -> List[Dict[str, Any]]:
        rows = self.db.fetchall(
            f"SELECT * FROM {table} WHERE timestamp BETWEEN ? AND ? ORDER BY timestamp",
            (start, end),
        )
        return [dict(r) for r in rows]

    def _get_by_id(self, table: str, record_id: int) -> Optional[Dict[str, Any]]:
        row = self.db.fetchone(
            f"SELECT * FROM {table} WHERE id = ?", (record_id,)
        )
        return dict(row) if row else None

    def _count(self, table: str) -> int:
        row = self.db.fetchone(f"SELECT COUNT(*) as cnt FROM {table}")
        return row["cnt"] if row else 0
