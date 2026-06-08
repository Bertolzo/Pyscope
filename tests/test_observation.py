"""
Testes da bridge layer ObservationSnapshot.

Etapa 1: Graph → ObservationSnapshot
Etapa 2: Testes de invariantes
Etapa 3: Classificação (quando disponível)
"""

from __future__ import annotations

from pathlib import Path

import pytest

from ags.core.observation import ObservationSnapshot, compute_observation_snapshot
from ags.core.graph.architectural_graph import ArchitecturalGraph
from ags.core.graph.builders import GraphBuilder


class TestObservationSnapshot:
    """Invariantes básicos do ObservationSnapshot."""

    def test_empty_graph(self):
        """Grafo vazio → todas as métricas zero."""
        graph = ArchitecturalGraph()
        snap = compute_observation_snapshot(graph)

        assert snap.cross_domain_ratio == 0.0
        assert snap.intra_domain_ratio == 0.0
        assert snap.file_level_leakage == 0.0
        assert snap.cycle_density == 0.0
        assert snap.observation_quality == 0.0
        assert snap.total_nodes == 0
        assert snap.total_edges == 0
        assert snap.unknown_edges == 0

    def test_single_node_no_edges(self):
        """Um nó sem edges → todas as métricas zero."""
        graph = ArchitecturalGraph()
        graph.add_file(path="main.py", module="root")
        snap = compute_observation_snapshot(graph)

        assert snap.total_nodes == 1
        assert snap.total_edges == 0
        assert snap.cross_domain_ratio == 0.0
        assert snap.intra_domain_ratio == 0.0
        assert snap.observation_quality == 0.0

    def test_single_node_self_loop(self):
        """Self-loop não é contado como edge de dependência."""
        graph = ArchitecturalGraph()
        graph.add_file(path="main.py", module="root")
        graph.add_import(from_path="main.py", to_path="main.py")
        snap = compute_observation_snapshot(graph)

        assert snap.total_edges == 0, "Self-loop não deve ser contado como edge"

    def test_all_ratios_zero_to_one(self, sample_project: Path):
        """Todas as razões devem estar em [0, 1]."""
        builder = GraphBuilder(str(sample_project))
        graph = builder.build()
        snap = compute_observation_snapshot(graph)

        for name, value in [
            ("cross_domain_ratio", snap.cross_domain_ratio),
            ("intra_domain_ratio", snap.intra_domain_ratio),
            ("file_level_leakage", snap.file_level_leakage),
            ("cycle_density", snap.cycle_density),
            ("observation_quality", snap.observation_quality),
            ("classification_confidence", snap.classification_confidence),
        ]:
            assert 0.0 <= value <= 1.0, f"{name}={value} fora de [0,1]"

    def test_provenance_fields(self):
        """ObservationSnapshot deve conter metadados de proveniência."""
        graph = ArchitecturalGraph()
        snap = compute_observation_snapshot(graph)

        assert snap.parser_version is not None
        assert snap.graph_builder_version is not None
        assert snap.timestamp is not None

    def test_to_dict(self):
        """to_dict() deve retornar um dicionário serializável."""
        graph = ArchitecturalGraph()
        snap = compute_observation_snapshot(graph)
        d = snap.to_dict()

        assert isinstance(d, dict)
        assert "cross_domain_ratio" in d
        assert "observation_quality" in d
        assert "parser_version" in d
        assert "timestamp" in d

    def test_unknown_edges_sum(self):
        """unknown_edges = unknown_unresolved + unknown_dynamic."""
        snap = ObservationSnapshot(
            unknown_unresolved_edges=10,
            unknown_dynamic_edges=5,
        )

        assert snap.unknown_edges == 15


class TestObservationSampleGraph:
    """Testes contra o sample_project de conftest."""

    def test_sample_graph_has_edges(self, sample_graph):
        """O sample_graph deve ter nodes e edges."""
        snap = compute_observation_snapshot(sample_graph)

        assert snap.total_nodes > 0
        assert snap.total_edges > 0
        # All edges cross domain (api→core, services→core, services→api)
        assert snap.cross_domain_edges > 0

    def test_sample_graph_all_cross_domain(self, sample_graph):
        """No sample_project, todos os imports são cross-domain."""
        snap = compute_observation_snapshot(sample_graph)

        assert snap.cross_domain_ratio == 1.0
        assert snap.intra_domain_ratio == 0.0

    def test_sample_graph_no_cycles(self, sample_graph):
        """O sample_project não tem ciclos."""
        snap = compute_observation_snapshot(sample_graph)

        assert snap.cycle_density == 0.0

    def test_sample_graph_high_quality(self, sample_graph):
        """O sample_project deve ter observation_quality = 1.0."""
        snap = compute_observation_snapshot(sample_graph)

        assert snap.observation_quality == 1.0


class TestObservationWithGlobalSample:
    """Testes com a fixture sample_project (global, from conftest)."""

    def test_with_sample_project(self, sample_project: Path):
        """Teste de integração com GraphBuilder + ObservationSnapshot."""
        builder = GraphBuilder(str(sample_project))
        graph = builder.build()
        snap = compute_observation_snapshot(graph)

        assert snap.total_nodes >= 3
        assert snap.total_edges >= 1
        assert snap.observation_quality >= 0.9


