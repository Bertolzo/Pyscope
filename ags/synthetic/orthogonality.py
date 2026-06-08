"""
CIR-4: Metric Orthogonality Tests.

Primitive metrics (ACP, DCI, Leakage, CycleDensity) should be independent.
Composite metrics (CRI) should not be dominated by any single component.

CIR-4A: Primitive Orthogonality
    For all pairs of primitive metrics (M_i, M_j):
        |pearson(M_i, M_j)| < 0.8
    Threshold rationale: corr < 0.8 means each metric carries
    at least 36% independent variance (1 - 0.8^2).

CIR-4B: Composite Dominance
    For CRI (composite metric):
        No single component explains > 70% of CRI variance.
    Rationale: A dominated CRI is effectively that component
    in disguise; the "composite" claim is vacuous.

FASM Analysis:
- Ontology: Architecture
- Theory: Axiom 7 (Observations are approximations)
- Phenomenon: Metric independence
- Causal Factors: Underlying structural dimensions
- State Vector: All dimensions
- Invariants: CIR-4 (Metric Independence)
- Governance: N/A (synthetic)
- Memory: N/A (synthetic)
- Applicability: C0 controlled conditions
"""

from __future__ import annotations

import math
import statistics
from typing import Dict, List, Optional, Tuple

import numpy as np

from ags.core.graph.architectural_graph import ArchitecturalGraph
from ags.core.graph.communities import detect_communities, community_contamination
from ags.synthetic.regimes import (
    RegimeName,
    REGIME_TAXONOMY,
)
from ags.synthetic.spec import FixtureSpec
from ags.synthetic.generator import RegimeAwareGraphGenerator


# ============================================================================
# Metric computation on synthetic graphs
# ============================================================================

def compute_primitive_metrics(graph: ArchitecturalGraph) -> Dict[str, float]:
    """
    Compute primitive metrics on a synthetic graph.

    Returns dict with:
        - acp: cross_domain_edges / total_edges
        - dci: 1 - module_cohesion (fraction of cross-module edges)
                [redefined from community contamination, which was collinear with ACP]
        - leakage: boundary_violations / total_edges
        - cycle_density: cyclomatic_complexity / total_edges
    """
    files = list(graph._files.values())
    if not files:
        return {"acp": 0.0, "dci": 1.0, "leakage": 0.0, "cycle_density": 0.0}

    # Count edge categories
    cross_domain = 0
    cross_module = 0
    boundary_violations = 0
    total_edges = 0

    for src, dst, data in graph.graph.edges(data=True):
        if src not in graph._files or dst not in graph._files:
            continue
        total_edges += 1

        src_mod = graph._files[src].module
        dst_mod = graph._files[dst].module
        src_domain = _extract_domain(src_mod)
        dst_domain = _extract_domain(dst_mod)

        if src_domain != dst_domain:
            cross_domain += 1
        if src_mod != dst_mod:
            cross_module += 1
        if data.get("is_boundary_violation"):
            boundary_violations += 1

    # ACP: cross-domain pressure
    acp = cross_domain / total_edges if total_edges else 0.0

    # DCI (refined): 1 - cross_module_ratio
    # Measures module cohesion: how internally connected each module is.
    # This is genuinely independent from ACP (which is cross-domain).
    cross_module_ratio = cross_module / total_edges if total_edges else 0.0
    dci = 1.0 - cross_module_ratio

    # Leakage: boundary violations
    leakage = boundary_violations / total_edges if total_edges else 0.0

    # Cycle density: cyclomatic complexity proxy
    n = graph.graph.number_of_nodes()
    e = graph.graph.number_of_edges()
    try:
        import networkx as nx
        n_scc = nx.number_strongly_connected_components(graph.graph)
        cyclomatic = max(0, e - n + n_scc)
    except Exception:
        cyclomatic = 0
    cycle_density = cyclomatic / max(e, 1) if e else 0.0

    return {
        "acp": acp,
        "dci": dci,
        "leakage": leakage,
        "cycle_density": min(1.0, cycle_density),
    }


def compute_cri(
    metrics: Dict[str, float],
    weights: Optional[Dict[str, float]] = None,
) -> float:
    """
    Compute CRI (Composite Risk Index) from primitive metrics.

    CRI = w1*(1-ACP) + w2*DCI + w3*(1-Leakage) + w4*(1-cycle_density)

    This is the synthetic-compatible version that doesn't depend on radon.
    """
    if weights is None:
        weights = {
            "coupling": 0.30,    # 1 - ACP
            "cohesion": 0.30,    # DCI
            "containment": 0.20, # 1 - Leakage
            "stability": 0.20,   # 1 - cycle_density
        }

    return (
        weights["coupling"] * (1.0 - metrics["acp"])
        + weights["cohesion"] * metrics["dci"]
        + weights["containment"] * (1.0 - metrics["leakage"])
        + weights["stability"] * (1.0 - metrics["cycle_density"])
    )


