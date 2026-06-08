"""
EvolutionRepository — Persistência de relatórios de evolução.
"""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

from ags.storage.database import Database

from .base import BaseRepository


class EvolutionRepository(BaseRepository):
    """Repository para relatórios de evolução."""

    TABLE = "evolution_reports"

    def save(self, snapshot_id: int, report_data: Dict[str, Any]) -> int:
        data = {
            "snapshot_id": snapshot_id,
            "timestamp": self._now(),
            "entropy_gradient": report_data.get("entropy_gradient", 0),
            "entropy_acceleration": report_data.get("entropy_acceleration", 0),
            "drift_ratio": report_data.get("drift_ratio", 0),
            "half_life_months": report_data.get("half_life_months", -1),
            "gradient_classification": report_data.get("gradient_classification", ""),
            "trend": report_data.get("trend", "stable"),
            "delta_cri": report_data.get("delta_cri", 0),
            "delta_entropy": report_data.get("delta_entropy", 0),
            "delta_acp": report_data.get("delta_acp", 0),
            "full_report": json.dumps(report_data, ensure_ascii=False, default=str),
        }
        return self._save(self.TABLE, data)

    def get_latest(self) -> Optional[Dict[str, Any]]:
        return self._get_latest(self.TABLE)

    def get_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        return self._get_history(self.TABLE, limit)

    def get_by_snapshot(self, snapshot_id: int) -> Optional[Dict[str, Any]]:
        row = self.db.fetchone(
            "SELECT * FROM evolution_reports WHERE snapshot_id = ?",
            (snapshot_id,),
        )
        return dict(row) if row else None

    def get_gradient_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        rows = self.db.fetchall(
            "SELECT timestamp, entropy_gradient, entropy_acceleration, drift_ratio "
            "FROM evolution_reports ORDER BY timestamp ASC LIMIT ?",
            (limit,),
        )
        return [dict(r) for r in rows]

    def count(self) -> int:
        return self._count(self.TABLE)
