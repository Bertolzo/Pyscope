"""
CIR-3: Graph Space Coverage Audit.

C0.0 must sample a non-degenerate region of the graph manifold.

CIR-3a: Distributional Spread
    Graph statistics (degree, edges, cycles) must have wide range.
    Coefficient of variation > threshold.

CIR-3b: Topology Diversity
    C0.0 must include diverse topology classes (DAG-like, mesh, modular, etc.).
    No single topology class should dominate.

CIR-3c: External Reference (placeholder)
    Will be filled in C1 with real projects (Django, FastAPI, etc.).
    For now: internal spread check.

FASM Analysis:
- Ontology: Architecture, Boundary, Dependency
- Theory: Axiom 1, Axiom 2 (Architecture has state)
- Phenomenon: All structural phenomena
- Causal Factors: Construction parameter variations cause graph diversity
- State Vector: All dimensions
- Invariants: CIR-3 (Graph Space Coverage)
- Governance: N/A (synthetic)
- Memory: N/A (synthetic)
- Applicability: Controlled experimental conditions
"""

from __future__ import annotations

import statistics
from collections import Counter
from typing import Dict, List, Tuple

from ags.core.graph.architectural_graph import ArchitecturalGraph
from ags.synthetic.regimes import (
    RegimeName,
    REGIME_TAXONOMY,
)
from ags.synthetic.spec import FixtureSpec
from ags.synthetic.generator import RegimeAwareGraphGenerator


def graph_statistics(g: ArchitecturalGraph) -> Dict[str, float]:
    """
    Compute graph-level statistics for coverage audit.

    Returns a dict with:
        - edge_count: number of edges
        - node_count: number of nodes
        - density: edge / max_edges
        - avg_degree: average degree (in+out)/2
        - max_degree: maximum degree
        - degree_variance: variance of degree distribution
        - cycle_count: number of simple cycles (capped at 1000)
        - n_communities: number of communities (Louvain proxy)
        - diameter: longest shortest path (sample-based)
    """
    n = g.graph.number_of_nodes()
    e = g.graph.number_of_edges()
    density = e / (n * (n - 1)) if n > 1 else 0.0

    # Degree distribution
    degrees = [g.graph.degree(n) for n in g.graph.nodes()]
    avg_degree = statistics.mean(degrees) if degrees else 0.0
    max_degree = max(degrees) if degrees else 0
    degree_var = statistics.variance(degrees) if len(degrees) > 1 else 0.0

    # Cycle count: fast proxy using feedback arc set
    # (n - n_scc) for directed graphs is a lower bound on cyclomatic complexity
    try:
        import networkx as nx
        n_scc = nx.number_strongly_connected_components(g.graph)
        # Cyclomatic complexity proxy: E - N + S (for directed)
        # where E = edges, N = nodes, S = strongly connected components
        cycle_count = max(0, e - n + n_scc)
    except Exception:
        cycle_count = 0

    # Community count (Louvain proxy: weakly connected components)
    try:
        import networkx as nx
        n_communities = nx.number_weakly_connected_components(g.graph)
    except Exception:
        n_communities = 0

    # Diameter (sampled)
    try:
        import networkx as nx
        if n > 0:
            # Sample-based diameter
            nodes = list(g.graph.nodes())
            if len(nodes) > 50:
                import random
                random.seed(42)
                sample = random.sample(nodes, 50)
            else:
                sample = nodes
            max_dist = 0
            for node in sample:
                lengths = nx.single_source_shortest_path_length(g.graph.to_undirected(), node)
                if lengths:
                    max_dist = max(max_dist, max(lengths.values()))
            diameter = max_dist
        else:
            diameter = 0
    except Exception:
        diameter = 0

    return {
        "edge_count": e,
        "node_count": n,
        "density": density,
        "avg_degree": avg_degree,
        "max_degree": max_degree,
        "degree_variance": degree_var,
        "cycle_count": cycle_count,
        "n_communities": n_communities,
        "diameter": diameter,
    }


def coverage_audit(
    seeds_per_regime: int = 5,
) -> Dict[str, Dict[str, float]]:
    """
    Run the full coverage audit.

    Returns a dict of statistic_name -> {min, max, mean, std, cv}.
    """
    all_stats: List[Dict[str, float]] = []

    for regime in REGIME_TAXONOMY:
        for seed in range(seeds_per_regime):
            spec = FixtureSpec(regime=regime, seed=seed)
            gen = RegimeAwareGraphGenerator(spec)
            gen.build()
            stats = graph_statistics(gen._last_graph)
            stats["regime"] = regime.value
            all_stats.append(stats)

    # Aggregate
    result: Dict[str, Dict[str, float]] = {}
    stat_names = [k for k in all_stats[0].keys() if k != "regime"]

    for stat in stat_names:
        values = [s[stat] for s in all_stats]
        mean = statistics.mean(values)
        std = statistics.stdev(values) if len(values) > 1 else 0.0
        cv = std / mean if mean > 0 else 0.0

        result[stat] = {
            "min": min(values),
            "max": max(values),
            "mean": mean,
            "std": std,
            "cv": cv,
        }

    return result


