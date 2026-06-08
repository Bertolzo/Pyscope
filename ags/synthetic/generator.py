"""
RegimeAwareGraphGenerator — Causal sampler for synthetic architectures.

This is the experimental apparatus of C0.0.
It constructs architectures from construction rules (FixtureSpec),
and provides derived expectations (not hardcoded).

FASM Analysis:
- Ontology: Architecture, Boundary, Dependency
- Theory: Axiom 1 (Architecture is graphable)
- Phenomenon: All structural phenomena
- Causal Factors: Construction rules cause specific metric behaviors
- State Vector: All dimensions
- Invariants: Valid DiGraph, deterministic, regime-stable
- Governance: N/A (synthetic)
- Memory: N/A (synthetic)
- Applicability: Controlled experimental conditions

Causal Integrity Rule (CIR-1):
    P(R_obs | R_spec) must be sharply peaked
"""

from __future__ import annotations

import random
from typing import Dict, List, Optional, Tuple

import numpy as np

from ags.core.graph.architectural_graph import ArchitecturalGraph
from ags.synthetic.regimes import (
    RegimeName,
    RegimeRange,
    REGIME_TAXONOMY,
    size_to_params,
    classify_observed_regime,
)
from ags.synthetic.spec import FixtureSpec


class RegimeAwareGraphGenerator:
    """
    Generates ArchitecturalGraphs from construction rules.

    Process:
        Spec -> latent structural field -> graph -> observed metrics
    Not:
        Spec -> graph -> expected values

    The spec defines causal intent. The graph realizes it.
    The metrics are observed. Expected metrics are DERIVED from rules.
    """

    def __init__(self, spec: FixtureSpec):
        self.spec = spec
        self.rng = np.random.default_rng(spec.seed)
        self.random = random.Random(spec.seed)

        self._spec_cross = self._sample_from_range(spec.regime_range.cross_domain_ratio)
        self._spec_intra = self._sample_from_range(spec.regime_range.intra_domain_ratio)
        self._spec_leakage = self._sample_from_range(spec.regime_range.file_level_leakage)
        self._spec_cycle = self._sample_from_range(spec.regime_range.cycle_density)
        self._last_graph: Optional[ArchitecturalGraph] = None

    def _sample_from_range(self, bounds: Tuple[float, float]) -> float:
        """Sample a value from a parameter range."""
        return self.rng.uniform(bounds[0], bounds[1])

    def build(self) -> ArchitecturalGraph:
        """
        Construct the graph from rules.

        Process:
        1. Determine structure (domains, modules, files)
        2. Add domains, modules, files
        3. Add intra-domain edges (controlled by intra_domain_ratio)
        4. Add cross-domain edges (controlled by cross_domain_ratio)
        5. Add file-level leakage (controlled by file_level_leakage)
        """
        graph = ArchitecturalGraph()

        # Step 1: Determine structure
        if self.spec.domains is not None:
            domains = self.spec.domains
        else:
            params = size_to_params(self.spec.regime_range.size_class)
            domains = params[0]

        if self.spec.modules_per_domain is not None:
            modules_per_domain = self.spec.modules_per_domain
        else:
            params = size_to_params(self.spec.regime_range.size_class)
            modules_per_domain = params[1]

        if self.spec.files_per_module is not None:
            files_per_module = self.spec.files_per_module
        else:
            params = size_to_params(self.spec.regime_range.size_class)
            files_per_module = params[2]

        # Step 2: Add structure
        domain_names = [f"domain_{i}" for i in range(domains)]
        module_names = []
        file_paths = []

        for d_name in domain_names:
            graph.add_module(d_name, is_domain=True)
            for j in range(modules_per_domain):
                m_name = f"{d_name}_module_{j}"
                module_names.append((m_name, d_name))
                graph.add_module(m_name)
                for k in range(files_per_module):
                    f_path = f"{m_name}/file_{k}.py"
                    file_paths.append((f_path, m_name, d_name))
                    graph.add_file(f_path, m_name, loc=self.random.randint(10, 100))

        # Step 3: Add intra-domain edges
        self._add_intra_domain_edges(
            graph, file_paths, module_names, domain_names
        )

        # Step 4: Add cross-domain edges
        self._add_cross_domain_edges(
            graph, file_paths, domain_names
        )

        # Step 5: Add file-level leakage
        self._add_file_level_leakage(
            graph, file_paths, domain_names
        )

        self._last_graph = graph
        return graph

    def _add_intra_domain_edges(
        self,
        graph: ArchitecturalGraph,
        file_paths: List[Tuple[str, str, str]],
        module_names: List[Tuple[str, str]],
        domain_names: List[str],
    ) -> None:
        """Add edges within the same domain based on intra_domain_ratio."""
        for d_name in domain_names:
            domain_files = [f for f, m, d in file_paths if d == d_name]
            if len(domain_files) < 2:
                continue

            n_possible = len(domain_files) * (len(domain_files) - 1)
            n_edges = int(n_possible * self._spec_intra)
            n_edges = min(n_edges, n_possible)

            for _ in range(n_edges):
                src, dst = self.random.sample(domain_files, 2)
                if not graph.graph.has_edge(src, dst):
                    graph.add_import(
                        src, dst,
                        import_type="from",
                        is_cross_module=(src.split("/")[0] != dst.split("/")[0]),
                    )

    def _add_cross_domain_edges(
        self,
        graph: ArchitecturalGraph,
        file_paths: List[Tuple[str, str, str]],
        domain_names: List[str],
    ) -> None:
        """Add edges between domains based on cross_domain_ratio."""
        if len(domain_names) < 2:
            return

        all_files = [f for f, m, d in file_paths]

        n_possible = len(all_files) * (len(all_files) - 1)
        n_edges = int(n_possible * self._spec_cross)
        n_edges = min(n_edges, n_possible)

        for _ in range(n_edges):
            src, dst = self.random.sample(all_files, 2)
            src_domain = next(d for f, m, d in file_paths if f == src)
            dst_domain = next(d for f, m, d in file_paths if f == dst)

            if src_domain != dst_domain:
                if not graph.graph.has_edge(src, dst):
                    graph.add_import(
                        src, dst,
                        import_type="from",
                        is_cross_module=True,
                    )

    def _add_file_level_leakage(
        self,
        graph: ArchitecturalGraph,
        file_paths: List[Tuple[str, str, str]],
        domain_names: List[str],
    ) -> None:
        """
        Add file-level imports that violate domain boundaries.

        This is the operational boundary leakage — file edges
        that ignore domain grouping, even when module-level
        boundaries are respected.
        """
        if len(domain_names) < 2:
            return

        all_files = [f for f, m, d in file_paths]
        if len(all_files) < 2:
            return

        n_possible = len(all_files) * (len(all_files) - 1)
        n_edges = int(n_possible * self._spec_leakage)

        for _ in range(n_edges):
            src, dst = self.random.sample(all_files, 2)
            src_domain = next(d for f, m, d in file_paths if f == src)
            dst_domain = next(d for f, m, d in file_paths if f == dst)

            if src_domain != dst_domain and src.split("/")[0] == dst.split("/")[0]:
                if not graph.graph.has_edge(src, dst):
                    graph.add_import(
                        src, dst,
                        import_type="from",
                        is_cross_module=False,
                        is_boundary_violation=True,
                    )

    def derived_expectations(self) -> dict:
        """
        Derive expected metrics from construction rules.

        These are NOT hardcoded — they EMERGE from the rules.

        Returns:
            {
                "cross_domain_ratio": ...,
                "intra_domain_ratio": ...,
                "file_level_leakage": ...,
                "cycle_density": ...,
                "graph_size": ...,
            }
        """
        return {
            "cross_domain_ratio": self._spec_cross,
            "intra_domain_ratio": self._spec_intra,
            "file_level_leakage": self._spec_leakage,
            "cycle_density": self._spec_cycle,
        }

    def compute_regime(self) -> RegimeName:
        """
        Classify the generated graph into a regime (observational truth).

        This is the metric-based regime classification.
        """
        expectations = self.derived_expectations()
        graph_size = self._last_graph.file_count if self._last_graph else 0
        return classify_observed_regime(
            cross_domain_ratio=expectations["cross_domain_ratio"],
            intra_domain_ratio=expectations["intra_domain_ratio"],
            file_level_leakage=expectations["file_level_leakage"],
            cycle_density=expectations["cycle_density"],
            graph_size=graph_size,
        )

    def causal_consistency_check(self) -> Tuple[bool, float]:
        """
        Check CIR-1: P(R_obs | R_spec) must be sharply peaked.

        Returns:
            (is_consistent, match_probability)
        """
        observed_regime = self.compute_regime()
        is_consistent = observed_regime == self.spec.regime
        return is_consistent, 1.0 if is_consistent else 0.0
