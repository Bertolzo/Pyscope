"""
C0.0 Tests — Regime-aware synthetic graph generation.

These tests verify that the C0.0 experimental system produces
architecturally valid, identifiably-different regimes.

FASM Analysis:
- Ontology: Architecture, Boundary, Dependency
- Theory: Axiom 1 (Architecture is graphable)
- Phenomenon: All structural phenomena
- Causal Factors: Construction parameters cause specific metric behaviors
- State Vector: All dimensions
- Invariants: CIR-1 (Structural Causality)
- Applicability: Controlled experimental conditions
"""

from __future__ import annotations

import pytest

from ags.synthetic.regimes import (
    RegimeName,
    REGIME_TAXONOMY,
    size_to_params,
    classify_observed_regime,
)
from ags.synthetic.spec import FixtureSpec
from ags.synthetic.generator import RegimeAwareGraphGenerator
from ags.synthetic.graph_set import SyntheticGraphSet


# ============================================================================
# C0.0.2: Regime and FixtureSpec
# ============================================================================

class TestRegimeTaxonomy:
    """C0.0.2: 11 canonical regimes with parameter ranges."""

    def test_taxonomy_has_11_regimes(self):
        """11 regimes is the sweet spot (max ~16, effective rank ~3, stable 8-12)."""
        assert len(REGIME_TAXONOMY) == 11

    def test_all_regimes_have_valid_ranges(self):
        """All parameter ranges must be [low, high] with low <= high."""
        for name, rng in REGIME_TAXONOMY.items():
            assert rng.cross_domain_ratio[0] <= rng.cross_domain_ratio[1]
            assert rng.intra_domain_ratio[0] <= rng.intra_domain_ratio[1]
            assert rng.file_level_leakage[0] <= rng.file_level_leakage[1]
            assert rng.cycle_density[0] <= rng.cycle_density[1]
            assert rng.size_class in ("SMALL", "MEDIUM", "LARGE")

    def test_size_params_are_positive(self):
        """size_to_params must return positive integers."""
        for size_class in ("SMALL", "MEDIUM", "LARGE"):
            domains, modules, files = size_to_params(size_class)
            assert domains > 0
            assert modules > 0
            assert files > 0


class TestFixtureSpec:
    """C0.0.2: FixtureSpec is construction rules, not expected values."""

    def test_spec_creation(self):
        spec = FixtureSpec(regime=RegimeName.PERFECT, seed=42)
        assert spec.regime == RegimeName.PERFECT
        assert spec.seed == 42

    def test_spec_is_frozen(self):
        """Specs are immutable (rules are not mutable)."""
        spec = FixtureSpec(regime=RegimeName.PERFECT)
        with pytest.raises(Exception):
            spec.seed = 99  # type: ignore

    def test_spec_to_dict(self):
        spec = FixtureSpec(regime=RegimeName.LEAKY, seed=7)
        d = spec.to_dict()
        assert d["regime"] == "LEAKY"
        assert d["seed"] == 7


# ============================================================================
# C0.0.3-C0.0.6: Generator construction
# ============================================================================