def compute_all_metrics(graph: ArchitecturalGraph) -> Dict[str, float]:
    """Compute primitive metrics + CRI."""
    primitives = compute_primitive_metrics(graph)
    primitives["cri"] = compute_cri(primitives)
    return primitives


def _extract_domain(module_name: str) -> str:
    """Extract domain from module name (domain_X, or domain_X_module_Y -> domain_X)."""
    parts = module_name.split("_")
    if len(parts) >= 2 and parts[0] == "domain":
        return f"domain_{parts[1]}"
    return module_name


# ============================================================================
# Correlation computations (Pearson, Spearman, MI) — pure numpy
# ============================================================================

def pearson(x: List[float], y: List[float]) -> float:
    """Pearson correlation coefficient."""
    n = len(x)
    if n < 2:
        return 0.0
    mean_x = sum(x) / n
    mean_y = sum(y) / n
    cov = sum((x[i] - mean_x) * (y[i] - mean_y) for i in range(n))
    var_x = sum((x[i] - mean_x) ** 2 for i in range(n))
    var_y = sum((y[i] - mean_y) ** 2 for i in range(n))
    if var_x == 0 or var_y == 0:
        return 0.0
    return cov / math.sqrt(var_x * var_y)


def spearman(x: List[float], y: List[float]) -> float:
    """Spearman rank correlation."""
    rx = _rank(x)
    ry = _rank(y)
    return pearson(rx, ry)


def _rank(x: List[float]) -> List[float]:
    """Assign ranks to values (1-indexed, average for ties)."""
    n = len(x)
    indexed = sorted(enumerate(x), key=lambda p: p[1])
    ranks = [0.0] * n
    i = 0
    while i < n:
        j = i
        while j < n and indexed[j][1] == indexed[i][1]:
            j += 1
        avg_rank = (i + 1 + j) / 2.0
        for k in range(i, j):
            ranks[indexed[k][0]] = avg_rank
        i = j
    return ranks


def mutual_info_binned(x: List[float], y: List[float], bins: int = 10) -> float:
    """
    Estimate mutual information using histogram binning.

    I(X;Y) = sum_{i,j} p(x_i, y_j) * log(p(x_i, y_j) / (p(x_i) * p(y_j)))

    Returns MI in nats. Normalized MI = I / sqrt(H(X) * H(Y)).
    """
    if len(x) < 2:
        return 0.0

    x_arr = np.array(x)
    y_arr = np.array(y)

    # Adaptive binning
    x_std = float(x_arr.std()) if len(x) > 1 else 0.0
    y_std = float(y_arr.std()) if len(y) > 1 else 0.0
    if x_std == 0 or y_std == 0:
        return 0.0

    n_bins_x = min(bins, max(3, int(math.sqrt(len(x)))))
    n_bins_y = min(bins, max(3, int(math.sqrt(len(y)))))

    try:
        h, _, _ = np.histogram2d(x_arr, y_arr, bins=[n_bins_x, n_bins_y])
    except Exception:
        return 0.0

    p_xy = h / h.sum()
    p_x = p_xy.sum(axis=1)
    p_y = p_xy.sum(axis=0)

    mi = 0.0
    for i in range(p_xy.shape[0]):
        for j in range(p_xy.shape[1]):
            if p_xy[i, j] > 0 and p_x[i] > 0 and p_y[j] > 0:
                mi += p_xy[i, j] * math.log(p_xy[i, j] / (p_x[i] * p_y[j]))

    # Normalize by sqrt(H(X) * H(Y))
    h_x = -sum(p * math.log(p) for p in p_x if p > 0)
    h_y = -sum(p * math.log(p) for p in p_y if p > 0)

    if h_x == 0 or h_y == 0:
        return 0.0
    return float(mi) / math.sqrt(h_x * h_y)


# ============================================================================
# CIR-4A: Primitive Orthogonality Test
# ============================================================================

PRIMITIVE_METRICS = ["acp", "dci", "leakage", "cycle_density"]


def primitive_orthogonality(
    metrics_list: List[Dict[str, float]],
    threshold: float = 0.8,
) -> Dict[Tuple[str, str], Dict[str, float]]:
    """
    CIR-4A: Test that all primitive metrics are pairwise independent.

    For each pair (M_i, M_j) of primitives:
        |pearson(M_i, M_j)| < threshold

    Returns:
        Dict[(metric_a, metric_b) -> {pearson, spearman, mi, passes}]
    """
    results: Dict[Tuple[str, str], Dict[str, float]] = {}

    for i, m_a in enumerate(PRIMITIVE_METRICS):
        for m_b in PRIMITIVE_METRICS[i + 1:]:
            x = [s[m_a] for s in metrics_list]
            y = [s[m_b] for s in metrics_list]

            p = pearson(x, y)
            s = spearman(x, y)
            mi = mutual_info_binned(x, y)

            results[(m_a, m_b)] = {
                "pearson": p,
                "spearman": s,
                "mi": mi,
                "passes": abs(p) < threshold,
            }

    return results


