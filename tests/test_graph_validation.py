"""
Testes exaustivos de validação do ArchitecturalGraph.

Categorias:
- Ciclos
- Context Radius
- Comunidades
- Drift
- Fan-in/Fan-out
- Builder
- Serialização
"""

from __future__ import annotations

from pathlib import Path

import networkx as nx
import pytest

from ags.core.graph.architectural_graph import ArchitecturalGraph
from ags.core.graph.builders import GraphBuilder
from ags.core.graph.communities import (
    community_contamination,
    detect_communities,
)
from ags.core.graph.metrics import (
    cycle_density,
    dependency_density,
    fan_in,
    fan_out,
    graph_drift,
    highest_fan_in,
    highest_fan_out,
    most_connected_nodes,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def graph() -> ArchitecturalGraph:
    return ArchitecturalGraph()


@pytest.fixture
def linear_chain() -> ArchitecturalGraph:
    """A → B → C → D"""
    g = ArchitecturalGraph()
    g.add_file("a.py", module="m")
    g.add_file("b.py", module="m")
    g.add_file("c.py", module="m")
    g.add_file("d.py", module="m")
    g.add_import("a.py", "b.py")
    g.add_import("b.py", "c.py")
    g.add_import("c.py", "d.py")
    return g


@pytest.fixture
def diamond() -> ArchitecturalGraph:
    """A → B, A → C, B → D, C → D"""
    g = ArchitecturalGraph()
    g.add_file("a.py", module="m")
    g.add_file("b.py", module="m")
    g.add_file("c.py", module="m")
    g.add_file("d.py", module="m")
    g.add_import("a.py", "b.py")
    g.add_import("a.py", "c.py")
    g.add_import("b.py", "d.py")
    g.add_import("c.py", "d.py")
    return g


@pytest.fixture
def cycle_graph() -> ArchitecturalGraph:
    """A → B → C → A"""
    g = ArchitecturalGraph()
    g.add_file("a.py", module="ma")
    g.add_file("b.py", module="mb")
    g.add_file("c.py", module="mc")
    g.add_import("a.py", "b.py")
    g.add_import("b.py", "c.py")
    g.add_import("c.py", "a.py")
    g.add_cross_module_import("ma", "mb")
    g.add_cross_module_import("mb", "mc")
    g.add_cross_module_import("mc", "ma")
    return g


@pytest.fixture
def monolith_graph() -> ArchitecturalGraph:
    """Grafo construído a partir do fixture sample_monolith."""
    fixture = Path(__file__).parent / "fixtures" / "sample_monolith"
    builder = GraphBuilder(str(fixture))
    return builder.build()


# ===========================================================================
# TestCycles
# ===========================================================================

class TestCycles:
    def test_simple_cycle(self, cycle_graph: ArchitecturalGraph) -> None:
        cycles = cycle_graph.detect_cycles()
        assert len(cycles) >= 1
        cycle = cycles[0]
        assert set(cycle) == {"ma", "mb", "mc"}

    def test_multiple_cycles(self) -> None:
        g = ArchitecturalGraph()
        g.add_file("a.py", module="ma")
        g.add_file("b.py", module="mb")
        g.add_file("c.py", module="mc")
        g.add_file("d.py", module="md")
        g.add_file("e.py", module="me")
        g.add_import("a.py", "b.py")
        g.add_import("b.py", "c.py")
        g.add_import("c.py", "a.py")
        g.add_import("a.py", "d.py")
        g.add_import("d.py", "e.py")
        g.add_import("e.py", "a.py")
        g.add_cross_module_import("ma", "mb")
        g.add_cross_module_import("mb", "mc")
        g.add_cross_module_import("mc", "ma")
        g.add_cross_module_import("ma", "md")
        g.add_cross_module_import("md", "me")
        g.add_cross_module_import("me", "ma")

        cycles = g.detect_cycles()
        assert len(cycles) >= 2

    def test_no_cycles_dag(self) -> None:
        g = ArchitecturalGraph()
        g.add_file("a.py", module="ma")
        g.add_file("b.py", module="mb")
        g.add_file("c.py", module="mc")
        g.add_import("a.py", "b.py")
        g.add_import("b.py", "c.py")
        g.add_cross_module_import("ma", "mb")
        g.add_cross_module_import("mb", "mc")

        cycles = g.detect_cycles()
        assert len(cycles) == 0

    def test_self_loop(self) -> None:
        g = ArchitecturalGraph()
        g.add_file("a.py", module="ma")
        g.add_import("a.py", "a.py")
        g.add_cross_module_import("ma", "ma")

        cycles = g.detect_cycles()
        assert len(cycles) >= 1

    def test_cycle_intra_module(self) -> None:
        g = ArchitecturalGraph()
        g.add_file("pkg/a.py", module="pkg")
        g.add_file("pkg/b.py", module="pkg")
        g.add_import("pkg/a.py", "pkg/b.py")
        g.add_import("pkg/b.py", "pkg/a.py")

        all_cycles = g.detect_all_cycles()
        assert len(all_cycles) >= 1

    def test_cycle_detection_against_manual(self) -> None:
        g = ArchitecturalGraph()
        for name in ["auth", "users", "billing", "notifications"]:
            g.add_file(f"{name}.py", module=name)

        g.add_import("auth.py", "users.py")
        g.add_import("users.py", "billing.py")
        g.add_import("billing.py", "auth.py")
        g.add_import("users.py", "notifications.py")

        for m in ["auth", "users", "billing"]:
            g.add_cross_module_import(m, {"auth": "users", "users": "billing", "billing": "auth"}[m])

        cycles = g.detect_cycles()
        assert len(cycles) >= 1
        module_names = {c for cycle in cycles for c in cycle}
        assert "notifications" not in module_names


# ===========================================================================
# TestContextRadius
# ===========================================================================

class TestContextRadius:
    def test_linear_chain(self, linear_chain: ArchitecturalGraph) -> None:
        assert linear_chain.context_radius("a.py", depth=3) == 3
        assert linear_chain.context_radius("d.py", depth=3) == 3

    def test_diamond(self, diamond: ArchitecturalGraph) -> None:
        radius = diamond.context_radius("a.py", depth=2)
        assert radius == 3

    def test_disconnected_nodes(self) -> None:
        g = ArchitecturalGraph()
        g.add_file("a.py", module="m")
        g.add_file("b.py", module="m")
        g.add_file("c.py", module="m")

        assert g.context_radius("a.py", depth=3) == 0

    def test_depth_zero_returns_zero(self, linear_chain: ArchitecturalGraph) -> None:
        assert linear_chain.context_radius("a.py", depth=0) == 0

    def test_depth_one_immediate(self, linear_chain: ArchitecturalGraph) -> None:
        assert linear_chain.context_radius("a.py", depth=1) == 1
        assert linear_chain.context_radius("c.py", depth=1) == 2

    def test_bidirectional_edge(self) -> None:
        g = ArchitecturalGraph()
        g.add_file("a.py", module="m")
        g.add_file("b.py", module="m")
        g.add_import("a.py", "b.py")
        g.add_import("b.py", "a.py")

        assert g.context_radius("a.py", depth=1) == 1
        assert g.context_radius("b.py", depth=1) == 1

    def test_depth_negative_returns_zero(self, linear_chain: ArchitecturalGraph) -> None:
        assert linear_chain.context_radius("a.py", depth=-1) == 0

    def test_nonexistent_node(self, linear_chain: ArchitecturalGraph) -> None:
        assert linear_chain.context_radius("z.py", depth=3) == 0


# ===========================================================================
# TestCommunities
# ===========================================================================

class TestCommunities:
    def test_three_isolated_clusters(self) -> None:
        g = nx.DiGraph()
        g.add_edge("a", "b")
        g.add_edge("b", "a")
        g.add_edge("c", "d")
        g.add_edge("d", "c")
        g.add_edge("e", "f")
        g.add_edge("f", "e")

        communities = detect_communities(g)
        assert len(set(communities.values())) >= 2

    def test_single_community(self) -> None:
        g = nx.DiGraph()
        g.add_edge("a", "b")
        g.add_edge("b", "c")
        g.add_edge("c", "a")

        communities = detect_communities(g)
        assert len(set(communities.values())) == 1

    def test_fully_connected(self) -> None:
        g = nx.DiGraph()
        nodes = ["a", "b", "c", "d"]
        g.add_nodes_from(nodes)
        for i, n1 in enumerate(nodes):
            for j, n2 in enumerate(nodes):
                if i != j:
                    g.add_edge(n1, n2)

        communities = detect_communities(g)
        assert len(set(communities.values())) == 1

    def test_graph_with_isolated_nodes(self) -> None:
        g = nx.DiGraph()
        g.add_edge("a", "b")
        g.add_node("isolated1")
        g.add_node("isolated2")

        communities = detect_communities(g)
        assert len(set(communities.values())) == 3

    def test_contamination_ratio_accuracy(self) -> None:
        g = nx.DiGraph()
        g.add_edge("a1", "a2")
        g.add_edge("a2", "a1")
        g.add_edge("b1", "b2")
        g.add_edge("b2", "b1")
        g.add_edge("a1", "b1")

        communities = {"a1": 0, "a2": 0, "b1": 1, "b2": 1}
        ratio, cross_edges, contaminated = community_contamination(g, communities)

        assert ratio == pytest.approx(1 / 5, abs=0.01)
        assert len(cross_edges) == 1
        assert contaminated == {0, 1}

    def test_contamination_zero_when_isolated(self) -> None:
        g = nx.DiGraph()
        g.add_edge("a1", "a2")
        g.add_edge("b1", "b2")

        communities = {"a1": 0, "a2": 0, "b1": 1, "b2": 1}
        ratio, cross_edges, contaminated = community_contamination(g, communities)

        assert ratio == 0.0
        assert len(cross_edges) == 0


# ===========================================================================
# TestDrift
# ===========================================================================

class TestDrift:
    def test_identical_graphs(self) -> None:
        g1 = ArchitecturalGraph()
        g1.add_file("a.py", module="m")
        g1.add_import("a.py", "a.py")

        g2 = ArchitecturalGraph()
        g2.add_file("a.py", module="m")
        g2.add_import("a.py", "a.py")

        assert graph_drift(g1.graph, g2.graph) == 0.0

    def test_completely_different(self) -> None:
        g1 = ArchitecturalGraph()
        g1.add_file("a.py", module="m")
        g1.add_import("a.py", "a.py")

        g2 = ArchitecturalGraph()
        g2.add_file("x.py", module="n")
        g2.add_import("x.py", "x.py")

        drift = graph_drift(g1.graph, g2.graph)
        assert drift > 0.5

    def test_one_edge_added(self) -> None:
        g1 = ArchitecturalGraph()
        g1.add_file("a.py", module="m")
        g1.add_import("a.py", "a.py")

        g2 = ArchitecturalGraph()
        g2.add_file("a.py", module="m")
        g2.add_file("b.py", module="m")
        g2.add_import("a.py", "a.py")
        g2.add_import("a.py", "b.py")

        drift = graph_drift(g1.graph, g2.graph)
        assert 0.0 < drift < 0.8

    def test_all_edges_changed(self) -> None:
        g1 = ArchitecturalGraph()
        g1.add_file("a.py", module="m")
        g1.add_file("b.py", module="m")
        g1.add_import("a.py", "b.py")

        g2 = ArchitecturalGraph()
        g2.add_file("a.py", module="m")
        g2.add_file("b.py", module="m")
        g2.add_import("b.py", "a.py")

        drift = graph_drift(g1.graph, g2.graph)
        assert drift > 0.0

    def test_empty_graphs(self) -> None:
        g1 = ArchitecturalGraph()
        g2 = ArchitecturalGraph()
        assert graph_drift(g1.graph, g2.graph) == 0.0

    def test_directed_drift_asymmetry(self) -> None:
        g_forward = ArchitecturalGraph()
        g_forward.add_file("a.py", module="m")
        g_forward.add_file("b.py", module="m")
        g_forward.add_import("a.py", "b.py")

        g_reverse = ArchitecturalGraph()
        g_reverse.add_file("a.py", module="m")
        g_reverse.add_file("b.py", module="m")
        g_reverse.add_import("b.py", "a.py")

        drift = graph_drift(g_forward.graph, g_reverse.graph)
        assert drift > 0.0


# ===========================================================================
# TestFanInOut
# ===========================================================================

class TestFanInOut:
    def test_hub_node(self) -> None:
        g = ArchitecturalGraph()
        g.add_file("hub.py", module="m")
        for i in range(5):
            g.add_file(f"leaf{i}.py", module="m")
            g.add_import(f"leaf{i}.py", "hub.py")

        assert fan_in(g.graph, "hub.py") == 5
        assert fan_out(g.graph, "hub.py") == 0

    def test_leaf_node(self) -> None:
        g = ArchitecturalGraph()
        g.add_file("leaf.py", module="m")
        for i in range(3):
            g.add_file(f"dep{i}.py", module="m")
            g.add_import("leaf.py", f"dep{i}.py")

        assert fan_out(g.graph, "leaf.py") == 3
        assert fan_in(g.graph, "leaf.py") == 0

    def test_balanced_graph(self) -> None:
        g = ArchitecturalGraph()
        g.add_file("a.py", module="m")
        g.add_file("b.py", module="m")
        g.add_import("a.py", "b.py")
        g.add_import("b.py", "a.py")

        assert fan_in(g.graph, "a.py") == 1
        assert fan_out(g.graph, "a.py") == 1

    def test_isolated_node(self) -> None:
        g = ArchitecturalGraph()
        g.add_file("isolated.py", module="m")

        assert fan_in(g.graph, "isolated.py") == 0
        assert fan_out(g.graph, "isolated.py") == 0

    def test_highest_fan_in(self) -> None:
        g = ArchitecturalGraph()
        g.add_file("target.py", module="m")
        g.add_file("other.py", module="m")
        for i in range(3):
            g.add_file(f"src{i}.py", module="m")
            g.add_import(f"src{i}.py", "target.py")
        g.add_import("src0.py", "other.py")

        top = highest_fan_in(g.graph, top_n=1)
        assert top[0][0] == "target.py"
        assert top[0][1] == 3

    def test_highest_fan_out(self) -> None:
        g = ArchitecturalGraph()
        g.add_file("source.py", module="m")
        for i in range(4):
            g.add_file(f"dep{i}.py", module="m")
            g.add_import("source.py", f"dep{i}.py")

        top = highest_fan_out(g.graph, top_n=1)
        assert top[0][0] == "source.py"
        assert top[0][1] == 4


# ===========================================================================
# TestBuilder
# ===========================================================================

class TestBuilder:
    def test_deep_relative_import(self, tmp_path: Path) -> None:
        pkg = tmp_path / "pkg"
        sub = pkg / "sub"
        sub.mkdir(parents=True)
        (pkg / "__init__.py").write_text("")
        (sub / "__init__.py").write_text("")
        (pkg / "target.py").write_text("X = 1\n")
        (sub / "caller.py").write_text("from ..target import X\n")

        builder = GraphBuilder(str(tmp_path))
        graph = builder.build()

        edges = list(graph.graph.edges())
        assert any("caller.py" in str(e[0]) and "target.py" in str(e[1]) for e in edges)

    def test_namespace_package(self, tmp_path: Path) -> None:
        ns = tmp_path / "ns_pkg"
        ns.mkdir()
        (ns / "module.py").write_text("Y = 2\n")

        builder = GraphBuilder(str(tmp_path))
        graph = builder.build()

        assert any("module.py" in f for f in graph.files)

    def test_star_imports(self, tmp_path: Path) -> None:
        pkg = tmp_path / "pkg"
        pkg.mkdir()
        (pkg / "__init__.py").write_text("")
        (pkg / "base.py").write_text("A = 1\nB = 2\n")
        (tmp_path / "__init__.py").write_text("")
        (tmp_path / "consumer.py").write_text("from pkg.base import *\n")

        builder = GraphBuilder(str(tmp_path))
        graph = builder.build()

        edges = list(graph.graph.edges())
        assert any("consumer.py" in str(e[0]) and "base.py" in str(e[1]) for e in edges)

    def test_circular_imports(self, tmp_path: Path) -> None:
        a = tmp_path / "mod_a"
        a.mkdir()
        (a / "__init__.py").write_text("from mod_b import func_b\n")
        b = tmp_path / "mod_b"
        b.mkdir()
        (b / "__init__.py").write_text("from mod_a import func_a\n")

        builder = GraphBuilder(str(tmp_path))
        graph = builder.build()

        cycles = graph.detect_all_cycles()
        assert len(cycles) >= 1

    def test_exclude_directories(self, tmp_path: Path) -> None:
        venv = tmp_path / "venv"
        venv.mkdir()
        (venv / "lib.py").write_text("x = 1\n")
        pycache = tmp_path / "__pycache__"
        pycache.mkdir()
        (pycache / "cached.py").write_text("y = 2\n")
        (tmp_path / "main.py").write_text("z = 3\n")

        builder = GraphBuilder(str(tmp_path))
        graph = builder.build()

        assert graph.file_count == 1
        assert any("main.py" in f for f in graph.files)

    def test_complex_structure(self, monolith_graph: ArchitecturalGraph) -> None:
        assert monolith_graph.file_count >= 10
        assert monolith_graph.module_count >= 5
        assert monolith_graph.edge_count >= 5


# ===========================================================================
# TestSerialization
# ===========================================================================

class TestSerialization:
    def test_roundtrip_json(self, cycle_graph: ArchitecturalGraph) -> None:
        json_str = cycle_graph.to_json()
        restored = ArchitecturalGraph.from_json(json_str)

        assert restored.file_count == cycle_graph.file_count
        assert restored.module_count == cycle_graph.module_count
        assert restored.edge_count == cycle_graph.edge_count

    def test_preserves_edge_attributes(self) -> None:
        g = ArchitecturalGraph()
        g.add_file("a.py", module="m")
        g.add_file("b.py", module="m")
        g.add_import("a.py", "b.py", import_type="from", level=1, is_cross_module=True)

        json_str = g.to_json()
        restored = ArchitecturalGraph.from_json(json_str)

        edge_data = restored.graph.get_edge_data("a.py", "b.py")
        assert edge_data is not None
        assert edge_data["import_type"] == "from"
        assert edge_data["level"] == 1
        assert edge_data["is_cross_module"] is True

    def test_preserves_node_attributes(self) -> None:
        g = ArchitecturalGraph()
        g.add_file("a.py", module="test_module", loc=42)

        json_str = g.to_json()
        restored = ArchitecturalGraph.from_json(json_str)

        node_data = restored.graph.nodes["a.py"]
        assert node_data["module"] == "test_module"
        assert node_data["loc"] == 42

    def test_large_graph(self) -> None:
        g = ArchitecturalGraph()
        for i in range(500):
            g.add_file(f"file_{i}.py", module=f"mod_{i % 10}", loc=i * 10)
        for i in range(499):
            g.add_import(f"file_{i}.py", f"file_{i + 1}.py")

        json_str = g.to_json()
        restored = ArchitecturalGraph.from_json(json_str)

        assert restored.file_count == 500
        assert restored.edge_count == 499