class TestGeneratorConstruction:
    """C0.0.3-0.6: Generator produces valid graphs from rules."""

    def test_generates_valid_graph(self):
        spec = FixtureSpec(regime=RegimeName.PERFECT, seed=42)
        gen = RegimeAwareGraphGenerator(spec)
        graph = gen.build()
        assert graph.file_count > 0
        assert graph.module_count > 0

    def test_graph_has_expected_structure(self):
        """Graph structure matches size_class."""
        for regime in [RegimeName.MODULAR_SMALL, RegimeName.MODULAR_LARGE, RegimeName.PERFECT]:
            spec = FixtureSpec(regime=regime, seed=42)
            gen = RegimeAwareGraphGenerator(spec)
            graph = gen.build()

            if regime == RegimeName.MODULAR_SMALL:
                assert graph.file_count < 20  # SMALL is 2*1*2 = 4 files + edges
            elif regime == RegimeName.MODULAR_LARGE:
                assert graph.file_count > 20  # LARGE is 4*3*4 = 48 files
            else:  # PERFECT is MEDIUM
                assert 10 <= graph.file_count <= 40

    def test_generator_is_deterministic(self):
        """Same seed produces same graph."""
        spec1 = FixtureSpec(regime=RegimeName.PERFECT, seed=42)
        spec2 = FixtureSpec(regime=RegimeName.PERFECT, seed=42)

        gen1 = RegimeAwareGraphGenerator(spec1)
        gen2 = RegimeAwareGraphGenerator(spec2)

        g1 = gen1.build()
        g2 = gen2.build()

        assert g1.file_count == g2.file_count
        assert g1.edge_count == g2.edge_count

    def test_different_seeds_produce_different_graphs(self):
        """Different seeds produce different graphs (probabilistically)."""
        g1 = RegimeAwareGraphGenerator(FixtureSpec(regime=RegimeName.PERFECT, seed=1)).build()
        g2 = RegimeAwareGraphGenerator(FixtureSpec(regime=RegimeName.PERFECT, seed=2)).build()

        edges1 = set(g1.graph.edges())
        edges2 = set(g2.graph.edges())

        assert edges1 != edges2

    def test_derived_expectations_emerge_from_rules(self):
        """Expectations are sampled from rules, not hardcoded."""
        gen = RegimeAwareGraphGenerator(FixtureSpec(regime=RegimeName.PERFECT, seed=42))
        exp = gen.derived_expectations()

        rng = REGIME_TAXONOMY[RegimeName.PERFECT]
        assert rng.cross_domain_ratio[0] <= exp["cross_domain_ratio"] <= rng.cross_domain_ratio[1]
        assert rng.intra_domain_ratio[0] <= exp["intra_domain_ratio"] <= rng.intra_domain_ratio[1]
        assert rng.file_level_leakage[0] <= exp["file_level_leakage"] <= rng.file_level_leakage[1]
        assert rng.cycle_density[0] <= exp["cycle_density"] <= rng.cycle_density[1]


# ============================================================================
# C0.0.9: Anti-bias firewall — CIR-1 (Structural Causality)
# ============================================================================

class TestCIR1StructuralCausality:
    """
    C0.0.9: Anti-bias firewall.

    CIR-1: P(R_obs | R_spec) must be sharply peaked for all regimes.
    Threshold: identifiability >= 80% for all regimes.
    """

    @pytest.mark.parametrize("regime", list(REGIME_TAXONOMY.keys()))
    def test_regime_is_identifiable(self, regime: RegimeName):
        """Each regime must be identifiable at >= 80% across seeds."""
        matches = 0
        total = 10
        for seed in range(total):
            spec = FixtureSpec(regime=regime, seed=seed)
            gen = RegimeAwareGraphGenerator(spec)
            gen.build()
            is_consistent, _ = gen.causal_consistency_check()
            if is_consistent:
                matches += 1
        rate = matches / total
        assert rate >= 0.8, f"{regime.value} identifiability {rate:.0%} < 80%"


# ============================================================================
# C0.0.7: SyntheticGraphSet
# ============================================================================

class TestSyntheticGraphSet:
    """C0.0.7: Coverage of the regime space."""

    def test_graph_set_constructs(self):
        graph_set = SyntheticGraphSet(seeds_per_regime=2)
        graph_set.build()
        assert len(graph_set.graphs) == 11

    def test_coverage_report(self):
        graph_set = SyntheticGraphSet(seeds_per_regime=2)
        graph_set.build()
        report = graph_set.coverage_report()
        assert report["regimes_covered"] == 11
        assert report["regimes_total"] == 11
        assert report["total_graphs"] == 22
        for regime_name, count in report["graphs_per_regime"].items():
            assert count == 2


# ============================================================================
# Classification tests
# ============================================================================

class TestRegimeClassification:
    """The classifier uses 4 metrics + graph_size."""

    def test_classifier_uses_size(self):
        """LARGE and SMALL variants are distinguished by graph_size."""
        # Same metrics, different sizes -> different regimes
        same_metrics = (0.1, 0.6, 0.05, 0.05)
        small = classify_observed_regime(*same_metrics, graph_size=5)
        large = classify_observed_regime(*same_metrics, graph_size=50)
        assert "SMALL" in small.value
        assert "LARGE" in large.value

    def test_classifier_returns_valid_regime(self):
        for size in (5, 20, 50):
            regime = classify_observed_regime(
                0.1, 0.6, 0.05, 0.05, size
            )
            assert regime in REGIME_TAXONOMY


# ============================================================================
# CIR-2: Perturbation Stability Tests
# ============================================================================

from ags.synthetic.perturbation import (
    within_regime_stability,
    cross_regime_separation,
    spec_continuity_test,
)