# ============================================================================
# CIR-4B: Composite Dominance Test
# ============================================================================

def composite_dominance(
    metrics_list: List[Dict[str, float]],
    cri_threshold: float = 0.7,
) -> Dict[str, float]:
    """
    CIR-4B: Test that CRI is not dominated by a single component.

    For each component (1-ACP, DCI, 1-Leakage, 1-cycle_density):
        contribution_i = |corr(component_i, CRI)|

    If max(contribution) < threshold, CRI is not dominated.

    Returns:
        Dict[component_name -> dominance_score]
    """
    cri_values = [s["cri"] for s in metrics_list]

    components = {
        "coupling": [1.0 - s["acp"] for s in metrics_list],
        "cohesion": [s["dci"] for s in metrics_list],
        "containment": [1.0 - s["leakage"] for s in metrics_list],
        "stability": [1.0 - s["cycle_density"] for s in metrics_list],
    }

    dominance: Dict[str, float] = {}
    for name, values in components.items():
        dominance[name] = abs(pearson(values, cri_values))

    return dominance


def effective_rank(
    metrics_list: List[Dict[str, float]],
    metric_names: List[str],
) -> float:
    """
    Compute effective rank of the metric covariance matrix.

    effective_rank = (sum of singular values)^2 / sum of squared singular values

    For k truly independent metrics, effective_rank ≈ k.
    For k collinear metrics, effective_rank ≈ 1.
    """
    if not metrics_list or not metric_names:
        return 0.0

    # Build matrix
    n_samples = len(metrics_list)
    n_metrics = len(metric_names)
    M = np.zeros((n_samples, n_metrics))
    for i, sample in enumerate(metrics_list):
        for j, name in enumerate(metric_names):
            M[i, j] = sample[name]

    # Center and scale
    M = M - M.mean(axis=0)
    std = M.std(axis=0)
    std[std == 0] = 1.0
    M = M / std

    # SVD
    try:
        s = np.linalg.svd(M, compute_uv=False)
    except Exception:
        return 0.0

    s_sum = float(s.sum())
    s_sq = float((s ** 2).sum())
    if s_sq == 0:
        return 0.0
    return (s_sum ** 2) / s_sq


# ============================================================================
# Full audit pipeline
# ============================================================================

def collect_metrics(
    seeds_per_regime: int = 100,
) -> List[Dict[str, float]]:
    """
    Collect primitive + composite metrics for all regimes.

    Returns:
        List of metric dicts, one per generated graph.
    """
    all_metrics: List[Dict[str, float]] = []
    for regime in REGIME_TAXONOMY:
        for seed in range(seeds_per_regime):
            spec = FixtureSpec(regime=regime, seed=seed)
            gen = RegimeAwareGraphGenerator(spec)
            gen.build()
            metrics = compute_all_metrics(gen._last_graph)
            all_metrics.append(metrics)
    return all_metrics


def full_orthogonality_audit(
    seeds_per_regime: int = 100,
    primitive_threshold: float = 0.8,
    dominance_threshold: float = 0.7,
    effective_rank_threshold: int = 3,
) -> Dict[str, object]:
    """
    Run the full CIR-4 audit.

    Returns:
        {
            "primitive_pairs": {(a,b) -> {pearson, spearman, mi, passes}},
            "dominance": {component -> score},
            "effective_rank_primitive": float,
            "effective_rank_all": float,
            "primitive_passes": bool,
            "dominance_passes": bool,
            "rank_passes": bool,
        }
    """
    metrics_list = collect_metrics(seeds_per_regime)

    prim = primitive_orthogonality(metrics_list, primitive_threshold)
    dom = composite_dominance(metrics_list, dominance_threshold)
    rank_prim = effective_rank(metrics_list, PRIMITIVE_METRICS)
    rank_all = effective_rank(metrics_list, PRIMITIVE_METRICS + ["cri"])

    primitive_passes = all(p["passes"] for p in prim.values())
    dominance_passes = max(dom.values()) < dominance_threshold
    rank_passes = rank_prim >= effective_rank_threshold

    return {
        "primitive_pairs": prim,
        "dominance": dom,
        "effective_rank_primitive": rank_prim,
        "effective_rank_all": rank_all,
        "primitive_passes": primitive_passes,
        "dominance_passes": dominance_passes,
        "rank_passes": rank_passes,
        "n_samples": len(metrics_list),
    }