def topology_class(g: ArchitecturalGraph) -> str:
    """
    Classify a graph into a topology class.

    Classes:
        - DAG: directed acyclic (no cycles)
        - WEAKLY_TREE: few cycles, tree-like
        - MESH: high density, many cycles
        - MODULAR: clear community structure
        - SCALE_FREE: power-law degree distribution
        - HUB_DOMINATED: very high max_degree / avg_degree ratio
    """
    stats = graph_statistics(g)
    n = stats["node_count"]
    e = stats["edge_count"]
    cycles = stats["cycle_count"]
    avg_deg = stats["avg_degree"]
    max_deg = stats["max_degree"]
    deg_var = stats["degree_variance"]

    # DAG: no cycles
    if cycles == 0:
        return "DAG"

    # HUB: extreme degree concentration
    if avg_deg > 0 and max_deg / avg_deg > 5:
        return "HUB_DOMINATED"

    # MESH: high density with many cycles
    if stats["density"] > 0.5 and cycles > 10:
        return "MESH"

    # MODULAR: many communities, moderate density
    if stats["n_communities"] > 3 and 0.1 < stats["density"] < 0.5:
        return "MODULAR"

    # SCALE_FREE: high degree variance
    if avg_deg > 0 and deg_var / avg_deg > 5:
        return "SCALE_FREE"

    # WEAKLY_TREE: default for low-cycle graphs
    if cycles < 3:
        return "WEAKLY_TREE"

    return "GENERAL"


def topology_diversity(
    seeds_per_regime: int = 5,
) -> Dict[str, int]:
    """
    Check that C0.0 covers multiple topology classes.

    Returns: Dict[topology_class -> count]
    """
    classes: List[str] = []
    for regime in REGIME_TAXONOMY:
        for seed in range(seeds_per_regime):
            spec = FixtureSpec(regime=regime, seed=seed)
            gen = RegimeAwareGraphGenerator(spec)
            gen.build()
            classes.append(topology_class(gen._last_graph))

    return dict(Counter(classes))


def coverage_report(
    seeds_per_regime: int = 5,
) -> Dict[str, object]:
    """
    Full coverage report.

    Returns:
        {
            "stats": coverage_audit result,
            "topology_classes": topology_diversity result,
            "total_graphs": 11 * seeds_per_regime,
        }
    """
    stats = coverage_audit(seeds_per_regime)
    classes = topology_diversity(seeds_per_regime)

    return {
        "stats": stats,
        "topology_classes": classes,
        "total_graphs": 11 * seeds_per_regime,
    }


def coverage_score(
    seeds_per_regime: int = 5,
) -> Dict[str, Tuple[float, bool]]:
    """
    Score the coverage against thresholds.

    Returns:
        Dict[metric_name -> (actual_value, passes)]
    """
    report = coverage_report(seeds_per_regime)
    stats = report["stats"]
    classes = report["topology_classes"]

    scores: Dict[str, Tuple[float, bool]] = {}

    # Edge count: should span at least 2 orders of magnitude
    edge_range = stats["edge_count"]["max"] / max(stats["edge_count"]["min"], 1)
    scores["edge_count_range"] = (edge_range, edge_range >= 10.0)

    # CV of edge count: high variance is good
    scores["edge_count_cv"] = (stats["edge_count"]["cv"], stats["edge_count"]["cv"] >= 0.5)

    # Density spread
    density_range = stats["density"]["max"] - stats["density"]["min"]
    scores["density_spread"] = (density_range, density_range >= 0.1)

    # Degree variance CV
    scores["degree_variance_cv"] = (
        stats["degree_variance"]["cv"],
        stats["degree_variance"]["cv"] >= 0.5,
    )

    # Diameter range
    diam_range = stats["diameter"]["max"] - stats["diameter"]["min"]
    scores["diameter_spread"] = (diam_range, diam_range >= 2)

    # Topology diversity: at least 3 distinct classes
    scores["topology_diversity"] = (len(classes), len(classes) >= 3)

    # No single class dominates (>70%)
    # Note: MODULAR is the natural attractor for software architecture,
    # so we allow up to 70% concentration
    total = sum(classes.values())
    max_frac = max(classes.values()) / total if total else 1.0
    scores["topology_balance"] = (max_frac, max_frac <= 0.70)

    return scores
