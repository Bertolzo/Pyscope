"""
EvolutionAnalyzer — L2 Evolution: State over time → Movement.

FASM Layer: 2 (Evolution)
Phenomenon: Architectural Entropy (rate of change)
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

import numpy as np
from pydantic import BaseModel, Field

from ags.intelligence.evolution.models import EntropyDynamics

logger = logging.getLogger(__name__)


class DeltaResult(BaseModel):
    cri_delta: float = 0.0
    entropy_delta: float = 0.0
    acp_delta: float = 0.0
    dci_delta: float = 0.0
    files_added: int = 0
    lines_added: int = 0
    trend: str = "stable"


class EvolutionReport(BaseModel):
    """
    L2 — Evolution Report: State over time → Movement.

    FASM Analysis:
    - Ontology: Dynamics
    - Theory: Axioma 3 (Architecture changes)
    - Phenomenon: Architectural Entropy (rate of change)
    - State Dimensions: entropy.velocity, entropy.acceleration
    - Metrics: Entropy Velocity, Entropy Acceleration
    - Governance: Predictions depend on correct derivatives
    - Memory: Included in embedding
    """

    # Canonical fields (L3 State Vector)
    entropy_dynamics: EntropyDynamics = Field(
        default_factory=EntropyDynamics,
        description="L3: Entropy dynamics (nested in State Vector)"
    )

    # Other evolution fields
    deltas: Optional[DeltaResult] = None
    gradient_classification: str = ""
    drift_ratio: float = 0.0
    drift_classification: str = ""
    original_modules: List[str] = Field(default_factory=list)
    current_modules: List[str] = Field(default_factory=list)
    half_life_months: float = -1.0
    half_life_classification: str = ""

    # Backward-compatible aliases (deprecated — remove in Sprint 4)
    @property
    def entropy_first_derivative(self) -> float:
        """Deprecated — use entropy_dynamics.velocity instead."""
        return self.entropy_dynamics.velocity

    @property
    def entropy_second_derivative(self) -> float:
        """Deprecated — use entropy_dynamics.acceleration instead."""
        return self.entropy_dynamics.acceleration

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()


class EvolutionAnalyzer:
    """Analisador de evolução — consome histórico do SQLite."""

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        self.config = config or {}
        self.snapshot = EvolutionReport()

    def analyze(
        self,
        current_structural: Any,
        current_coupling: Any,
        history: List[Dict[str, Any]],
        project_modules: Optional[List[str]] = None,
    ) -> EvolutionReport:
        self.current_structural = current_structural
        self.current_coupling = current_coupling
        self.history = history
        self.project_modules = project_modules or []

        self._calculate_deltas()
        self._calculate_entropy_gradient()
        self._calculate_architectural_drift()
        self._calculate_half_life()

        return self.snapshot

    def _calculate_deltas(self) -> None:
        if not self.history:
            self.snapshot.deltas = None
            return

        last = self.history[-1]

        cri_current = getattr(self.current_structural, "cri_score", 0)
        cri_previous = last.get("cri_score", cri_current)
        cri_delta = cri_current - cri_previous

        entropy_current = getattr(self.current_structural, "architectural_entropy", 0)
        entropy_previous = last.get("architectural_entropy", entropy_current)
        entropy_delta = entropy_current - entropy_previous

        files_current = getattr(self.current_structural, "total_files", 0)
        files_previous = last.get("total_files", files_current)
        files_added = files_current - files_previous

        lines_current = getattr(self.current_structural, "total_lines", 0)
        lines_previous = last.get("total_lines", lines_current)
        lines_added = lines_current - lines_previous

        if cri_delta > 5 and entropy_delta < -10:
            trend = "improving"
        elif cri_delta < -5 or entropy_delta > 10:
            trend = "collapsing" if entropy_delta > 20 else "degrading"
        else:
            trend = "stable"

        self.snapshot.deltas = DeltaResult(
            cri_delta=round(cri_delta, 2),
            entropy_delta=round(entropy_delta, 2),
            files_added=files_added,
            lines_added=lines_added,
            trend=trend,
        )

    def _calculate_entropy_gradient(self) -> None:
        """
        L2 — Dynamics: Calculate entropy velocity and acceleration.

        FASM Analysis:
        - Ontology: State, Dynamics
        - Theory: Axioma 2 (Architecture has state)
        - Phenomenon: Architectural Entropy (rate of change)
        - State Dimensions: entropy.velocity, entropy.acceleration
        - Metrics: Entropy Velocity (points/day), Entropy Acceleration (points/day²)
        - Invariants: velocity and acceleration can be any real number
        - Governance: Predictions depend on correct derivatives
        - Memory: Included in embedding (indices 1, 2)
        """
        if len(self.history) < 2:
            self.snapshot.entropy_dynamics = EntropyDynamics(
                gradient_classification="stable (sem histórico)"
            )
            return

        entropies = [h.get("architectural_entropy", h.get("entropy", 0)) for h in self.history[-10:]]

        if len(entropies) < 2:
            self.snapshot.entropy_dynamics = EntropyDynamics(
                gradient_classification="stable (dados insuficientes)"
            )
            return

        x = np.arange(len(entropies), dtype=float)
        y = np.array(entropies, dtype=float)

        coeffs = np.polyfit(x, y, min(2, len(entropies) - 1))

        # Extract polynomial coefficients: E(t) = a*t² + b*t + c
        a = float(coeffs[0]) if len(coeffs) > 0 else 0.0
        b = float(coeffs[1]) if len(coeffs) > 1 else 0.0
        c = float(coeffs[2]) if len(coeffs) > 2 else 0.0

        # Calculate derivatives at current time
        t_now = float(len(entropies) - 1)

        # dE/dt = 2*a*t + b (velocity at current time)
        velocity = 2 * a * t_now + b

        # d²E/dt² = 2*a (acceleration, constant for quadratic)
        acceleration = 2 * a

        # Current entropy (last measured value)
        current_entropy = float(entropies[-1])

        # Classify gradient
        if abs(velocity) < 0.1:
            gradient_classification = "stable"
        elif velocity > 0 and acceleration > 0:
            gradient_classification = "collapsing"
        elif velocity > 0 and acceleration <= 0:
            gradient_classification = "degrading"
        elif velocity < 0:
            gradient_classification = "recovering"
        else:
            gradient_classification = "stable"

        # Create EntropyDynamics
        self.snapshot.entropy_dynamics = EntropyDynamics(
            current=current_entropy,
            velocity=round(velocity, 4),
            acceleration=round(acceleration, 6),
            polyfit_a=round(a, 6),
            polyfit_b=round(b, 6),
            polyfit_c=round(c, 6),
            gradient_classification=gradient_classification,
        )

    def _calculate_architectural_drift(self) -> None:
        baseline_modules: List[str] = []

        if self.history:
            first = self.history[0]
            baseline_modules = first.get("agp_domains", first.get("project_modules", []))

        if not baseline_modules:
            baseline_modules = self.project_modules.copy()

        self.snapshot.original_modules = baseline_modules
        self.snapshot.current_modules = self.project_modules.copy()

        added = set(self.project_modules) - set(baseline_modules)

        if baseline_modules:
            drift_ratio = len(added) / len(baseline_modules) * 100
        else:
            drift_ratio = 0

        self.snapshot.drift_ratio = round(drift_ratio, 2)

        if drift_ratio < 20:
            self.snapshot.drift_classification = "🟢 Estrutura estável"
        elif drift_ratio < 50:
            self.snapshot.drift_classification = "🟡 Crescimento controlado"
        elif drift_ratio < 100:
            self.snapshot.drift_classification = "🟠 Drift significativo"
        else:
            self.snapshot.drift_classification = "🔴 Arquitetura completamente diferente"

    def _calculate_half_life(self) -> None:
        """
        L4 — Dynamics: Calculate half-life (linear extrapolation).

        FASM Analysis:
        - Ontology: Dynamics
        - Theory: Axioma 5 (Half-Life is not prediction)
        - Phenomenon: Architectural Entropy (rate of change)
        - State Dimensions: entropy.velocity
        - Metrics: Half-Life (months)
        - Invariants: half_life > 0 or half_life = inf
        - Governance: Operational indicator for urgency
        - Memory: Not directly embedded
        """
        velocity = self.snapshot.entropy_dynamics.velocity
        current_entropy = getattr(self.current_structural, "architectural_entropy", 0)

        if velocity <= 0:
            self.snapshot.half_life_months = float("inf")
            self.snapshot.half_life_classification = "🟢 Arquitetura se recuperando"
            return

        target_entropy = min(100, current_entropy * 2)
        days_to_target = (target_entropy - current_entropy) / velocity
        months = days_to_target / 30.0

        self.snapshot.half_life_months = round(months, 2)

        if months > 12:
            self.snapshot.half_life_classification = "🟢 Half-life > 1 ano"
        elif months > 6:
            self.snapshot.half_life_classification = "🟡 Half-life 6-12 meses"
        elif months > 3:
            self.snapshot.half_life_classification = "🟠 Half-life 3-6 meses"
        else:
            self.snapshot.half_life_classification = "🔴 Half-life < 3 meses (CRÍTICO)"
