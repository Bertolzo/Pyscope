"""
AGS v2 — Orchestrator.

Pipeline: Graph → Core → Intelligence → Storage → Report
"""

from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from ags.core.coupling.analyzer import CouplingAnalyzer
from ags.core.graph.builders import GraphBuilder
from ags.core.governance.engine import GovernanceEngine
from ags.core.governance.guardian import ArchitecturalGuardian
from ags.core.structural.analyzer import StructuralAnalyzer
from ags.intelligence.evolution.analyzer import EvolutionAnalyzer
from ags.intelligence.prediction.engine import PredictionEngine
from ags.storage.database import Database
from ags.storage.repositories.coupling_repo import CouplingRepository
from ags.storage.repositories.evolution_repo import EvolutionRepository
from ags.storage.repositories.governance_repo import GovernanceRepository
from ags.storage.repositories.snapshot_repo import SnapshotRepository

logger = logging.getLogger(__name__)


class AGS:
    """
    Architectural Governance System v2

    Pipeline:
      1. GraphBuilder → ArchitecturalGraph
      2. StructuralAnalyzer → StructuralSnapshot
      3. CouplingAnalyzer → CouplingReport
      4. EvolutionAnalyzer → EvolutionReport
      5. GovernanceEngine → GovernanceReport
      6. PredictionEngine → PredictionReport
      7. ArchitecturalGuardian → GuardianReport
    """

    def __init__(
        self,
        project_path: str,
        config: Optional[Dict[str, Any]] = None,
        db_path: str = "ags_data.db",
    ) -> None:
        self.project_path = Path(project_path).resolve()
        self.config = config or self._default_config()
        self.db = Database(db_path)

        self.snapshot_repo = SnapshotRepository(self.db)
        self.coupling_repo = CouplingRepository(self.db)
        self.evolution_repo = EvolutionRepository(self.db)
        self.governance_repo = GovernanceRepository(self.db)

        self.structural = None
        self.coupling = None
        self.evolution = None
        self.governance = None
        self.prediction = None
        self.guardian = None
        self.graph = None

    def _default_config(self) -> Dict[str, Any]:
        return {
            "max_file_lines": 300,
            "max_class_lines": 200,
            "max_function_lines": 40,
            "max_cyclomatic_complexity": 10,
            "max_context_cost": 1500,
            "weight_radon_mi": 0.15,
            "weight_cyclomatic": 0.15,
            "weight_god_objects": 0.15,
            "weight_boundary_violations": 0.20,
            "weight_context_cost": 0.20,
            "weight_test_coverage": 0.10,
            "weight_type_coverage": 0.05,
            "penalty_syspath_insert": 10,
            "penalty_syspath_append": 5,
            "penalty_relative_deep_import": 3,
            "penalty_cross_module_import": 2,
            "penalty_domain_imports_infra": 4,
            "penalty_star_import": 2,
            "penalty_missing_init": 1,
            "penalty_large_file": 3,
            "penalty_very_large_file": 5,
            "penalty_god_class": 4,
            "penalty_super_god_class": 6,
            "penalty_hardcoded_path": 5,
            "penalty_secret_in_code": 10,
            "penalty_cycle": 8,
            "penalty_agp_high": 3,
            "acp_max_cross_imports_per_domain": 5,
            "dci_threshold": 0.30,
            "half_life_critical_months": 3.0,
            "prediction_days": [30, 60, 90],
            "entropy_budget": 100,
            "domain_budget": 5,
            "regression_cri_threshold": 5,
            "regression_entropy_threshold": 10,
            "agp_max_domains": 3,
            "layer_order": [
                "domain", "core", "application", "service", "usecase",
                "adapter", "infra", "infrastructure", "api", "web", "cli", "main",
            ],
            "agp_domain_keywords": {
                "agents": ["agent", "bot", "worker", "task", "orchestrator"],
                "runtime": ["runtime", "executor", "scheduler", "loop", "engine"],
                "security": ["security", "auth", "rbac", "permission", "encrypt", "audit"],
                "eval": ["eval", "benchmark", "judge", "score", "metric", "test"],
                "mcp": ["mcp", "server", "protocol", "tool"],
                "web": ["web", "api", "http", "fastapi", "flask", "endpoint"],
                "vector": ["vector", "embedding", "retrieval", "store", "index"],
                "infra": ["docker", "deploy", "ci", "cd", "terraform", "k8s"],
            },
            "responsibility_keywords": {
                "auth": ["auth", "login", "token", "jwt", "oauth", "session"],
                "cache": ["cache", "redis", "memcached", "ttl", "expire"],
                "db": ["database", "db", "sql", "query", "orm", "repository"],
                "http": ["http", "request", "response", "api", "rest", "endpoint"],
                "config": ["config", "settings", "env", "cfg", "constant"],
                "ml": ["model", "inference", "predict", "train", "embedding", "vector"],
            },
        }

    def analyze(self) -> Dict[str, Any]:
        """Pipeline completo das 6 camadas."""
        print(f"\n🔍 AGS v2 — Architectural Governance System")
        print(f"📁 Projeto: {self.project_path}")
        print()

        # Camada 1: Graph
        print("[1/6] Graph Builder...")
        builder = GraphBuilder(str(self.project_path), self.config)
        self.graph = builder.build()
        print(f"      Files: {self.graph.file_count} | Modules: {self.graph.module_count} | Edges: {self.graph.edge_count}")

        # Camada 2: Structural Analysis
        print("[2/6] Structural Analysis...")
        structural_analyzer = StructuralAnalyzer(self.graph, self.config)
        self.structural = structural_analyzer.analyze()
        print(f"      CRI: {self.structural.cri_score:.2f} | Entropy: {self.structural.architectural_entropy:.2f} | AGP: {self.structural.agp_score:.2f}")

        # Camada 3: Coupling Intelligence
        print("[3/6] Coupling Intelligence...")
        coupling_analyzer = CouplingAnalyzer(self.graph, self.config)
        self.coupling = coupling_analyzer.analyze()
        acp_score = self.coupling.acp.acp_score if self.coupling.acp else 0
        dci_score = self.coupling.dci.dci_score if self.coupling.dci else 0
        print(f"      ACP: {acp_score:.2f} | DCI: {dci_score:.2f} | Radius: {self.coupling.context_radius_avg:.1f}")

        # Carregar histórico para Evolution e Prediction
        history = self.snapshot_repo.get_history_for_forecast(limit=100)

        # Camada 4: Evolution Intelligence
        print("[4/6] Evolution Intelligence...")
        evolution_analyzer = EvolutionAnalyzer(self.config)
        self.evolution = evolution_analyzer.analyze(
            self.structural, self.coupling, history,
            project_modules=list(self.graph.modules.keys()),
        )
        print(f"      dE/dt: {self.evolution.entropy_first_derivative:.4f} | Gradient: {self.evolution.gradient_classification}")

        # Camada 5: Prediction Engine
        print("[5/6] Prediction Engine...")
        prediction_engine = PredictionEngine(self.config)
        self.prediction = prediction_engine.analyze(
            self.structural, self.coupling, self.evolution, history
        )
        if self.prediction.predictions:
            p90 = next((p for p in self.prediction.predictions if p.days == 90), None)
            if p90:
                print(f"      90d: E={p90.predicted_entropy:.1f} | Risk: {p90.risk_level} | Collapse prob: {self.prediction.collapse_probability_90d:.0%}")

        # Camada 6: Governance + Guardian
        print("[6/6] Governance + Guardian...")
        previous_structural = self._load_previous_structural()
        governance_engine = GovernanceEngine(self.config)
        self.governance = governance_engine.analyze(
            self.structural, self.coupling, self.evolution, previous_structural
        )
        print(f"      Merge: {'✅ ALLOWED' if self.governance.merge_allowed else '❌ BLOCKED'} | {self.governance.gate_status}")

        guardian = ArchitecturalGuardian(self.config)
        self.guardian = guardian.analyze(
            self.structural, self.coupling, self.evolution, self.governance, self.prediction
        )
        print(f"      Exit code: {self.guardian.exit_code}")

        # Persistir no SQLite
        print()
        print("💾 Persistindo no SQLite...")
        self._persist_results()

        return self._compile_report()

    def _load_previous_structural(self) -> Optional[Any]:
        latest = self.snapshot_repo.get_latest()
        if not latest:
            return None

        from ags.core.structural.snapshot import StructuralSnapshot

        try:
            full = json.loads(latest.get("full_snapshot", "{}"))
            return StructuralSnapshot(**full)
        except Exception:
            return None

    def _persist_results(self) -> None:
        from ags.core.structural.snapshot import StructuralSnapshot

        snapshot_data = self.structural.model_dump() if hasattr(self.structural, "model_dump") else {}
        snapshot_data["project_path"] = str(self.project_path)

        graph_json = self.graph.to_json() if self.graph else ""
        snapshot_id = self.snapshot_repo.save(snapshot_data, graph_json)

        coupling_data = self.coupling.to_dict() if self.coupling else {}
        self.coupling_repo.save(snapshot_id, coupling_data)

        evolution_data = self.evolution.to_dict() if self.evolution else {}
        self.evolution_repo.save(snapshot_id, evolution_data)

        governance_data = self.governance.to_dict() if self.governance else {}
        self.governance_repo.save(snapshot_id, governance_data)

        print(f"      Snapshot #{snapshot_id} salvo")

    def _compile_report(self) -> Dict[str, Any]:
        return {
            "timestamp": datetime.now().isoformat(),
            "project_path": str(self.project_path),
            "structural": self.structural.to_dict() if self.structural else {},
            "coupling": self.coupling.to_dict() if self.coupling else {},
            "evolution": self.evolution.to_dict() if self.evolution else {},
            "governance": self.governance.to_dict() if self.governance else {},
            "prediction": self.prediction.to_dict() if self.prediction else {},
            "guardian": self.guardian.to_dict() if self.guardian else {},
        }

    def print_report(self) -> None:
        if not self.structural:
            print("Execute analyze() primeiro.")
            return

        print()
        print("╔" + "═" * 78 + "╗")
        print("║" + " " * 20 + "AGS v2 — ARCHITECTURAL GOVERNANCE SYSTEM" + " " * 18 + "║")
        print("╚" + "═" * 78 + "╝")

        # Structural
        print("┌" + "─" * 78 + "┐")
        print("│  🧠 STRUCTURAL ANALYSIS                                                     │")
        print("├" + "─" * 78 + "┤")
        print(f"│  {'CRI':45s} {self.structural.cri_score:6.2f}  {self._bar(self.structural.cri_score)}  │")
        print(f"│  {'Entropy':45s} {self.structural.architectural_entropy:6.2f}  {self._bar(max(0, 100 - self.structural.architectural_entropy))}  │")
        print(f"│  {'AGP':45s} {self.structural.agp_score:6.2f}  {self._bar(self.structural.agp_score)}  │")
        print(f"│  {'Cycles':45s} {self.structural.cycle_count:6d}  │")
        print(f"│  {'Files':45s} {self.structural.total_files:6d}  │")
        print(f"│  {'Lines':45s} {self.structural.total_lines:6,}  │")
        print("└" + "─" * 78 + "┘")

        # Coupling
        if self.coupling:
            print("┌" + "─" * 78 + "┐")
            print("│  🔗 COUPLING INTELLIGENCE                                                   │")
            print("├" + "─" * 78 + "┤")
            if self.coupling.acp:
                print(f"│  {'ACP':45s} {self.coupling.acp.acp_score:6.2f}  {self._bar(self.coupling.acp.acp_score)}  │")
            if self.coupling.dci:
                print(f"│  {'DCI':45s} {self.coupling.dci.dci_score:6.2f}  {self._bar(self.coupling.dci.dci_score)}  │")
            print(f"│  {'Context Radius':45s} {self.coupling.context_radius_avg:6.2f}  │")
            print("└" + "─" * 78 + "┘")

        # Governance
        if self.governance:
            print("┌" + "─" * 78 + "┐")
            print("│  🛡️  GOVERNANCE LAYER                                                       │")
            print("├" + "─" * 78 + "┤")
            print(f"│  {'Merge Gate':45s} {'✅ ALLOWED' if self.governance.merge_allowed else '❌ BLOCKED':>30s}  │")
            print(f"│  {'Status':45s} {self.governance.gate_status:>30s}  │")
            print("├" + "─" * 78 + "┤")
            print("│  BUDGETS:                                                                   │")
            for b in self.governance.budgets:
                icon = "🟢" if b.status == "ok" else "🟡" if b.status == "warning" else "🔴"
                print(f"│  {icon} {b.name:10s} {b.current:.1f}/{b.limit:.1f} ({b.percentage:.1f}%)  │")
            print("├" + "─" * 78 + "┤")
            print("│  VIOLATIONS:                                                                │")
            for severity in ["FATAL", "CRITICAL", "ERROR", "WARNING", "INFO"]:
                count = sum(1 for v in self.governance.violations if v.severity == severity)
                if count > 0:
                    icon_map = {"FATAL": "💀", "CRITICAL": "🔴", "ERROR": "🟠", "WARNING": "🟡", "INFO": "🔵"}
                    print(f"│  {icon_map[severity]} {severity:10s}: {count:3d}                                          │")
            print("└" + "─" * 78 + "┘")

        # Predictions
        if self.prediction and self.prediction.predictions:
            print("┌" + "─" * 78 + "┐")
            print("│  🔮 PREDICTION ENGINE                                                       │")
            print("├" + "─" * 78 + "┤")
            for p in self.prediction.predictions:
                print(f"│  {p.days:3d}d: E={p.predicted_entropy:6.2f} CRI={p.predicted_cri:6.2f}  conf={p.confidence:.0%}  {p.risk_level:>15s}  │")
            print("├" + "─" * 78 + "┤")
            print(f"│  {'Probabilidade de colapso (90d)':45s} {self.prediction.collapse_probability_90d:>29.0%}  │")
            print("└" + "─" * 78 + "┘")

        # Guardian
        if self.guardian:
            print("┌" + "─" * 78 + "┐")
            print("│  🛡️  ARCHITECTURAL GUARDIAN                                                 │")
            print("├" + "─" * 78 + "┤")
            if self.guardian.block_reasons:
                print("│  BLOCK REASONS:                                                             │")
                for reason in self.guardian.block_reasons[:5]:
                    print(f"│    • {reason:72s}  │")
            print(f"│  {'Exit Code':45s} {self.guardian.exit_code:>30d}  │")
            print("└" + "─" * 78 + "┘")

    def _bar(self, value: float, width: int = 10) -> str:
        filled = int((value / 100) * width)
        filled = max(0, min(filled, width))
        if value >= 70:
            char = "█"
        elif value >= 50:
            char = "▓"
        elif value >= 30:
            char = "▒"
        else:
            char = "░"
        return char * filled + "░" * (width - filled)

    def export_json(self, output_path: str) -> None:
        report = self._compile_report()
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False, default=str)
        print(f"💾 Relatório exportado: {output_path}")

    def close(self) -> None:
        self.db.close()

    def __enter__(self) -> AGS:
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()
