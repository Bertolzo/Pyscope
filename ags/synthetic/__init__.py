"""
Synthetic C0.0 experimental system — causal regime generator.

FASM Analysis:
- Ontology: Architecture, Boundary, Dependency
- Theory: Axiom 1 (Architecture is graphable)
- Phenomenon: All structural phenomena
- Causal Factors: Construction rules cause specific metric behaviors
- State Vector: All dimensions
- Invariants: CIR-1, CIR-2, CIR-3 (Causal Integrity Rules)
- Governance: N/A (synthetic)
- Memory: N/A (synthetic)
- Applicability: Controlled experimental conditions

Public API:
    RegimeName - Canonical regime names (11 attractor classes)
    RegimeRange - Parameter range definition
    REGIME_TAXONOMY - Complete taxonomy dict
    FixtureSpec - Construction rules (not expected values)
    RegimeAwareGraphGenerator - Causal sampler
    SyntheticGraphSet - Collection spanning regime space
    classify_observed_regime - Metric-based regime classification
    within_regime_stability - CIR-2a test
    cross_regime_separation - CIR-2b test
    spec_continuity_test - CIR-2c test
    coverage_audit - CIR-3 graph space coverage
"""

from ags.synthetic.regimes import (
    RegimeName,
    RegimeRange,
    REGIME_TAXONOMY,
    size_to_params,
    classify_observed_regime,
    CIR1_DOC,
)
from ags.synthetic.spec import FixtureSpec
from ags.synthetic.generator import RegimeAwareGraphGenerator
from ags.synthetic.graph_set import SyntheticGraphSet
from ags.synthetic.perturbation import (
    graph_structural_distance,
    within_regime_stability,
    cross_regime_separation,
    spec_continuity_test,
)
from ags.synthetic.coverage_audit import (
    graph_statistics,
    coverage_audit,
    topology_class,
    topology_diversity,
    coverage_report,
    coverage_score,
)
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
)

__all__ = [
    "RegimeName",
    "RegimeRange",
    "REGIME_TAXONOMY",
    "size_to_params",
    "classify_observed_regime",
    "CIR1_DOC",
    "FixtureSpec",
    "RegimeAwareGraphGenerator",
    "SyntheticGraphSet",
    "graph_structural_distance",
    "within_regime_stability",
    "cross_regime_separation",
    "spec_continuity_test",
    "graph_statistics",
    "coverage_audit",
    "topology_class",
    "topology_diversity",
    "coverage_report",
    "coverage_score",
    "compute_primitive_metrics",
    "compute_cri",
    "compute_all_metrics",
    "primitive_orthogonality",
    "composite_dominance",
    "effective_rank",
    "pearson",
    "spearman",
    "mutual_info_binned",
    "full_orthogonality_audit",
]