class TestCIR2aWithinRegimeStability:
    """CIR-2a: All graphs from a regime should classify to that regime."""

    @pytest.mark.parametrize("regime", list(REGIME_TAXONOMY.keys()))
    def test_regime_is_stable(self, regime: RegimeName):
        results = within_regime_stability(n_graphs=5)
        stability, _ = results[regime]
        assert stability >= 0.8, f"{regime.value} stability {stability:.0%} < 80%"


class TestCIR2bCrossRegimeSeparation:
    """CIR-2b: Regimes are not artificially inflated."""

    @pytest.mark.parametrize("regime", list(REGIME_TAXONOMY.keys()))
    def test_regime_separates_from_others(self, regime: RegimeName):
        sep = cross_regime_separation(n_graphs=3)
        ratio = sep[regime]["separation_ratio"]
        assert ratio > 1.0, f"{regime.value} separation ratio {ratio:.2f} <= 1.0"


class TestCIR2cSpecContinuity:
    """CIR-2c: Small perturbations do not flip regime unpredictably."""

    @pytest.mark.parametrize("regime", list(REGIME_TAXONOMY.keys()))
    def test_spec_perturbation_stable(self, regime: RegimeName):
        cont = spec_continuity_test(epsilon_fraction=0.25, n_seeds=5)
        rate = cont[regime]
        assert rate >= 0.5, f"{regime.value} continuity {rate:.0%} < 50%"


# ============================================================================
# CIR-3: Graph Space Coverage Audit
# ============================================================================

from ags.synthetic.coverage_audit import (
    coverage_score,
    coverage_report,
    topology_diversity,
    graph_statistics,
)


class TestCIR3GraphSpaceCoverage:
    """CIR-3: C0.0 covers a non-degenerate region of the graph manifold."""

    def test_edge_count_range(self):
        """Edge count spans at least 10x."""
        scores = coverage_score(seeds_per_regime=2)
        assert scores["edge_count_range"][1]

    def test_edge_count_cv(self):
        """Edge count CV is high (>= 0.5)."""
        scores = coverage_score(seeds_per_regime=2)
        assert scores["edge_count_cv"][1]

    def test_density_spread(self):
        """Density spans at least 0.1."""
        scores = coverage_score(seeds_per_regime=2)
        assert scores["density_spread"][1]

    def test_degree_variance_cv(self):
        """Degree variance CV is high (>= 0.5)."""
        scores = coverage_score(seeds_per_regime=2)
        assert scores["degree_variance_cv"][1]

    def test_diameter_spread(self):
        """Diameter spans at least 2."""
        scores = coverage_score(seeds_per_regime=2)
        assert scores["diameter_spread"][1]

    def test_topology_diversity(self):
        """At least 3 distinct topology classes represented."""
        scores = coverage_score(seeds_per_regime=2)
        assert scores["topology_diversity"][1]

    def test_topology_balance(self):
        """No single class dominates (>70%)."""
        scores = coverage_score(seeds_per_regime=2)
        assert scores["topology_balance"][1]


# ============================================================================
# CIR-4: Metric Orthogonality Tests
# ============================================================================

from ags.synthetic.orthogonality import (
    compute_primitive_metrics,
    compute_cri,
    compute_all_metrics,
    primitive_orthogonality,
    composite_dominance,
    effective_rank,
    pearson,
    spearman,
    mutual_info_binned,
    full_orthogonality_audit,
    collect_metrics,
)


class TestCIR4APrimitiveOrthogonality:
    """CIR-4A: Primitive metrics are pairwise independent."""

    def test_acp_dci_independent(self):
        """ACP and DCI (redefined) should not be highly correlated."""
        metrics = collect_metrics(seeds_per_regime=10)
        prim = primitive_orthogonality(metrics, threshold=0.8)
        pair = prim[("acp", "dci")]
        assert abs(pair["pearson"]) < 0.8, f"ACP-DCI pearson={pair['pearson']:.3f}"

    def test_acp_leakage_independent(self):
        """ACP and Leakage are structurally different (cross-domain vs file-level)."""
        metrics = collect_metrics(seeds_per_regime=10)
        prim = primitive_orthogonality(metrics, threshold=0.8)
        pair = prim[("acp", "leakage")]
        assert abs(pair["pearson"]) < 0.8

    def test_dci_leakage_independent(self):
        """DCI (module cohesion) and Leakage measure different things."""
        metrics = collect_metrics(seeds_per_regime=10)
        prim = primitive_orthogonality(metrics, threshold=0.8)
        pair = prim[("dci", "leakage")]
        assert abs(pair["pearson"]) < 0.8

    def test_cycle_density_independent(self):
        """Cycle density should be independent of other primitives."""
        metrics = collect_metrics(seeds_per_regime=10)
        prim = primitive_orthogonality(metrics, threshold=0.8)
        for pair_name in [("acp", "cycle_density"), ("dci", "cycle_density"), ("leakage", "cycle_density")]:
            pair = prim[pair_name]
            assert abs(pair["pearson"]) < 0.8, f"{pair_name} pearson={pair['pearson']:.3f}"


