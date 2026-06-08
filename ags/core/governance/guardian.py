"""
ArchitecturalGuardian — Camada 7 do AGS.

CI/CD integration, PR analysis, merge gate.
"""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class PRAnalysis(BaseModel):
    new_cycles: int = 0
    new_couplings: int = 0
    entropy_increase: float = 0.0
    cri_regression: float = 0.0
    files_touched: int = 0
    risk_level: str = "🟢 BAIXO"


class GuardianReport(BaseModel):
    """Relatório do Guardian."""

    pr_analysis: Optional[PRAnalysis] = None
    merge_allowed: bool = True
    block_reasons: List[str] = Field(default_factory=list)
    dashboard_data: Dict[str, Any] = Field(default_factory=dict)
    exit_code: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()


class ArchitecturalGuardian:
    """Guardião Arquitetural — Camada 7 do AGS."""

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        self.config = config or {}
        self.snapshot = GuardianReport()

    def analyze(
        self,
        structural_snapshot: Any,
        coupling_snapshot: Any,
        evolution_snapshot: Any,
        governance_snapshot: Any,
        prediction_snapshot: Any = None,
    ) -> GuardianReport:
        self.structural = structural_snapshot
        self.coupling = coupling_snapshot
        self.evolution = evolution_snapshot
        self.governance = governance_snapshot
        self.prediction = prediction_snapshot

        self._analyze_pr_impact()
        self._determine_merge_gate()
        self._generate_dashboard_data()
        self._determine_exit_code()

        return self.snapshot

    def _analyze_pr_impact(self) -> None:
        deltas = getattr(self.evolution, "deltas", None)
        if not deltas:
            self.snapshot.pr_analysis = None
            return

        risk = "🟢 BAIXO"
        trend = getattr(deltas, "trend", "stable")
        if trend == "collapsing":
            risk = "🔴 CRÍTICO"
        elif trend == "degrading":
            risk = "🟠 ALTO"
        elif getattr(deltas, "entropy_delta", 0) > 5:
            risk = "🟡 MÉDIO"

        self.snapshot.pr_analysis = PRAnalysis(
            entropy_increase=getattr(deltas, "entropy_delta", 0),
            cri_regression=getattr(deltas, "cri_delta", 0),
            files_touched=getattr(deltas, "files_added", 0),
            risk_level=risk,
        )

    def _determine_merge_gate(self) -> None:
        reasons: List[str] = []

        if self.governance and not self.governance.merge_allowed:
            reasons.append(self.governance.gate_status)

        if self.prediction and self.prediction.predictions:
            p30 = next(
                (p for p in self.prediction.predictions if p.days == 30), None
            )
            if p30 and p30.predicted_entropy > 80:
                reasons.append(
                    f"🔮 Colapso previsto em 30 dias (E={p30.predicted_entropy:.1f})"
                )

        if self.evolution:
            hl = getattr(self.evolution, "half_life_months", float("inf"))
            if hl != float("inf") and hl < 3:
                reasons.append(f"🚨 Half-life = {hl} meses")

            gc = getattr(self.evolution, "gradient_classification", "")
            if gc == "collapsing":
                reasons.append("📉 Arquitetura em colapso (d²E/dt² > 0)")

        if self.coupling and self.coupling.dci:
            if self.coupling.dci.contamination_ratio > 0.6:
                reasons.append(
                    f"☣️  DCI = {self.coupling.dci.contamination_ratio * 100:.0f}% contaminação"
                )

        if self.coupling and self.coupling.acp:
            if self.coupling.acp.acp_score < 30:
                reasons.append(
                    f"🔗 ACP = {self.coupling.acp.acp_score:.1f} (acoplamento crítico)"
                )

        self.snapshot.block_reasons = reasons
        self.snapshot.merge_allowed = len(reasons) == 0

    def _generate_dashboard_data(self) -> None:
        self.snapshot.dashboard_data = {
            "cri": round(getattr(self.structural, "cri_score", 0), 2),
            "entropy": round(getattr(self.structural, "architectural_entropy", 0), 2),
            "acp": round(self.coupling.acp.acp_score, 2) if self.coupling and self.coupling.acp else 0,
            "dci": round(self.coupling.dci.dci_score, 2) if self.coupling and self.coupling.dci else 0,
            "agp": round(getattr(self.structural, "agp_score", 0), 2),
            "cycles": getattr(self.structural, "cycle_count", 0),
            "gradient": getattr(self.evolution, "gradient_classification", ""),
            "drift_percent": getattr(self.evolution, "drift_ratio", 0),
            "context_radius": self.coupling.context_radius_avg if self.coupling else 0,
            "merge_allowed": self.snapshot.merge_allowed,
            "trend": getattr(
                getattr(self.evolution, "deltas", None), "trend", "unknown"
            ),
        }

    def _determine_exit_code(self) -> None:
        if not self.snapshot.merge_allowed:
            self.snapshot.exit_code = 1
        elif getattr(self.evolution, "gradient_classification", "") == "collapsing":
            self.snapshot.exit_code = 2
        elif self.governance and self.governance.gate_status.startswith("WARNING"):
            self.snapshot.exit_code = 0
        else:
            self.snapshot.exit_code = 0

    def export_for_ci(self, output_path: str) -> None:
        with open(output_path, "w") as f:
            json.dump(self.snapshot.to_dict(), f, indent=2, default=str)
