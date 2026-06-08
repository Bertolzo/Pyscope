"""
Invariantes do ArchitecturalGraph.

Propriedades que NUNCA devem ser quebradas por refatorações futuras.
"""

from __future__ import annotations

from pathlib import Path

import networkx as nx
import pytest

from ags.core.graph.architectural_graph import ArchitecturalGraph
from ags.core.graph.builders import GraphBuilder
from ags.core.graph.communities import detect_communities
from ags.core.graph.metrics import dependency_density


@pytest.fixture
def sample_graph() -> ArchitecturalGraph:
    g = ArchitecturalGraph()
    g.add_file("a.py", module="ma", loc=100)
    g.add_file("b.py", module="mb", loc=200)
    g.add_file("c.py", module="ma", loc=50)
    g.add_import("a.py", "b.py")
    g.add_import("b.py", "c.py")
    g.add_import("c.py", "a.py")
    g.add_cross_module_import("ma", "mb")
    return g


@pytest.fixture
def monolith_graph() -> ArchitecturalGraph:
    fixture = Path(__file__).parent / "fixtures" / "sample_monolith"
    builder = GraphBuilder(str(fixture))
    return builder.build()


class TestGraphInvariants:
    """Invariantes fundamentais do grafo."""

    def test_no_duplicate_nodes(self, sample_graph: ArchitecturalGraph) -> None:
        nodes = list(sample_graph.graph.nodes())
        assert len(nodes) == len(set(nodes))

    def test_no_duplicate_edges(self, sample_graph: ArchitecturalGraph) -> None:
        edges = list(sample_graph.graph.edges())
        assert len(edges) == len(set(edges))

    def test_every_edge_has_existing_nodes(self, sample_graph: ArchitecturalGraph) -> None:
        nodes = set(sample_graph.graph.nodes())
        for u, v in sample_graph.graph.edges():
            assert u in nodes, f"Node {u} in edge ({u}, {v}) not in graph"
            assert v in nodes, f"Node {v} in edge ({u}, {v}) not in graph"

    def test_file_nodes_have_module(self, sample_graph: ArchitecturalGraph) -> None:
        for path, node in sample_graph.files.items():
            assert node.module != "", f"FileNode {path} has empty module"

    def test_module_nodes_have_name(self, sample_graph: ArchitecturalGraph) -> None:
        for name, node in sample_graph.modules.items():
            assert node.name != "", f"ModuleNode has empty name"
            assert node.name == name

    def test_serialization_preserves_node_count(
        self, sample_graph: ArchitecturalGraph
    ) -> None:
        json_str = sample_graph.to_json()
        restored = ArchitecturalGraph.from_json(json_str)
        assert restored.graph.number_of_nodes() == sample_graph.graph.number_of_nodes()

    def test_serialization_preserves_edge_count(
        self, sample_graph: ArchitecturalGraph
    ) -> None:
        json_str = sample_graph.to_json()
        restored = ArchitecturalGraph.from_json(json_str)
        assert restored.graph.number_of_edges() == sample_graph.graph.number_of_edges()

    def test_community_covers_all_nodes(self, sample_graph: ArchitecturalGraph) -> None:
        communities = detect_communities(sample_graph.graph)
        assert len(communities) == sample_graph.graph.number_of_nodes()

    def test_context_radius_never_negative(
        self, sample_graph: ArchitecturalGraph
    ) -> None:
        for path in sample_graph.files:
            for depth in range(5):
                radius = sample_graph.context_radius(path, depth=depth)
                assert radius >= 0, f"context_radius({path}, {depth}) = {radius} < 0"

    def test_dependency_density_bounds(
        self, sample_graph: ArchitecturalGraph
    ) -> None:
        density = dependency_density(sample_graph.graph)
        assert 0.0 <= density <= 1.0, f"dependency_density = {density} out of [0, 1]"

    def test_monolith_has_no_self_loops(self, monolith_graph: ArchitecturalGraph) -> None:
        for u, v in monolith_graph.graph.edges():
            assert u != v, f"Self-loop detected: {u} -> {v}"

    def test_monolith_edge_count_reasonable(
        self, monolith_graph: ArchitecturalGraph
    ) -> None:
        n = monolith_graph.graph.number_of_nodes()
        e = monolith_graph.graph.number_of_edges()
        assert e <= n * (n - 1), f"Edge count {e} exceeds maximum for {n} nodes"

    def test_serialization_roundtrip_preserves_file_data(
        self, sample_graph: ArchitecturalGraph
    ) -> None:
        json_str = sample_graph.to_json()
        restored = ArchitecturalGraph.from_json(json_str)

        for path in sample_graph.files:
            assert path in restored.files
            assert restored.files[path].module == sample_graph.files[path].module
            assert restored.files[path].loc == sample_graph.files[path].loc
