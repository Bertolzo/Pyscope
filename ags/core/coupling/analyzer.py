"""
CouplingAnalyzer — L3 State: Measures coupling between domains.

FASM Layer: 3 (State Vector)
Phenomena: Structural Pressure, Structural Cohesion
"""

from __future__ import annotations

from collections import defaultdict
from typing import Any, Dict, List, Optional, Set, Tuple

from ags.core.graph.architectural_graph import ArchitecturalGraph
from ags.core.graph.communities import (
    community_contamination,
    detect_communities,
    inter_community_edges,
)
from ags.core.graph.metrics import dependency_density

from .snapshot import ACPResult, CouplingReport, DCIResult


class CouplingAnalyzer:
    """
    L3 — State: Measures coupling between domains.

    FASM Analysis:
    - Ontology: Dependency, Boundary
    - Theory: Axioma 2 (ACP measures structural pressure)
    - Phenomena: Structural Pressure, Structural Cohesion
    - State Dimensions: acp, dci, boundary_leakage
    - Metrics: ACP (%), DCI (%), Boundary Leakage (ratio)
    - Invariants: 0 <= acp <= 100, 0 <= dci <= 100, 0 <= leakage <= 1
    - Governance: Correct coupling classification
    - Memory: Both dimensions in embedding
    """

    def __init__(self, graph: ArchitecturalGraph, config: Optional[Dict[str, Any]] = None) -> None:
        self.graph = graph
        self.config = config or {}
        self.snapshot = CouplingReport()

    def analyze(self) -> CouplingReport:
        """Pipeline completo de análise de acoplamento."""
        communities = detect_communities(self.graph.graph)
        self.snapshot.communities_count = len(set(communities.values())) if communities else 0

        self._calculate_acp(communities)
        self._calculate_dci(communities)
        self._calculate_context_radius()
        self._calculate_dependency_density()

        return self.snapshot

    def _calculate_acp(self, communities: Dict[str, int]) -> None:
        """
        L3 — State: Calculate ACP (Structural Coupling Pressure).

        FASM Analysis:
        - Ontology: Dependency, Boundary
        - Theory: Axioma 2 (ACP measures structural pressure)
        - Phenomenon: Structural Pressure
        - State Dimension: acp
        - Metric: ACP (%)
        - Invariant: 0 <= acp <= 100
        - Governance: Correct coupling classification
        - Memory: Included in embedding (index 3)

        Important: ACP includes ALL edges (file + module).
        This measures structural coupling pressure, not operational violations.
        """
        cross_matrix: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
        total_cross = 0

        # ACP includes ALL edges (structural coupling pressure)
        for from_node, to_node, data in self.graph.graph.edges(data=True):
            from_comm = communities.get(from_node, 0)
            to_comm = communities.get(to_node, 0)

            if from_comm != to_comm:
                cross_matrix[str(from_comm)][str(to_comm)] += 1
                total_cross += 1

        community_count = self.snapshot.communities_count
        max_acceptable = community_count * self.config.get("acp_max_cross_imports_per_domain", 5)

        if total_cross <= max_acceptable:
            acp_score = 100.0 - (total_cross / max(max_acceptable, 1)) * 50
        else:
            acp_score = max(0.0, 50.0 - (total_cross - max_acceptable) * 2)

        coupled_pairs: List[Tuple[str, str, int]] = []
        for from_c, to_dict in cross_matrix.items():
            for to_c, count in to_dict.items():
                coupled_pairs.append((from_c, to_c, count))
        coupled_pairs.sort(key=lambda x: x[2], reverse=True)

        if acp_score >= 80:
            classification = "🟢 Desacoplado"
        elif acp_score >= 60:
            classification = "🟡 Acoplamento moderado"
        elif acp_score >= 40:
            classification = "🟠 Acoplamento alto"
        else:
            classification = "🔴 Acoplamento crítico"

        self.snapshot.acp = ACPResult(
            domain_count=community_count,
            total_cross_imports=total_cross,
            cross_import_matrix=dict(cross_matrix),
            acp_score=round(acp_score, 2),
            acp_classification=classification,
            most_coupled_pairs=coupled_pairs[:10],
        )

    def _calculate_dci(self, communities: Dict[str, int]) -> None:
        """Domain Contamination Index."""
        ratio, cross_edges, contaminated = community_contamination(
            self.graph.graph, communities
        )

        bidirectional: List[Tuple[str, str]] = []
        edge_set = set(cross_edges)
        for from_node, to_node in cross_edges:
            if (to_node, from_node) in edge_set:
                pair = tuple(sorted([from_node, to_node]))
                if pair not in bidirectional:
                    bidirectional.append(pair)

        dci_score = 100.0 - (ratio * 100)

        if ratio < 0.1:
            classification = "🟢 Domínios puros"
        elif ratio < 0.3:
            classification = "🟡 Contaminação leve"
        elif ratio < 0.6:
            classification = "🟠 Contaminação significativa"
        else:
            classification = "🔴 Contaminação severa"

        self.snapshot.dci = DCIResult(
            bidirectional_pairs=bidirectional,
            contaminated_communities=sorted(contaminated),
            contamination_ratio=round(ratio, 4),
            dci_score=round(dci_score, 2),
            dci_classification=classification,
        )

    def _calculate_context_radius(self) -> None:
        """Context Radius via BFS real no grafo."""
        radii: List[int] = []

        for path in self.graph.get_file_nodes():
            radius = self.graph.context_radius(path, depth=3)
            radii.append(radius)

        if radii:
            self.snapshot.context_radius_avg = round(
                sum(radii) / len(radii), 2
            )
            self.snapshot.context_radius_max = max(radii)

        avg = self.snapshot.context_radius_avg
        if avg <= 3:
            self.snapshot.context_radius_classification = "🟢 Feature localizada"
        elif avg <= 8:
            self.snapshot.context_radius_classification = "🟡 Feature toca múltiplos arquivos"
        elif avg <= 15:
            self.snapshot.context_radius_classification = "🟠 Feature recontexto amplo"
        else:
            self.snapshot.context_radius_classification = "🔴 Feature toca metade do sistema"

    def _calculate_dependency_density(self) -> None:
        self.snapshot.dependency_density = round(
            dependency_density(self.graph.graph), 4
        )
