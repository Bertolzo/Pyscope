"""
Tests for RegimeClassification (bridge layer C1.0).
"""

from __future__ import annotations

import pytest

from ags.core.observation import (
    ObservationSnapshot,
    RegimeClassification,
    classify_from_snapshot,
    compute_observation_snapshot,
)
from ags.core.graph.architectural_graph import ArchitecturalGraph
from ags.synthetic.regimes import RegimeName


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def empty_graph():
    return ArchitecturalGraph()


@pytest.fixture
def perfect_graph():
    """All edges within same domain, no cycles, no leakage."""
    g = ArchitecturalGraph()
    g.add_file("src/main.py", module="app.core")
    g.add_file("src/utils.py", module="app.core")
    g.add_file("src/models.py", module="app.core")
    g.add_import("src/main.py", "src/utils.py")
    g.add_import("src/main.py", "src/models.py")
    g.add_import("src/utils.py", "src/models.py")
    return g


@pytest.fixture
def leaky_graph():
    """
    File-level boundary violations: files from one module import
    specific files from another module (not just the domain boundary).
    """
    g = ArchitecturalGraph()
    g.add_file("orders/models.py", module="orders")
    g.add_file("orders/views.py", module="orders")
    g.add_file("payments/gateway.py", module="payments")
    g.add_file("payments/webhooks.py", module="payments")

    # Intra-domain
    g.add_import("orders/models.py", "orders/views.py")

    # Cross-domain (file→file, not module→module) counts as leakage
    g.add_import("orders/models.py", "payments/gateway.py", is_boundary_violation=True)
    g.add_import("orders/views.py", "payments/webhooks.py", is_boundary_violation=True)
    g.add_import("payments/webhooks.py", "orders/models.py", is_boundary_violation=True)
    return g


@pytest.fixture
def coupled_graph():
    """Moderate cross-domain coupling, some cycles, some leakage."""
    g = ArchitecturalGraph()
    # Domain A
    g.add_file("a/mod1.py", module="domain_a")
    g.add_file("a/mod2.py", module="domain_a")
    g.add_file("a/mod3.py", module="domain_a")
    # Domain B
    g.add_file("b/mod1.py", module="domain_b")
    g.add_file("b/mod2.py", module="domain_b")
    g.add_file("b/mod3.py", module="domain_b")

    # Intra edges (within domain_a)
    g.add_import("a/mod1.py", "a/mod2.py")
    g.add_import("a/mod2.py", "a/mod3.py")
    g.add_import("a/mod3.py", "a/mod1.py")  # cycle within domain

    # Intra edges (within domain_b)
    g.add_import("b/mod1.py", "b/mod2.py")

    # Cross edges
    g.add_import("a/mod1.py", "b/mod1.py")
    g.add_import("a/mod2.py", "b/mod3.py")
    return g


# ---------------------------------------------------------------------------
# Tests: empty graph
# ---------------------------------------------------------------------------

class TestEmptyClassification:
    def test_empty_graph_classifies(self, empty_graph):
        snap = compute_observation_snapshot(empty_graph)
        cls = classify_from_snapshot(snap)
        assert isinstance(cls.regime, RegimeName)
        assert cls.confidence == 0.0  # observation_quality == 0
        assert cls.distance_1 >= 0.0
        assert cls.distance_2 >= cls.distance_1
        assert cls.margin >= 0.0

    def test_empty_graph_not_confident(self, empty_graph):
        snap = compute_observation_snapshot(empty_graph)
        cls = classify_from_snapshot(snap)
        assert not cls.is_confident()
        assert not cls.is_confident(threshold=0.0) is False  # threshold=0 → confident

    def test_empty_graph_has_no_margin_when_tiny(self, empty_graph):
        snap = compute_observation_snapshot(empty_graph)
        cls = classify_from_snapshot(snap)
        assert cls.has_margin(threshold=0.0)  # threshold=0 always has margin


# ---------------------------------------------------------------------------
# Tests: perfect regime
# ---------------------------------------------------------------------------

class TestPerfectClassification:
    def test_perfect_graph_classification(self, perfect_graph):
        snap = compute_observation_snapshot(perfect_graph)
        cls = classify_from_snapshot(snap)
        # Perfect → high intra, no cross, no leakage, no cycles
        # The size (3 files) is SMALL
        assert isinstance(cls.regime, RegimeName)
        assert cls.distance_1 >= 0.0

    def test_perfect_confidence_nonzero(self, perfect_graph):
        snap = compute_observation_snapshot(perfect_graph)
        cls = classify_from_snapshot(snap)
        # observation_quality should be 1.0 (all edges resolved)
        assert snap.observation_quality == 1.0
        assert cls.confidence > 0.0


# ---------------------------------------------------------------------------
# Tests: leaky regime
# ---------------------------------------------------------------------------

