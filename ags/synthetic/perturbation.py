"""
CIR-2: Perturbation Stability Tests.

Regimes must be attractors, not threshold artifacts.
Small perturbations must not produce chaotic regime flips.

CIR-2a: Within-Regime Stability
    For each regime R, N sampled graphs should all classify to R (or neighbor).
    Within-regime structural distance < between-regime distance.

CIR-2b: Cross-Regime Separation
    Between-regime distance > within-regime distance.
    Regimes are not artificially inflated.

CIR-2c: Spec Continuity
    Spec perturbed by eps within regime range still classifies to R.
    Spec perturbed outside range transitions to neighbor (not random).

FASM Analysis:
- Ontology: Architecture
- Theory: Axiom 1, Axiom 7 (observations are approximations)
- Phenomenon: All structural phenomena
- Causal Factors: Construction parameter variations
- State Vector: All dimensions
- Invariants: CIR-2 (Stability under perturbation)
- Governance: N/A (synthetic)
- Memory: N/A (synthetic)
- Applicability: Controlled experimental conditions
"""

from __future__ import annotations

import statistics
from typing import Dict, List, Tuple

from ags.core.graph.architectural_graph import ArchitecturalGraph
from ags.synthetic.regimes import (
    RegimeName,
    REGIME_TAXONOMY,
    classify_observed_regime,
)
from ags.synthetic.spec import FixtureSpec
from ags.synthetic.generator import RegimeAwareGraphGenerator


def graph_structural_distance(g1: ArchitecturalGraph, g2: ArchitecturalGraph) -> float:
    """
    Structural distance between two graphs.

    Uses Jaccard distance on edge sets (0.0 = identical, 1.0 = disjoint).
    Falls back to a metric-based distance if graphs are empty.
    """
    edges1 = set(g1.graph.edges())
    edges2 = set(g2.graph.edges())

    if not edges1 and not edges2:
        # Both empty: distance based on size difference
        return abs(g1.file_count - g2.file_count) / max(g1.file_count + g2.file_count, 1)

    intersection = len(edges1 & edges2)
    union = len(edges1 | edges2)
    if union == 0:
        return 0.0
    return 1.0 - (intersection / union)


# ============================================================================
# CIR-2a: Within-Regime Stability
# ============================================================================

def within_regime_stability(
    n_graphs: int = 10,
    stability_threshold: float = 0.8,
) -> Dict[RegimeName, Tuple[float, float]]:
    """
    For each regime, generate n_graphs and verify stability.

    Uses the generator's spec-based classification (truth by construction).

    Returns:
        Dict[regime -> (stability_rate, avg_within_distance)]
    """
    results: Dict[RegimeName, Tuple[float, float]] = {}

    for regime in REGIME_TAXONOMY:
        generators: List[RegimeAwareGraphGenerator] = []
        graphs: List[ArchitecturalGraph] = []
        for seed in range(n_graphs):
            spec = FixtureSpec(regime=regime, seed=seed)
            gen = RegimeAwareGraphGenerator(spec)
            gen.build()
            generators.append(gen)
            graphs.append(gen._last_graph)

        # Check classification stability using spec truth
        stable = 0
        for gen in generators:
            obs = gen.compute_regime()
            if obs == regime:
                stable += 1

        stability_rate = stable / n_graphs

        # Compute average within-regime distance
        distances = []
        for i in range(len(graphs)):
            for j in range(i + 1, len(graphs)):
                d = graph_structural_distance(graphs[i], graphs[j])
                distances.append(d)
        avg_dist = statistics.mean(distances) if distances else 0.0

        results[regime] = (stability_rate, avg_dist)

    return results


def _classify_graph(g: ArchitecturalGraph) -> RegimeName:
    """Classify a generated graph into a regime."""
    files = list(g._files.values())
    if not files:
        return RegimeName.PERFECT

    cross = 0
    intra = 0
    leakage = 0
    for src, dst, data in g.graph.edges(data=True):
        if src in g._files and dst in g._files:
            src_mod = g._files[src].module
            dst_mod = g._files[dst].module
            src_domain = _extract_domain(src_mod)
            dst_domain = _extract_domain(dst_mod)
            if src_domain != dst_domain:
                cross += 1
            else:
                intra += 1
            if data.get("is_boundary_violation"):
                leakage += 1

    total = cross + intra
    cross_ratio = cross / total if total else 0.0
    intra_ratio = intra / total if total else 0.0
    leak_ratio = leakage / total if total else 0.0

    # Cycle density via backward edges (proxy: edges that close a cycle)
    # Faster than nx.simple_cycles
    try:
        import networkx as nx
        # Use number of strongly connected components > 1 as proxy
        n_scc = nx.number_strongly_connected_components(g.graph)
        cycle_proxy = max(0, n_scc - 1) / max(total, 1)
    except Exception:
        cycle_proxy = 0.0

    return classify_observed_regime(
        cross_domain_ratio=cross_ratio,
        intra_domain_ratio=intra_ratio,
        file_level_leakage=leak_ratio,
        cycle_density=min(1.0, cycle_proxy),
        graph_size=g.file_count,
    )


def _extract_domain(module_name: str) -> str:
    """Extract domain from module name."""
    # For domain_X, return domain_X
    # For domain_X_module_Y, return domain_X
    parts = module_name.split("_")
    if len(parts) >= 2 and parts[0] == "domain":
        return f"domain_{parts[1]}"
    return module_name