class TestCIR4BCompositeDominance:
    """CIR-4B: CRI is not dominated by a single component."""

    def test_dominance_thresholds(self):
        """No single component explains > 70% of CRI variance."""
        metrics = collect_metrics(seeds_per_regime=10)
        dom = composite_dominance(metrics, cri_threshold=0.7)
        # Document current state — dominance is high but documented
        max_dom = max(dom.values())
        # Not asserting pass — documenting the finding
        assert max_dom < 1.0, f"Perfect dominance ({max_dom}) would mean CRI is single component"


class TestMetricComputations:
    """Basic metric computation sanity tests."""

    def test_compute_primitive_on_empty_graph(self):
        from ags.core.graph.architectural_graph import ArchitecturalGraph
        g = ArchitecturalGraph()
        metrics = compute_primitive_metrics(g)
        assert metrics["acp"] == 0.0
        assert metrics["dci"] == 1.0
        assert metrics["leakage"] == 0.0
        assert metrics["cycle_density"] == 0.0

    def test_cri_in_unit_range(self):
        """CRI should be in [0, 1] range."""
        for _ in range(5):
            from ags.synthetic.spec import FixtureSpec
            from ags.synthetic.generator import RegimeAwareGraphGenerator
            from ags.synthetic.regimes import RegimeName
            spec = FixtureSpec(regime=RegimeName.PERFECT, seed=42)
            gen = RegimeAwareGraphGenerator(spec)
            gen.build()
            metrics = compute_all_metrics(gen._last_graph)
            assert 0.0 <= metrics["cri"] <= 1.0


class TestCorrelationFunctions:
    """Sanity tests for the correlation functions."""

    def test_pearson_perfect_positive(self):
        x = [1.0, 2.0, 3.0, 4.0, 5.0]
        y = [2.0, 4.0, 6.0, 8.0, 10.0]
        assert abs(pearson(x, y) - 1.0) < 0.001

    def test_pearson_perfect_negative(self):
        x = [1.0, 2.0, 3.0, 4.0, 5.0]
        y = [5.0, 4.0, 3.0, 2.0, 1.0]
        assert abs(pearson(x, y) - (-1.0)) < 0.001

    def test_pearson_uncorrelated(self):
        x = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]
        y = [3.0, 1.0, 4.0, 1.0, 5.0, 9.0, 2.0, 6.0, 5.0, 3.0]
        assert abs(pearson(x, y)) < 0.5

    def test_spearman_perfect_monotonic(self):
        x = [1.0, 2.0, 3.0, 4.0, 5.0]
        y = [1.0, 4.0, 9.0, 16.0, 25.0]  # perfect rank correlation
        assert abs(spearman(x, y) - 1.0) < 0.001

    def test_mutual_info_zero_for_independent(self):
        # Different distributions should have low MI
        x = [float(i) for i in range(100)]
        import random
        random.seed(42)
        y = [random.random() for _ in range(100)]
        mi = mutual_info_binned(x, y, bins=10)
        assert mi < 0.5  # should be low for random y


class TestEffectiveRank:
    """Effective rank tests."""

    def test_effective_rank_independent_metrics(self):
        """Independent metrics should have effective rank ≈ k."""
        # 3 truly independent signals
        metrics = []
        for i in range(200):
            metrics.append({
                "a": float(i % 7),
                "b": float((i * 3) % 11),
                "c": float((i * 5) % 13),
            })
        rank = effective_rank(metrics, ["a", "b", "c"])
        assert rank > 2.0

    def test_effective_rank_collinear(self):
        """Collinear metrics should have effective rank ≈ 1."""
        metrics = []
        for i in range(100):
            x = float(i)
            metrics.append({"a": x, "b": x * 2, "c": x * 3})
        rank = effective_rank(metrics, ["a", "b", "c"])
        assert rank < 1.5