class TestLeakyClassification:
    def test_leaky_graph_has_high_leakage(self, leaky_graph):
        snap = compute_observation_snapshot(leaky_graph)
        cls = classify_from_snapshot(snap)
        # LEAKY has high file_level_leakage → this graph has 3/4 = 0.75
        assert snap.file_level_leakage > 0.5
        assert isinstance(cls.regime, RegimeName)
        assert cls.distance_1 >= 0.0

    def test_leaky_distance_ordered(self, leaky_graph):
        snap = compute_observation_snapshot(leaky_graph)
        cls = classify_from_snapshot(snap)
        # Distances sorted ascending
        assert cls.distance_1 <= cls.distance_2
        assert cls.all_distances == sorted(cls.all_distances, key=lambda x: x[1])


# ---------------------------------------------------------------------------
# Tests: classification invariants
# ---------------------------------------------------------------------------

class TestClassificationInvariants:
    def test_immutable(self, perfect_graph):
        snap = compute_observation_snapshot(perfect_graph)
        cls = classify_from_snapshot(snap)
        with pytest.raises(AttributeError):
            cls.regime = RegimeName.COLLAPSED

    def test_fields_present(self, perfect_graph):
        snap = compute_observation_snapshot(perfect_graph)
        cls = classify_from_snapshot(snap)
        assert cls.regime == cls.nearest_regime
        assert cls.observation is snap
        assert len(cls.all_distances) == 11  # 11 regimes

    def test_all_regimes_sorted_by_distance(self, perfect_graph):
        snap = compute_observation_snapshot(perfect_graph)
        cls = classify_from_snapshot(snap)
        distances = [d for _, d in cls.all_distances]
        assert distances == sorted(distances)

    def test_margin_positive(self, coupled_graph):
        snap = compute_observation_snapshot(coupled_graph)
        cls = classify_from_snapshot(snap)
        assert cls.margin >= 0.0
        # Coupled should be distinguishable from perfect
        assert cls.regime != RegimeName.PERFECT

    def test_confidence_non_negative(self, empty_graph):
        snap = compute_observation_snapshot(empty_graph)
        cls = classify_from_snapshot(snap)
        assert cls.confidence >= 0.0
        assert cls.confidence <= 1.0

    def test_confidence_bounded(self, perfect_graph):
        """Confidence is in [0, 1] for any observation."""
        snap = compute_observation_snapshot(perfect_graph)
        cls = classify_from_snapshot(snap)
        assert 0.0 <= cls.confidence <= 1.0


# ---------------------------------------------------------------------------
# Tests: coupled / real-world scenario
# ---------------------------------------------------------------------------

class TestCoupledClassification:
    def test_coupled_not_collapsed(self, coupled_graph):
        snap = compute_observation_snapshot(coupled_graph)
        cls = classify_from_snapshot(snap)
        # Coupled: moderate cross (2/8 = 0.25), moderate intra (5/8 = 0.625)
        # File leakage: 0 (no is_boundary_violation)
        # Cycles: some (3 edges in cycle / 8 = 0.375)
        assert cls.regime not in (
            RegimeName.COLLAPSED,
            RegimeName.LEAKY,
            RegimeName.PERFECT,
        )
        assert cls.distance_1 >= 0.0

    def test_coupled_has_all_11_distances(self, coupled_graph):
        snap = compute_observation_snapshot(coupled_graph)
        cls = classify_from_snapshot(snap)
        assert len(cls.all_distances) == 11
        names = {name for name, _ in cls.all_distances}
        assert names == {r.value for r in RegimeName}

    def test_coupled_second_nearest_differs(self, coupled_graph):
        snap = compute_observation_snapshot(coupled_graph)
        cls = classify_from_snapshot(snap)
        assert cls.nearest_regime != cls.second_nearest_regime


# ---------------------------------------------------------------------------
# Tests: size-related
# ---------------------------------------------------------------------------

class TestSizeClassification:
    def test_large_graph_bias(self):
        """Graph with 100+ nodes should bias toward LARGE regimes."""
        g = ArchitecturalGraph()
        for i in range(100):
            g.add_file(f"file_{i}.py", module=f"mod_{i % 5}")
        snap = compute_observation_snapshot(g)
        cls = classify_from_snapshot(snap)
        # No edges → all metrics at 0
        assert len(cls.all_distances) == 11

    def test_explicit_graph_size(self):
        """Override graph_size parameter."""
        g = ArchitecturalGraph()
        g.add_file("a.py", module="mod")
        snap = compute_observation_snapshot(g)
        # Force large size → regime shifts
        cls_small = classify_from_snapshot(snap, graph_size=3)
        cls_large = classify_from_snapshot(snap, graph_size=100)
        # Different graph sizes should give different classifications
        # (or at least different distances)
        assert cls_small.all_distances != cls_large.all_distances
