"""
Snapshot Consistency — roundtrip SQLite preserva dados.

snapshot → sqlite → load → graph/metrics
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest

from ags.core.graph.architectural_graph import ArchitecturalGraph
from ags.core.structural.snapshot import StructuralSnapshot
from ags.core.coupling.snapshot import CouplingReport, ACPResult, DCIResult
from ags.storage.database import Database
from ags.storage.repositories.snapshot_repo import SnapshotRepository
from ags.storage.repositories.coupling_repo import CouplingRepository


@pytest.fixture
def tmp_db():
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    db = Database(db_path)
    yield db
    db.close()
    Path(db_path).unlink(missing_ok=True)


@pytest.fixture
def sample_structural_snapshot() -> StructuralSnapshot:
    return StructuralSnapshot(
        cri_score=72.5,
        architectural_entropy=35.0,
        agp_score=85.0,
        cycle_count=2,
        total_files=150,
        total_lines=12000,
        total_functions=400,
        total_classes=50,
        radon_mi_score=65.0,
        cyclomatic_score=70.0,
        god_object_score=80.0,
        boundary_violation_score=75.0,
        context_cost_score=90.0,
        test_coverage_score=60.0,
        type_coverage_score=45.0,
        agp_domains=["api", "domain", "infra"],
        project_path="/tmp/test",
    )


@pytest.fixture
def sample_coupling_report() -> CouplingReport:
    return CouplingReport(
        acp=ACPResult(
            domain_count=3,
            total_cross_imports=15,
            acp_score=65.0,
            acp_classification="🟡 Acoplamento moderado",
        ),
        dci=DCIResult(
            contamination_ratio=0.25,
            dci_score=75.0,
            dci_classification="🟡 Contaminação leve",
        ),
        context_radius_avg=6.5,
        context_radius_max=12,
        dependency_density=0.15,
        communities_count=3,
    )


class TestSnapshotConsistency:
    def test_structural_snapshot_roundtrip(
        self, tmp_db: Database, sample_structural_snapshot: StructuralSnapshot
    ) -> None:
        repo = SnapshotRepository(tmp_db)
        data = sample_structural_snapshot.model_dump()
        data["project_path"] = "/tmp/test"
        snapshot_id = repo.save(data)

        loaded = repo.get_by_id(snapshot_id)
        assert loaded is not None
        assert loaded["cri_score"] == 72.5
        assert loaded["architectural_entropy"] == 35.0
        assert loaded["agp_score"] == 85.0
        assert loaded["cycle_count"] == 2
        assert loaded["total_files"] == 150
        assert loaded["total_lines"] == 12000

    def test_graph_serialization_in_snapshot(self, tmp_db: Database) -> None:
        g = ArchitecturalGraph()
        g.add_file("a.py", module="m", loc=100)
        g.add_file("b.py", module="m", loc=200)
        g.add_import("a.py", "b.py")
        g.add_module("m")

        graph_json = g.to_json()
        repo = SnapshotRepository(tmp_db)
        snapshot_id = repo.save(
            {"project_path": "/tmp", "cri_score": 50.0},
            graph_json=graph_json,
        )

        loaded = repo.get_by_id(snapshot_id)
        assert loaded is not None
        assert loaded["graph_json"] != ""

        restored_graph = ArchitecturalGraph.from_json(loaded["graph_json"])
        assert restored_graph.file_count == g.file_count
        assert restored_graph.edge_count == g.edge_count

    def test_coupling_report_roundtrip(
        self, tmp_db: Database, sample_coupling_report: CouplingReport
    ) -> None:
        snap_repo = SnapshotRepository(tmp_db)
        snap_id = snap_repo.save({"project_path": "/tmp", "cri_score": 50.0})

        coupling_repo = CouplingRepository(tmp_db)
        report_data = sample_coupling_report.model_dump()
        coupling_repo.save(snap_id, report_data)

        loaded = coupling_repo.get_by_snapshot(snap_id)
        assert loaded is not None
        assert loaded["acp_score"] == 65.0
        assert loaded["dci_score"] == 75.0
        assert loaded["context_radius_avg"] == 6.5
        assert loaded["dependency_density"] == 0.15

    def test_evolution_report_roundtrip(self, tmp_db: Database) -> None:
        from ags.storage.repositories.evolution_repo import EvolutionRepository

        snap_repo = SnapshotRepository(tmp_db)
        snap_id = snap_repo.save({"project_path": "/tmp", "cri_score": 50.0})

        evo_repo = EvolutionRepository(tmp_db)
        report_data = {
            "entropy_gradient": 0.05,
            "entropy_acceleration": 0.01,
            "drift_ratio": 15.0,
            "half_life_months": 18.0,
            "gradient_classification": "degrading",
            "trend": "stable",
            "delta_cri": -3.0,
            "delta_entropy": 5.0,
            "delta_acp": 0.0,
        }
        evo_repo.save(snap_id, report_data)

        loaded = evo_repo.get_by_snapshot(snap_id)
        assert loaded is not None
        assert loaded["entropy_gradient"] == 0.05
        assert loaded["drift_ratio"] == 15.0
        assert loaded["half_life_months"] == 18.0
        assert loaded["gradient_classification"] == "degrading"

    def test_governance_report_roundtrip(self, tmp_db: Database) -> None:
        from ags.storage.repositories.governance_repo import GovernanceRepository

        snap_repo = SnapshotRepository(tmp_db)
        snap_id = snap_repo.save({"project_path": "/tmp", "cri_score": 50.0})

        gov_repo = GovernanceRepository(tmp_db)
        report_data = {
            "merge_allowed": False,
            "gate_status": "BLOCKED: Regressão detectada",
            "violations_count": 5,
            "critical_count": 2,
            "fatal_count": 0,
        }
        gov_repo.save(snap_id, report_data)

        loaded = gov_repo.get_by_snapshot(snap_id)
        assert loaded is not None
        assert loaded["merge_allowed"] == 0
        assert loaded["gate_status"] == "BLOCKED: Regressão detectada"
        assert loaded["violations_count"] == 5
        assert loaded["critical_count"] == 2
