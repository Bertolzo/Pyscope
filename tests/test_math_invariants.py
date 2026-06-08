"""
Mathematical Invariants Tests — FASM Layer 5 (Metrics).

These tests validate universal invariants that must hold true
for all architectural states.

FASM Analysis:
- Ontology: State
- Theory: All axioms
- Phenomena: All phenomena
- State Dimensions: All dimensions
- Invariants: Universal constraints
- Governance: Correct classification
- Memory: Valid embeddings
"""

from __future__ import annotations

import pytest

from ags.core.models.state_vector import ArchitecturalStateVector
from ags.intelligence.evolution.models import EntropyDynamics


class TestEntropyInvariants:
    """Test invariants for Architectural Entropy."""

    def test_entropy_never_negative(self):
        """Entropy must be >= 0 (Axioma 1: Entropy is cumulative)."""
        state = ArchitecturalStateVector(
            entropy=EntropyDynamics(current=0.0)
        )
        assert state.entropy.current >= 0

    def test_entropy_velocity_unbounded(self):
        """Entropy velocity can be any real number."""
        state = ArchitecturalStateVector(
            entropy=EntropyDynamics(velocity=100.0)
        )
        assert state.entropy.velocity == 100.0

        state = ArchitecturalStateVector(
            entropy=EntropyDynamics(velocity=-100.0)
        )
        assert state.entropy.velocity == -100.0

    def test_entropy_acceleration_unbounded(self):
        """Entropy acceleration can be any real number."""
        state = ArchitecturalStateVector(
            entropy=EntropyDynamics(acceleration=50.0)
        )
        assert state.entropy.acceleration == 50.0

        state = ArchitecturalStateVector(
            entropy=EntropyDynamics(acceleration=-50.0)
        )
        assert state.entropy.acceleration == -50.0


class TestACPBounded:
    """Test invariants for ACP (Structural Coupling Pressure)."""

    def test_acp_lower_bound(self):
        """ACP must be >= 0."""
        state = ArchitecturalStateVector(acp=0.0)
        assert state.acp >= 0

    def test_acp_upper_bound(self):
        """ACP must be <= 100."""
        state = ArchitecturalStateVector(acp=100.0)
        assert state.acp <= 100

    def test_acp_valid_range(self):
        """ACP must be in [0, 100]."""
        state = ArchitecturalStateVector(acp=50.0)
        assert 0 <= state.acp <= 100


class TestDCIBounded:
    """Test invariants for DCI (Structural Cohesion)."""

    def test_dci_lower_bound(self):
        """DCI must be >= 0."""
        state = ArchitecturalStateVector(dci=0.0)
        assert state.dci >= 0

    def test_dci_upper_bound(self):
        """DCI must be <= 100."""
        state = ArchitecturalStateVector(dci=100.0)
        assert state.dci <= 100

    def test_dci_valid_range(self):
        """DCI must be in [0, 100]."""
        state = ArchitecturalStateVector(dci=75.0)
        assert 0 <= state.dci <= 100


class TestBoundaryLeakageBounded:
    """Test invariants for Boundary Leakage."""

    def test_leakage_lower_bound(self):
        """Boundary Leakage must be >= 0."""
        state = ArchitecturalStateVector(boundary_leakage=0.0)
        assert state.boundary_leakage >= 0

    def test_leakage_upper_bound(self):
        """Boundary Leakage must be <= 1."""
        state = ArchitecturalStateVector(boundary_leakage=1.0)
        assert state.boundary_leakage <= 1

    def test_leakage_valid_range(self):
        """Boundary Leakage must be in [0, 1]."""
        state = ArchitecturalStateVector(boundary_leakage=0.5)
        assert 0 <= state.boundary_leakage <= 1


class TestCRIBounded:
    """Test invariants for CRI (Architectural Integrity)."""

    def test_cri_lower_bound(self):
        """CRI must be >= 0."""
        state = ArchitecturalStateVector(cri=0.0)
        assert state.cri >= 0

    def test_cri_upper_bound(self):
        """CRI must be <= 100."""
        state = ArchitecturalStateVector(cri=100.0)
        assert state.cri <= 100

    def test_cri_valid_range(self):
        """CRI must be in [0, 100]."""
        state = ArchitecturalStateVector(cri=85.0)
        assert 0 <= state.cri <= 100


class TestAGPBounded:
    """Test invariants for AGP (Governance Compliance)."""

    def test_agp_lower_bound(self):
        """AGP must be >= 0."""
        state = ArchitecturalStateVector(agp=0.0)
        assert state.agp >= 0

    def test_agp_upper_bound(self):
        """AGP must be <= 100."""
        state = ArchitecturalStateVector(agp=100.0)
        assert state.agp <= 100

    def test_agp_valid_range(self):
        """AGP must be in [0, 100]."""
        state = ArchitecturalStateVector(agp=90.0)
        assert 0 <= state.agp <= 100


class TestContextRadiusBounded:
    """Test invariants for Context Radius."""

    def test_context_radius_lower_bound(self):
        """Context Radius must be >= 0."""
        state = ArchitecturalStateVector(context_radius=0)
        assert state.context_radius >= 0

    def test_context_radius_positive(self):
        """Context Radius can be positive."""
        state = ArchitecturalStateVector(context_radius=5)
        assert state.context_radius == 5


class TestDependencyDensityBounded:
    """Test invariants for Dependency Density."""

    def test_dependency_density_lower_bound(self):
        """Dependency Density must be >= 0."""
        state = ArchitecturalStateVector(dependency_density=0.0)
        assert state.dependency_density >= 0

    def test_dependency_density_upper_bound(self):
        """Dependency Density must be <= 1."""
        state = ArchitecturalStateVector(dependency_density=1.0)
        assert state.dependency_density <= 1

    def test_dependency_density_valid_range(self):
        """Dependency Density must be in [0, 1]."""
        state = ArchitecturalStateVector(dependency_density=0.3)
        assert 0 <= state.dependency_density <= 1


class TestStateVectorInvariants:
    """Test invariants for the complete State Vector."""

    def test_embedding_dimensions(self):
        """Embedding must have exactly 10 dimensions."""
        state = ArchitecturalStateVector()
        embedding = state.to_embedding()
        assert len(embedding) == 10

    def test_embedding_non_negative(self):
        """All embedding values must be non-negative."""
        state = ArchitecturalStateVector(
            entropy=EntropyDynamics(current=0.0, velocity=0.0, acceleration=0.0)
        )
        embedding = state.to_embedding()
        for v in embedding:
            assert v >= 0

    def test_embedding_dimension_property(self):
        """embedding_dimension property must return 10."""
        state = ArchitecturalStateVector()
        assert state.embedding_dimension == 10

    def test_default_state_valid(self):
        """Default state must be valid."""
        state = ArchitecturalStateVector()
        assert 0 <= state.acp <= 100
        assert 0 <= state.dci <= 100
        assert 0 <= state.boundary_leakage <= 1
        assert 0 <= state.cri <= 100
        assert 0 <= state.agp <= 100
        assert state.context_radius >= 0
        assert 0 <= state.dependency_density <= 1
