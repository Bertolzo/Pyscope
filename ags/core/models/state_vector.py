"""
ArchitecturalStateVector — L3 State Vector: Minimal representation of architecture at time t.

FASM Layer: 3 (State Vector)
Phenomena: All architectural phenomena
"""

from __future__ import annotations

from typing import TYPE_CHECKING, List

from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from ags.intelligence.evolution.models import EntropyDynamics


class ArchitecturalStateVector(BaseModel):
    """
    L3 — State Vector: Minimal representation of architecture at time t.

    This is the canonical representation of architectural state.
    All AGS metrics are projections of this vector.
    All Governance decisions consume this vector.
    All Memory operations store this vector.

    FASM Analysis:
    - Ontology: State
    - Theory: Axioma 2 (Architecture has state)
    - Phenomena: All architectural phenomena
    - State Dimensions: All dimensions of S(t)
    - Metrics: All metrics are projections
    - Invariants: See individual field constraints
    - Governance: Consumes this vector
    - Memory: Stores embedding of this vector
    """

    # Entropy Dynamics (nested entity)
    # Using Any type to avoid circular import issues
    # The actual type is EntropyDynamics
    entropy: "EntropyDynamics" = Field(
        default_factory=lambda: _get_entropy_dynamics_default(),
        description="L2: Architectural Entropy phenomenon"
    )

    # Coupling
    acp: float = Field(
        default=0.0,
        ge=0,
        le=100,
        description="L2: Structural Pressure phenomenon (%)"
    )
    dci: float = Field(
        default=0.0,
        ge=0,
        le=100,
        description="L2: Structural Cohesion phenomenon (%)"
    )
    boundary_leakage: float = Field(
        default=0.0,
        ge=0,
        le=1,
        description="L2: Operational Leakage phenomenon (ratio)"
    )

    # Composition
    cri: float = Field(
        default=100.0,
        ge=0,
        le=100,
        description="L2: Architectural Integrity phenomenon (score)"
    )
    agp: float = Field(
        default=100.0,
        ge=0,
        le=100,
        description="L2: Governance Compliance phenomenon (%)"
    )

    # Structural
    context_radius: int = Field(
        default=0,
        ge=0,
        description="L2: Architectural Reachability phenomenon (files)"
    )
    dependency_density: float = Field(
        default=0.0,
        ge=0,
        le=1,
        description="Coupling Intensity (ratio)"
    )

    def to_embedding(self) -> List[float]:
        """
        L7 — Memory: Convert to vector for embedding.

        This method enables the State Vector to be stored in vector stores.
        The mechanism (sqlite-vec, FAISS, pgvector) is an implementation detail.
        """
        return [
            self.entropy.current,
            self.entropy.velocity,
            self.entropy.acceleration,
            self.acp,
            self.dci,
            self.boundary_leakage,
            self.cri,
            self.agp,
            float(self.context_radius),
            self.dependency_density,
        ]

    @property
    def embedding_dimension(self) -> int:
        """Return the dimension of the embedding vector."""
        return 10


def _get_entropy_dynamics_default():
    """Get default EntropyDynamics to avoid circular import."""
    from ags.intelligence.evolution.models import EntropyDynamics
    return EntropyDynamics()


# Rebuild model to resolve forward references
def _rebuild_model():
    """Rebuild model after all imports are available."""
    from ags.intelligence.evolution.models import EntropyDynamics
    ArchitecturalStateVector.model_rebuild()


# Auto-rebuild on import
try:
    _rebuild_model()
except Exception:
    # If rebuild fails, it will be retried when the model is used
    pass
