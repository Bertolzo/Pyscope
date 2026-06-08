"""
CouplingRepository — Persistência de relatórios de acoplamento.
"""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

from ags.storage.database import Database

from .base import BaseRepository


class CouplingRepository(BaseRepository):
    """Repository para relatórios de acoplamento."""

    TABLE = "coupling_reports"

    def save(self, snapshot_id: int, report_data: Dict[str, Any]) -> int:
        acp = report_data.get("acp", {})
        dci = report_data.get("dci", {})
        data = {
            "snapshot_id": snapshot_id,
            "timestamp": self._now(),
            "acp_score": acp.get("acp_score", 0) if isinstance(acp, dict) else report_data.get("acp_score", 0),
            "acp_classification": acp.get("acp_classification", "") if isinstance(acp, dict) else report_data.get("acp_classification", ""),
            "dci_score": dci.get("dci_score", 0) if isinstance(dci, dict) else report_data.get("dci_score", 0),
            "dci_classification": dci.get("dci_classification", "") if isinstance(dci, dict) else report_data.get("dci_classification", ""),
            "context_radius_avg": report_data.get("context_radius_avg", 0),
            "context_radius_max": report_data.get("context_radius_max", 0),
            "cross_imports": report_data.get("cross_imports", 0),
            "contamination_ratio": report_data.get("contamination_ratio", 0),
            "dependency_density": report_data.get("dependency_density", 0),
            "communities_count": report_data.get("communities_count", 0),
            "full_report": json.dumps(report_data, ensure_ascii=False, default=str),
        }
        return self._save(self.TABLE, data)

    def get_latest(self) -> Optional[Dict[str, Any]]:
        return self._get_latest(self.TABLE)

    def get_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        return self._get_history(self.TABLE, limit)

    def get_by_snapshot(self, snapshot_id: int) -> Optional[Dict[str, Any]]:
        row = self.db.fetchone(
            "SELECT * FROM coupling_reports WHERE snapshot_id = ?",
            (snapshot_id,),
        )
        return dict(row) if row else None

    def get_previous(self, current_snapshot_id: int) -> Optional[Dict[str, Any]]:
        row = self.db.fetchone(
            "SELECT * FROM coupling_reports WHERE snapshot_id < ? ORDER BY snapshot_id DESC LIMIT 1",
            (current_snapshot_id,),
        )
        return dict(row) if row else None

    def count(self) -> int:
        return self._count(self.TABLE)
