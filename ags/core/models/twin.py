"""
ArchitecturalTwin — Digital Twin of Software Architecture.

This is the long-term concept that combines current state,
historical states, predictions, and governance into a single entity.

FASM Analysis:
- Ontology: Architecture, State, Dynamics, Governance, Memory
- Theory: All axioms (1-8)
- Phenomenon: All phenomena
- State Vector: All dimensions
- Dynamics: velocity, acceleration, drift, regression, half-life
- Metrics: All metrics
- Governance: ALLOW, WARN, BLOCK
- Memory: State History, Similarity, Recall
- Applicability: Structural and dynamic analysis only
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from ags.core.models.state_vector import ArchitecturalStateVector


class EvolutionSummary(BaseModel):
    """
    Summary of architectural evolution over time.

    L4 — Dynamics: How state changes over time.
    """

    current: ArchitecturalStateVector = Field(
        default_factory=ArchitecturalStateVector,
        description="Current architectural state"
    )
    previous: Optional[ArchitecturalStateVector] = Field(
        default=None,
        description="Previous architectural state"
    )
    drift_ratio: float = Field(
        default=0.0,
        ge=0,
        le=1,
        description="Structural divergence from baseline"
    )
    regression_detected: bool = Field(
        default=False,
        description="Whether regression was detected"
    )
    half_life_months: float = Field(
        default=float("inf"),
        description="Time until operational collapse (linear)"
    )


class PredictionSummary(BaseModel):
    """
    Summary of architectural predictions.

    L3 — Prediction: Future state estimation.
    """

    future_states: List[ArchitecturalStateVector] = Field(
        default_factory=list,
        description="Predicted future states"
    )
    confidence: float = Field(
        default=0.0,
        ge=0,
        le=1,
        description="Prediction confidence"
    )
    collapse_probability: float = Field(
        default=0.0,
        ge=0,
        le=1,
        description="Probability of architectural collapse"
    )


class GovernanceSummary(BaseModel):
    """
    Summary of architectural governance.

    L7 — Governance: Decisions based on state.
    """

    merge_allowed: bool = Field(
        default=True,
        description="Whether merge is allowed"
    )
    gate_status: str = Field(
        default="PASS",
        description="Gate status"
    )
    violations: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Active violations"
    )
    budgets: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Budget status"
    )


class ArchitecturalTwin(BaseModel):
    """
    Digital Twin of Software Architecture.

    Combines current state, historical states, predictions,
    and governance into a single observable entity.

    This is the long-term vision for AGS.
    When this is complete, AGS becomes a "Digital Twin Engine
    for Software Architecture."

    FASM Analysis:
    - Ontology: Architecture
    - Theory: All axioms
    - Phenomena: All phenomena
    - State Vector: All dimensions
    - Dynamics: velocity, acceleration, drift, regression, half-life
    - Governance: ALLOW, WARN, BLOCK
    - Memory: State History, Similarity, Recall
    - Applicability: Structural and dynamic analysis
    """

    # Identity
    project_name: str = Field(
        default="",
        description="Project name"
    )
    timestamp: str = Field(
        default="",
        description="Analysis timestamp"
    )

    # State (L4)
    state: ArchitecturalStateVector = Field(
        default_factory=ArchitecturalStateVector,
        description="Current architectural state"
    )

    # Evolution (L4)
    evolution: EvolutionSummary = Field(
        default_factory=EvolutionSummary,
        description="Architectural evolution over time"
    )

    # Prediction (L3)
    prediction: PredictionSummary = Field(
        default_factory=PredictionSummary,
        description="Architectural predictions"
    )

    # Governance (L7)
    governance: GovernanceSummary = Field(
        default_factory=GovernanceSummary,
        description="Architectural governance"
    )

    # Memory (L8)
    historical_states: List[ArchitecturalStateVector] = Field(
        default_factory=list,
        description="Historical state snapshots"
    )

    @property
    def health_status(self) -> str:
        """
        Overall health status based on governance and state.

        Returns:
            "HEALTHY", "DEGRADING", or "COLLAPSING"
        """
        if not self.governance.merge_allowed:
            return "COLLAPSING"

        cri = self.state.cri
        if cri >= 80:
            return "HEALTHY"
        elif cri >= 60:
            return "DEGRADING"
        else:
            return "COLLAPSING"

    @property
    def embedding(self) -> List[float]:
        """
        L8 — Memory: Convert twin to embedding for storage.
        """
        return self.state.to_embedding()

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return self.model_dump()
