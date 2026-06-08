"""
EntropyDynamics — L4 Dynamics: How entropy changes over time.

FASM Layer: 4 (Dynamics)
Phenomenon: Architectural Entropy (rate of change)
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class EntropyDynamics(BaseModel):
    """
    L4 — Dynamics: How entropy changes over time.

    This is a nested entity within ArchitecturalStateVector.
    It represents the instantaneous state of entropy dynamics.

    FASM Analysis:
    - Ontology: State, Dynamics
    - Theory: Axioma 2 (Architecture has state)
    - Phenomenon: Architectural Entropy (rate of change)
    - State Dimension: entropy.velocity, entropy.acceleration
    - Metrics: Entropy Velocity, Entropy Acceleration
    - Invariants: velocity and acceleration can be any real number
    - Governance: Predictions depend on correct derivatives
    - Memory: Included in embedding (indices 1, 2)
    """

    # Current state
    current: float = Field(
        default=0.0,
        ge=0,
        description="L3: entropy.current — Accumulated architectural debt (points)"
    )

    # Derivatives
    velocity: float = Field(
        default=0.0,
        description="L3: entropy.velocity — Rate of deterioration (points/day)"
    )
    acceleration: float = Field(
        default=0.0,
        description="L3: entropy.acceleration — Acceleration of deterioration (points/day²)"
    )

    # Polynomial coefficients (for audit/transparency)
    polyfit_a: float = Field(
        default=0.0,
        description="Quadratic coefficient of polyfit"
    )
    polyfit_b: float = Field(
        default=0.0,
        description="Linear coefficient of polyfit"
    )
    polyfit_c: float = Field(
        default=0.0,
        description="Constant coefficient of polyfit"
    )

    # Classification
    gradient_classification: str = Field(
        default="",
        description="L6: Governance classification of gradient"
    )

    @property
    def entropy_first_derivative(self) -> float:
        """
        Deprecated — use velocity instead.

        Kept for backward compatibility.
        Remove in Sprint 4.
        """
        return self.velocity

    @property
    def entropy_second_derivative(self) -> float:
        """
        Deprecated — use acceleration instead.

        Kept for backward compatibility.
        Remove in Sprint 4.
        """
        return self.acceleration
