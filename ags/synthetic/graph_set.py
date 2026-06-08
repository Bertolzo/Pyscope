"""
SyntheticGraphSet — Collection of generated graphs spanning the regime space.
"""

from __future__ import annotations

from typing import Dict, List

from ags.core.graph.architectural_graph import ArchitecturalGraph
from ags.synthetic.generator import RegimeAwareGraphGenerator
from ags.synthetic.regimes import (
    RegimeName,
    REGIME_TAXONOMY,
    size_to_params,
)
from ags.synthetic.spec import FixtureSpec


class SyntheticGraphSet:
    """
    Collection of generated graphs spanning the regime space.

    For each regime, generates N graphs with different seeds.
    """

    def __init__(self, seeds_per_regime: int = 100):
        self.seeds_per_regime = seeds_per_regime
        self.graphs: Dict[RegimeName, List[ArchitecturalGraph]] = {}
        self.generators: Dict[RegimeName, List[RegimeAwareGraphGenerator]] = {}

    def build(self) -> None:
        """Generate all graphs."""
        for regime in REGIME_TAXONOMY:
            self.graphs[regime] = []
            self.generators[regime] = []

            for seed in range(self.seeds_per_regime):
                spec = FixtureSpec(regime=regime, seed=seed)
                generator = RegimeAwareGraphGenerator(spec)
                graph = generator.build()
                self.graphs[regime].append(graph)
                self.generators[regime].append(generator)

    def coverage_report(self) -> dict:
        """
        Report on regime coverage.

        Returns:
            {
                "regimes_covered": 11,
                "regimes_total": 11,
                "graphs_per_regime": {...},
                "total_graphs": 1100,
            }
        """
        return {
            "regimes_covered": len(self.graphs),
            "regimes_total": len(REGIME_TAXONOMY),
            "graphs_per_regime": {
                r.value: len(gs) for r, gs in self.graphs.items()
            },
            "total_graphs": sum(len(gs) for gs in self.graphs.values()),
        }
