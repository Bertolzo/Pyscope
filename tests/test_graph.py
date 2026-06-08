"""
Testes para ArchitecturalGraph e GraphBuilder.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from ags.core.graph.architectural_graph import ArchitecturalGraph
from ags.core.graph.builders import GraphBuilder
from ags.core.graph.communities import detect_communities, community_contamination
from ags.core.graph.metrics import (
    cycle_density,
    dependency_density,
    graph_drift,
    most_connected_nodes,
)


class TestArchitecturalGraph:
    """Testes da classe ArchitecturalGraph."""

    def test_empty_graph(self) -> None:
        g = ArchitecturalGraph()
        assert g.file_count == 0
        assert g.module_count == 0
        assert g.edge_count == 0

    def test_add_file(self) -> None:
        g = ArchitecturalGraph()
        g.add_file("src/main.py", module="src", loc=100)
        assert g.file_count == 1
        assert "src/main.py" in g.files

    def test_add_module(self) -> None:
        g = ArchitecturalGraph()
        g.add_module("core")
        assert g.module_count == 1
        assert "core" in g.modules

    def test_add_import(self) -> None:
        g = ArchitecturalGraph()
        g.add_file("a.py", module="pkg")
        g.add_file("b.py", module="pkg")
        g.add_import("a.py", "b.py")
        assert g.edge_count == 1

    def test_context_radius(self) -> None:
        g = ArchitecturalGraph()
        g.add_file("a.py", module="m")
        g.add_file("b.py", module="m")
        g.add_file("c.py", module="m")
        g.add_import("a.py", "b.py")
        g.add_import("b.py", "c.py")

        radius = g.context_radius("a.py", depth=3)
        assert radius == 2

    def test_dependency_density_empty(self) -> None:
        g = ArchitecturalGraph()
        assert g.dependency_density() == 0.0

    def test_serialization_roundtrip(self) -> None:
        g = ArchitecturalGraph()
        g.add_file("a.py", module="m", loc=50)
        g.add_module("m")
        g.add_import("a.py", "a.py")

        json_str = g.to_json()
        g2 = ArchitecturalGraph.from_json(json_str)

        assert g2.file_count == g.file_count
        assert g2.module_count == g.module_count
        assert g2.edge_count == g.edge_count

    def test_get_files_in_module(self) -> None:
        g = ArchitecturalGraph()
        g.add_file("core/a.py", module="core")
        g.add_file("core/b.py", module="core")
        g.add_file("api/c.py", module="api")

        core_files = g.get_files_in_module("core")
        assert len(core_files) == 2

    def test_repr(self) -> None:
        g = ArchitecturalGraph()
        r = repr(g)
        assert "ArchitecturalGraph" in r


class TestGraphBuilder:
    """Testes do GraphBuilder."""

    def test_build_from_sample_project(self, sample_project: Path) -> None:
        builder = GraphBuilder(str(sample_project))
        graph = builder.build()

        assert graph.file_count > 0
        assert graph.module_count > 0

    def test_build_discovers_modules(self, sample_project: Path) -> None:
        builder = GraphBuilder(str(sample_project))
        graph = builder.build()

        module_names = list(graph.modules.keys())
        assert "core" in module_names
        assert "api" in module_names
        assert "services" in module_names

    def test_build_discovers_imports(self, sample_project: Path) -> None:
        builder = GraphBuilder(str(sample_project))
        graph = builder.build()

        assert graph.edge_count > 0

    def test_build_resolves_multiple_import_names(self, tmp_path: Path) -> None:
        project = tmp_path / "project"
        project.mkdir()
        (project / "__init__.py").write_text('"""project"""\n')
        (project / "a.py").write_text("x = 1\n")
        (project / "b.py").write_text("y = 2\n")
        (project / "main.py").write_text("import a, b\n")

        builder = GraphBuilder(str(project))
        graph = builder.build()

        assert str(project / "a.py") in graph.get_imports_from(str(project / "main.py"))
        assert str(project / "b.py") in graph.get_imports_from(str(project / "main.py"))

    def test_build_resolves_from_import_submodule(self, tmp_path: Path) -> None:
        project = tmp_path / "project"
        project.mkdir()
        (project / "__init__.py").write_text('"""project"""\n')
        pkg = project / "pkg"
        pkg.mkdir()
        (pkg / "__init__.py").write_text('"""pkg"""\n')
        (pkg / "sub.py").write_text("value = 42\n")
        (project / "main.py").write_text("from pkg import sub\n")

        builder = GraphBuilder(str(project))
        graph = builder.build()

        assert str(pkg / "sub.py") in graph.get_imports_from(str(project / "main.py"))

    def test_build_excludes_venv(self, sample_project: Path) -> None:
        venv = sample_project / "venv"
        venv.mkdir()
        (venv / "lib.py").write_text("x = 1\n")

        builder = GraphBuilder(str(sample_project))
        graph = builder.build()

        assert not any("venv" in Path(p).parts for p in graph.files)


class TestGraphMetrics:
    """Testes de métricas de grafo."""

    def test_dependency_density(self) -> None:
        g = ArchitecturalGraph()
        g.add_file("a.py", module="m")
        g.add_file("b.py", module="m")
        g.add_import("a.py", "b.py")

        density = dependency_density(g.graph)
        assert 0.0 <= density <= 1.0

    def test_cycle_density(self) -> None:
        import networkx as nx

        g = nx.DiGraph()
        g.add_edge("a", "b")
        g.add_edge("b", "c")
        g.add_edge("c", "a")

        density = cycle_density(g)
        assert density > 0

    def test_graph_drift_identical(self) -> None:
        g1 = ArchitecturalGraph()
        g1.add_file("a.py", module="m")
        g1.add_import("a.py", "a.py")

        g2 = ArchitecturalGraph()
        g2.add_file("a.py", module="m")
        g2.add_import("a.py", "a.py")

        drift = graph_drift(g1.graph, g2.graph)
        assert drift == 0.0

    def test_graph_drift_different(self) -> None:
        g1 = ArchitecturalGraph()
        g1.add_file("a.py", module="m")

        g2 = ArchitecturalGraph()
        g2.add_file("b.py", module="m")
        g2.add_import("b.py", "b.py")

        drift = graph_drift(g1.graph, g2.graph)
        assert drift > 0.0

    def test_most_connected_nodes(self) -> None:
        g = ArchitecturalGraph()
        g.add_file("a.py", module="m")
        g.add_file("b.py", module="m")
        g.add_import("a.py", "b.py")

        top = most_connected_nodes(g.graph, top_n=1)
        assert len(top) == 1


class TestCommunities:
    """Testes de detecção de comunidades."""

    def test_detect_communities_empty(self) -> None:
        import networkx as nx

        g = nx.DiGraph()
        communities = detect_communities(g)
        assert communities == {}

    def test_detect_communities(self) -> None:
        import networkx as nx

        g = nx.DiGraph()
        g.add_edge("a", "b")
        g.add_edge("b", "a")
        g.add_edge("c", "d")
        g.add_edge("d", "c")

        communities = detect_communities(g)
        assert len(communities) > 0
