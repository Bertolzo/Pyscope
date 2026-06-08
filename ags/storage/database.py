"""
Database — Conexão SQLite com WAL mode e migration engine.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional

SCHEMA_VERSION = 1

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS metadata (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    project_path TEXT NOT NULL,
    cri_score REAL DEFAULT 0,
    architectural_entropy REAL DEFAULT 0,
    agp_score REAL DEFAULT 0,
    cycle_count INTEGER DEFAULT 0,
    total_files INTEGER DEFAULT 0,
    total_lines INTEGER DEFAULT 0,
    total_functions INTEGER DEFAULT 0,
    total_classes INTEGER DEFAULT 0,
    radon_mi_score REAL DEFAULT 0,
    cyclomatic_score REAL DEFAULT 0,
    god_object_score REAL DEFAULT 0,
    boundary_violation_score REAL DEFAULT 0,
    context_cost_score REAL DEFAULT 0,
    test_coverage_score REAL DEFAULT 0,
    type_coverage_score REAL DEFAULT 0,
    agp_domains TEXT DEFAULT '[]',
    graph_json TEXT,
    full_snapshot TEXT
);

CREATE TABLE IF NOT EXISTS coupling_reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    snapshot_id INTEGER NOT NULL,
    timestamp TEXT NOT NULL,
    acp_score REAL DEFAULT 0,
    acp_classification TEXT DEFAULT '',
    dci_score REAL DEFAULT 0,
    dci_classification TEXT DEFAULT '',
    context_radius_avg REAL DEFAULT 0,
    context_radius_max INTEGER DEFAULT 0,
    cross_imports INTEGER DEFAULT 0,
    contamination_ratio REAL DEFAULT 0,
    dependency_density REAL DEFAULT 0,
    communities_count INTEGER DEFAULT 0,
    full_report TEXT,
    FOREIGN KEY (snapshot_id) REFERENCES snapshots(id)
);

CREATE TABLE IF NOT EXISTS evolution_reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    snapshot_id INTEGER NOT NULL,
    timestamp TEXT NOT NULL,
    entropy_gradient REAL DEFAULT 0,
    entropy_acceleration REAL DEFAULT 0,
    drift_ratio REAL DEFAULT 0,
    half_life_months REAL DEFAULT -1,
    gradient_classification TEXT DEFAULT '',
    trend TEXT DEFAULT 'stable',
    delta_cri REAL DEFAULT 0,
    delta_entropy REAL DEFAULT 0,
    delta_acp REAL DEFAULT 0,
    full_report TEXT,
    FOREIGN KEY (snapshot_id) REFERENCES snapshots(id)
);

CREATE TABLE IF NOT EXISTS governance_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    snapshot_id INTEGER NOT NULL,
    timestamp TEXT NOT NULL,
    merge_allowed INTEGER DEFAULT 1,
    gate_status TEXT DEFAULT '',
    violations_count INTEGER DEFAULT 0,
    critical_count INTEGER DEFAULT 0,
    fatal_count INTEGER DEFAULT 0,
    full_report TEXT,
    FOREIGN KEY (snapshot_id) REFERENCES snapshots(id)
);

CREATE TABLE IF NOT EXISTS predictions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    snapshot_id INTEGER NOT NULL,
    timestamp TEXT NOT NULL,
    collapse_probability_90d REAL DEFAULT 0,
    ai_maintainability_tokens REAL DEFAULT 0,
    predictions_30d TEXT DEFAULT '{}',
    predictions_60d TEXT DEFAULT '{}',
    predictions_90d TEXT DEFAULT '{}',
    full_report TEXT,
    FOREIGN KEY (snapshot_id) REFERENCES snapshots(id)
);

CREATE TABLE IF NOT EXISTS pull_request_reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    pr_id TEXT DEFAULT '',
    merge_allowed INTEGER DEFAULT 1,
    cri_before REAL DEFAULT 0,
    cri_after REAL DEFAULT 0,
    entropy_before REAL DEFAULT 0,
    entropy_after REAL DEFAULT 0,
    block_reasons TEXT DEFAULT '[]',
    exit_code INTEGER DEFAULT 0,
    full_report TEXT
);
"""


class Database:
    """Conexão SQLite com WAL mode."""

    def __init__(self, db_path: str = "ags_data.db") -> None:
        self.db_path = Path(db_path)
        self._conn: Optional[sqlite3.Connection] = None
        self.connect()

    def connect(self) -> None:
        self._conn = sqlite3.connect(str(self.db_path))
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._conn.execute("PRAGMA foreign_keys=ON")
        self._migrate()

    def close(self) -> None:
        if self._conn:
            self._conn.close()
            self._conn = None

    def _migrate(self) -> None:
        current = self._get_schema_version()
        if current < SCHEMA_VERSION:
            self._conn.executescript(SCHEMA_SQL)
            self._set_schema_version(SCHEMA_VERSION)

    def _get_schema_version(self) -> int:
        try:
            row = self._conn.execute(
                "SELECT value FROM metadata WHERE key = 'schema_version'"
            ).fetchone()
            return int(row["value"]) if row else 0
        except sqlite3.OperationalError:
            return 0

    def _set_schema_version(self, version: int) -> None:
        self._conn.execute(
            "INSERT OR REPLACE INTO metadata (key, value) VALUES (?, ?)",
            ("schema_version", str(version)),
        )
        self._conn.commit()

    def execute(self, sql: str, params: Any = ()) -> sqlite3.Cursor:
        assert self._conn is not None, "Database not connected"
        return self._conn.execute(sql, params)

    def executemany(self, sql: str, params_list: List[Any]) -> sqlite3.Cursor:
        assert self._conn is not None, "Database not connected"
        return self._conn.executemany(sql, params_list)

    def fetchone(self, sql: str, params: Any = ()) -> Optional[sqlite3.Row]:
        assert self._conn is not None, "Database not connected"
        return self._conn.execute(sql, params).fetchone()

    def fetchall(self, sql: str, params: Any = ()) -> List[sqlite3.Row]:
        assert self._conn is not None, "Database not connected"
        return self._conn.execute(sql, params).fetchall()

    def commit(self) -> None:
        assert self._conn is not None, "Database not connected"
        self._conn.commit()

    def __enter__(self) -> Database:
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()