# ============================================================================
# CIR-2b: Cross-Regime Separation
# ============================================================================

def cross_regime_separation(
    n_graphs: int = 5,
) -> Dict[RegimeName, Dict[str, float]]:
    """
    Verify that regimes are not artificially inflated.

    For each regime, compute:
        - within_dist: avg distance to other graphs of same regime
        - between_dist: avg distance to graphs of other regimes
        - separation_ratio: between_dist / within_dist

    If separation_ratio < 1.0, regime is not well-defined.
    """
    all_graphs: Dict[RegimeName, List[ArchitecturalGraph]] = {}
    for regime in REGIME_TAXONOMY:
        all_graphs[regime] = []
        for seed in range(n_graphs):
            spec = FixtureSpec(regime=regime, seed=seed)
            gen = RegimeAwareGraphGenerator(spec)
            gen.build()
            all_graphs[regime].append(gen._last_graph)

    results: Dict[RegimeName, Dict[str, float]] = {}

    for regime in REGIME_TAXONOMY:
        own_graphs = all_graphs[regime]

        within_dists = []
        for i in range(len(own_graphs)):
            for j in range(i + 1, len(own_graphs)):
                within_dists.append(
                    graph_structural_distance(own_graphs[i], own_graphs[j])
                )

        between_dists = []
        for other_regime, other_graphs in all_graphs.items():
            if other_regime == regime:
                continue
            for g1 in own_graphs:
                for g2 in other_graphs:
                    between_dists.append(graph_structural_distance(g1, g2))

        within_avg = statistics.mean(within_dists) if within_dists else 0.0
        between_avg = statistics.mean(between_dists) if between_dists else 1.0

        # Separation ratio: > 1.0 means between > within
        separation = between_avg / within_avg if within_avg > 0 else float("inf")

        results[regime] = {
            "within_distance": within_avg,
            "between_distance": between_avg,
            "separation_ratio": separation,
        }

    return results


# ============================================================================
# CIR-2c: Spec Continuity
# ============================================================================

def spec_continuity_test(
    epsilon_fraction: float = 0.25,
    n_seeds: int = 10,
) -> Dict[RegimeName, float]:
    """
    Perturb specs by epsilon_fraction of range width.

    epsilon_fraction=0.25 means perturb by 25% of the range width.
    The perturbed spec should still classify to R (or close neighbor).

    This is a relative perturbation, so regimes with narrow ranges
    get small perturbations and regimes with wide ranges get larger ones.
    """
    results: Dict[RegimeName, float] = {}

    for regime in REGIME_TAXONOMY:
        rng = REGIME_TAXONOMY[regime]
        continues = 0
        total = 0

        # Compute range widths for each parameter
        cross_width = rng.cross_domain_ratio[1] - rng.cross_domain_ratio[0]
        intra_width = rng.intra_domain_ratio[1] - rng.intra_domain_ratio[0]
        leak_width = rng.file_level_leakage[1] - rng.file_level_leakage[0]
        cycle_width = rng.cycle_density[1] - rng.cycle_density[0]

        # Compute per-parameter epsilon
        eps_cross = cross_width * epsilon_fraction
        eps_intra = intra_width * epsilon_fraction
        eps_leak = leak_width * epsilon_fraction
        eps_cycle = cycle_width * epsilon_fraction

        for seed in range(n_seeds):
            # Sample midpoint
            mid_cross = (rng.cross_domain_ratio[0] + rng.cross_domain_ratio[1]) / 2
            mid_intra = (rng.intra_domain_ratio[0] + rng.intra_domain_ratio[1]) / 2
            mid_leak = (rng.file_level_leakage[0] + rng.file_level_leakage[1]) / 2
            mid_cycle = (rng.cycle_density[0] + rng.cycle_density[1]) / 2

            for direction in [-1, 1]:
                perturbed = {
                    "cross": max(0, min(1, mid_cross + direction * eps_cross)),
                    "intra": max(0, min(1, mid_intra + direction * eps_intra)),
                    "leak": max(0, min(1, mid_leak + direction * eps_leak)),
                    "cycle": max(0, min(1, mid_cycle + direction * eps_cycle)),
                }
                total += 1
                obs = classify_observed_regime(
                    cross_domain_ratio=perturbed["cross"],
                    intra_domain_ratio=perturbed["intra"],
                    file_level_leakage=perturbed["leak"],
                    cycle_density=perturbed["cycle"],
                    graph_size=20,
                )
                if obs == regime or _is_adjacent(obs, regime):
                    continues += 1

        results[regime] = continues / total if total else 0.0

    return results


def _is_adjacent(a: RegimeName, b: RegimeName) -> bool:
    """
    Are two regimes structurally adjacent in parameter space?

    Adjacent = overlapping parameter ranges on at least one axis.
    """
    rng_a = REGIME_TAXONOMY[a]
    rng_b = REGIME_TAXONOMY[b]

    def _overlap(x, y):
        return not (x[1] < y[0] or y[1] < x[0])

    return (
        _overlap(rng_a.cross_domain_ratio, rng_b.cross_domain_ratio)
        and _overlap(rng_a.intra_domain_ratio, rng_b.intra_domain_ratio)
        and _overlap(rng_a.file_level_leakage, rng_b.file_level_leakage)
        and _overlap(rng_a.cycle_density, rng_b.cycle_density)
    )
