"""
GovernanceRepository — Persistência de eventos de governança.
"""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

from ags.storage.database import Database

from .base import BaseRepository


class GovernanceRepository(BaseRepository):
    """Repository para eventos de governança."""

    TABLE = "governance_events"

    def save(self, snapshot_id: int, report_data: Dict[str, Any]) -> int:
        data = {
            "snapshot_id": snapshot_id,
            "timestamp": self._now(),
            "merge_allowed": 1 if report_data.get("merge_allowed", True) else 0,
            "gate_status": report_data.get("gate_status", ""),
            "violations_count": report_data.get("violations_count", 0),
            "critical_count": report_data.get("critical_count", 0),
            "fatal_count": report_data.get("fatal_count", 0),
            "full_report": json.dumps(report_data, ensure_ascii=False, default=str),
        }
        return self._save(self.TABLE, data)

    def get_latest(self) -> Optional[Dict[str, Any]]:
        return self._get_latest(self.TABLE)

    def get_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        return self._get_history(self.TABLE, limit)

    def get_by_snapshot(self, snapshot_id: int) -> Optional[Dict[str, Any]]:
        row = self.db.fetchone(
            "SELECT * FROM governance_events WHERE snapshot_id = ?",
            (snapshot_id,),
        )
        return dict(row) if row else None

    def count(self) -> int:
        return self._count(self.TABLE)
