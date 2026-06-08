"""
SnapshotRepository — Persistência de snapshots estruturais.
"""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

from ags.storage.database import Database

from .base import BaseRepository


class SnapshotRepository(BaseRepository):
    """Repository para snapshots estruturais."""

    TABLE = "snapshots"

    def save(self, snapshot_data: Dict[str, Any], graph_json: str = "") -> int:
        data = {
            "timestamp": self._now(),
            "project_path": snapshot_data.get("project_path", ""),
            "cri_score": snapshot_data.get("cri_score", 0),
            "architectural_entropy": snapshot_data.get("architectural_entropy", 0),
            "agp_score": snapshot_data.get("agp_score", 0),
            "cycle_count": snapshot_data.get("cycle_count", 0),
            "total_files": snapshot_data.get("total_files", 0),
            "total_lines": snapshot_data.get("total_lines", 0),
            "total_functions": snapshot_data.get("total_functions", 0),
            "total_classes": snapshot_data.get("total_classes", 0),
            "radon_mi_score": snapshot_data.get("radon_mi_score", 0),
            "cyclomatic_score": snapshot_data.get("cyclomatic_score", 0),
            "god_object_score": snapshot_data.get("god_object_score", 0),
            "boundary_violation_score": snapshot_data.get("boundary_violation_score", 0),
            "context_cost_score": snapshot_data.get("context_cost_score", 0),
            "test_coverage_score": snapshot_data.get("test_coverage_score", 0),
            "type_coverage_score": snapshot_data.get("type_coverage_score", 0),
            "agp_domains": json.dumps(snapshot_data.get("agp_domains", [])),
            "graph_json": graph_json,
            "full_snapshot": json.dumps(snapshot_data, ensure_ascii=False, default=str),
        }
        return self._save(self.TABLE, data)

    def get_latest(self) -> Optional[Dict[str, Any]]:
        return self._get_latest(self.TABLE)

    def get_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        return self._get_history(self.TABLE, limit)

    def get_by_id(self, snapshot_id: int) -> Optional[Dict[str, Any]]:
        return self._get_by_id(self.TABLE, snapshot_id)

    def get_range(self, start: str, end: str) -> List[Dict[str, Any]]:
        return self._get_range(self.TABLE, start, end)

    def get_history_for_forecast(self, limit: int = 365) -> List[Dict[str, Any]]:
        rows = self.db.fetchall(
            "SELECT * FROM snapshots ORDER BY timestamp ASC LIMIT ?",
            (limit,),
        )
        return [dict(r) for r in rows]

    def count(self) -> int:
        return self._count(self.TABLE)