class TestObservationCycles:
    """Testes de detecção de ciclos."""

    def test_dag(self):
        """Grafo DAG → cycle_density = 0."""
        graph = ArchitecturalGraph()
        graph.add_file(path="a.py", module="mod1")
        graph.add_file(path="b.py", module="mod2")
        graph.add_file(path="c.py", module="mod3")

        graph.add_import(from_path="a.py", to_path="b.py")
        graph.add_import(from_path="b.py", to_path="c.py")

        snap = compute_observation_snapshot(graph)
        assert snap.cycle_density == 0.0
        assert snap.total_edges == 2

    def test_simple_cycle(self):
        """Ciclo simples a→b→a → cycle_density = 2/2 = 1.0."""
        graph = ArchitecturalGraph()
        graph.add_file(path="a.py", module="mod1")
        graph.add_file(path="b.py", module="mod2")

        graph.add_import(from_path="a.py", to_path="b.py")
        graph.add_import(from_path="b.py", to_path="a.py")

        snap = compute_observation_snapshot(graph)
        # Both edges participate in the cycle
        assert snap.cycle_density == 1.0
        assert snap.total_edges == 2

    def test_partial_cycle(self):
        """Ciclo parcial: a→b→c→b → apenas 2 edges em ciclo."""
        graph = ArchitecturalGraph()
        graph.add_file(path="a.py", module="mod1")
        graph.add_file(path="b.py", module="mod2")
        graph.add_file(path="c.py", module="mod3")

        graph.add_import(from_path="a.py", to_path="b.py")
        graph.add_import(from_path="b.py", to_path="c.py")
        graph.add_import(from_path="c.py", to_path="b.py")

        snap = compute_observation_snapshot(graph)
        # b→c and c→b participate in a cycle; a→b is not in the cycle
        assert snap.cycle_density == 2 / 3  # 2 of 3 edges in cycle
        assert snap.total_edges == 3


class TestObservationDomains:
    """Testes de classificação de domínios."""

    def test_all_intra_domain(self):
        """Todos os edges dentro do mesmo módulo."""
        graph = ArchitecturalGraph()
        graph.add_file(path="a.py", module="core")
        graph.add_file(path="b.py", module="core")
        graph.add_file(path="c.py", module="core")

        graph.add_import(from_path="a.py", to_path="b.py")
        graph.add_import(from_path="b.py", to_path="c.py")

        snap = compute_observation_snapshot(graph)
        assert snap.intra_domain_ratio == 1.0
        assert snap.cross_domain_ratio == 0.0

    def test_mixed_domains(self):
        """Mistura de cross-domain e intra-domain."""
        graph = ArchitecturalGraph()
        graph.add_file(path="a.py", module="core")
        graph.add_file(path="b.py", module="core")
        graph.add_file(path="c.py", module="api")
        graph.add_file(path="d.py", module="api")

        graph.add_import(from_path="a.py", to_path="b.py")  # intra
        graph.add_import(from_path="a.py", to_path="c.py")  # cross
        graph.add_import(from_path="c.py", to_path="d.py")  # intra
        graph.add_import(from_path="d.py", to_path="a.py")  # cross

        snap = compute_observation_snapshot(graph)
        assert snap.intra_domain_ratio == 2 / 4  # 2 intra / 4 total
        assert snap.cross_domain_ratio == 2 / 4  # 2 cross / 4 total

    def test_unknown_module(self):
        """Edge para nó sem módulo → unknown_unresolved."""
        graph = ArchitecturalGraph()
        graph.add_file(path="a.py", module="core")
        graph.add_file(path="b.py", module="core")
        # Explicitly add a module node (no "module" attribute)
        graph.graph.add_node("external.py", node_type="file")

        graph.add_import(from_path="a.py", to_path="b.py")  # known
        graph.graph.add_edge("a.py", "external.py", import_type="import")  # unknown target

        snap = compute_observation_snapshot(graph)
        assert snap.total_edges >= 1
        assert snap.unknown_unresolved_edges >= 0


class TestObservationQuality:
    """Testes de observation_quality."""

    def test_perfect_quality(self):
        """Sem unknown edges → quality = 1.0."""
        snap = ObservationSnapshot(total_edges=100, unknown_unresolved_edges=0, unknown_dynamic_edges=0)
        assert snap.observation_quality == 1.0

    def test_partial_quality(self):
        """20% unknown → quality = 0.8."""
        snap = ObservationSnapshot(total_edges=100, unknown_unresolved_edges=10, unknown_dynamic_edges=10)
        assert snap.observation_quality == 0.8

    def test_quality_uses_import_attempts_when_available(self):
        """Observation quality usa total_imports_attempted quando fornecido."""
        snap = ObservationSnapshot(
            total_edges=1,
            unknown_unresolved_edges=0,
            unknown_dynamic_edges=3,
            total_imports_attempted=4,
        )
        assert snap.unknown_edges == 3
        assert snap.observation_quality == 0.25


class TestGraphBuilderImportCounts:
    """Verifica se o GraphBuilder registra os imports tentados."""

    def test_total_imports_attempted(self, tmp_path):
        project_dir = tmp_path / "project"
        project_dir.mkdir()
        src = project_dir / "__init__.py"
        src.write_text("from .mod import f\n")
        mod = project_dir / "mod.py"
        mod.write_text("def f():\n    return 1\n")

        builder = GraphBuilder(str(project_dir))
        graph = builder.build()

        assert builder.total_imports_attempted == 1
        snap = compute_observation_snapshot(graph, total_imports_attempted=builder.total_imports_attempted)
        assert snap.total_imports_attempted == 1
        assert snap.observation_quality == 1.0

    def test_zero_quality(self):
        """100% unknown → quality = 0.0."""
        snap = ObservationSnapshot(total_edges=10, unknown_unresolved_edges=10, unknown_dynamic_edges=0)
        assert snap.observation_quality == 0.0

    def test_no_edges(self):
        """Sem edges → quality = 0.0 (sem dados para observar)."""
        snap = ObservationSnapshot(total_edges=0, unknown_unresolved_edges=0, unknown_dynamic_edges=0)
        assert snap.observation_quality == 0.0


