"""
StructuralAnalyzer — Camada 2 do AGS.

Mede o estado estrutural atual consumindo ArchitecturalGraph.
"""

from __future__ import annotations

import logging
import warnings
from typing import Any, Dict, List, Optional, Set

from ags.core.graph.architectural_graph import ArchitecturalGraph
from ags.core.graph.communities import detect_communities
from ags.core.graph.metrics import cycle_density

from .snapshot import StructuralSnapshot

logger = logging.getLogger(__name__)


class StructuralAnalyzer:
    """Analisador estrutural — consome ArchitecturalGraph."""

    def __init__(self, graph: ArchitecturalGraph, config: Optional[Dict[str, Any]] = None) -> None:
        self.graph = graph
        self.config = config or {}
        self.snapshot = StructuralSnapshot()

    def analyze(self) -> StructuralSnapshot:
        """Pipeline completo de análise estrutural."""
        self.snapshot.total_files = self.graph.file_count
        self.snapshot.total_lines = sum(
            f.loc for f in self.graph.files.values()
        )
        self.snapshot.total_classes = sum(
            len(f.classes) for f in self.graph.files.values()
        )
        self.snapshot.total_functions = sum(
            len(f.functions) for f in self.graph.files.values()
        )

        self._calculate_cycles()
        self._calculate_boundary_violations()
        self._calculate_context_costs()
        self._calculate_god_objects()
        self._calculate_agp()
        self._calculate_radon_metrics()
        self._estimate_coverage()
        self._calculate_cri()
        self._calculate_entropy()

        return self.snapshot

    def _calculate_cycles(self) -> None:
        cycles = self.graph.detect_cycles()
        self.snapshot.cycles = [
            {"cycle": cycle, "severity": 8} for cycle in cycles
        ]
        self.snapshot.cycle_count = len(cycles)

    def _calculate_boundary_violations(self) -> None:
        violations: List[Dict[str, Any]] = []

        for path, node_data in self.graph.graph.nodes(data=True):
            if node_data.get("node_type") != "file":
                continue

            file_analysis = self.graph.files.get(path)
            if not file_analysis:
                continue

            for imp_data in self.graph.graph.out_edges(path, data=True):
                _, to_node, edge_data = imp_data
                if edge_data.get("level", 0) > 2:
                    violations.append({
                        "type": "deep_relative_import",
                        "file": path,
                        "detail": f"level {edge_data['level']}",
                        "severity": 6,
                    })

            for imp_data in self.graph.graph.out_edges(path, data=True):
                _, to_node, edge_data = imp_data
                if edge_data.get("is_cross_module"):
                    violations.append({
                        "type": "cross_module_import",
                        "file": path,
                        "detail": f"{file_analysis.module} → {to_node}",
                        "severity": 4,
                    })

        self.snapshot.boundary_violations = violations

        bv_penalty = sum(v.get("severity", 0) for v in violations)
        self.snapshot.boundary_violation_score = max(0.0, 100.0 - bv_penalty * 1.5)

    def _calculate_context_costs(self) -> None:
        high_cost: List[Dict[str, Any]] = []
        max_cost = self.config.get("max_context_cost", 1500)

        for path in self.graph.get_file_nodes():
            radius = self.graph.context_radius(path, depth=2)
            if radius > max_cost:
                high_cost.append({
                    "file": path,
                    "context_cost": radius,
                    "threshold": max_cost,
                })

        self.snapshot.high_context_cost_files = high_cost
        total = max(self.graph.file_count, 1)
        self.snapshot.context_cost_score = max(0.0, 100.0 - (len(high_cost) / total) * 100)

    def _calculate_god_objects(self) -> None:
        god_classes: List[Dict[str, Any]] = []
        large_files: List[Dict[str, Any]] = []
        god_penalty = 0

        for path, node in self.graph.files.items():
            for cls in node.classes:
                if cls.get("lines", 0) > 500:
                    god_penalty += self.config.get("penalty_super_god_class", 6)
                    god_classes.append({**cls, "file": path})
                elif cls.get("lines", 0) > 200:
                    god_penalty += self.config.get("penalty_god_class", 4)
                    god_classes.append({**cls, "file": path})

            if node.loc > 1000:
                god_penalty += self.config.get("penalty_very_large_file", 5)
                large_files.append({"file": path, "lines": node.loc})
            elif node.loc > 300:
                god_penalty += self.config.get("penalty_large_file", 3)
                large_files.append({"file": path, "lines": node.loc})

        self.snapshot.god_classes = god_classes
        self.snapshot.large_files = large_files
        self.snapshot.god_object_score = max(0.0, 100.0 - god_penalty * 2)

    def _calculate_agp(self) -> None:
        """
        L6 — Governance: Calculate Architectural Governance Purity.

        FASM Analysis:
        - Ontology: Governance
        - Theory: Axioma 4 (CRI is composite)
        - Phenomenon: Governance Compliance
        - State Dimensions: agp
        - Metrics: AGP Score (%)
        - Invariants: 0 <= agp <= 100
        - Governance: Merge gate decisions
        - Memory: Included in embedding (index 7)
        """
        detected_domains: Set[str] = set()
        domain_keywords = self.config.get("agp_domain_keywords", {})

        for path, node in self.graph.files.items():
            content = path.lower() + " " + " ".join(
                f"{fn['name']}" for fn in node.functions
            )
            for domain, keywords in domain_keywords.items():
                for kw in keywords:
                    if kw in content:
                        detected_domains.add(domain)
                        break

        self.snapshot.agp_domains = sorted(detected_domains)
        domain_count = len(detected_domains)
        max_domains = self.config.get("agp_max_domains", 3)

        # Fix: Handle domain_count == 0 (no domains detected)
        if domain_count == 0:
            self.snapshot.agp_score = 100.0
        elif domain_count <= max_domains:
            self.snapshot.agp_score = 100.0 - (domain_count - 1) * 15
        else:
            self.snapshot.agp_score = max(
                0.0,
                100.0 - (domain_count - max_domains) * 20 - (max_domains - 1) * 15,
            )

        if domain_count <= 2:
            self.snapshot.agp_classification = "🟢 Produto focado"
        elif domain_count <= 3:
            self.snapshot.agp_classification = "🟡 Produto com extensões"
        elif domain_count <= 5:
            self.snapshot.agp_classification = "🟠 Tornando-se plataforma"
        else:
            self.snapshot.agp_classification = "🔴 Plataforma não intencional"

    def _calculate_radon_metrics(self) -> None:
        try:
            from radon.complexity import cc_visit
            from radon.metrics import mi_visit

            total_mi = 0.0
            total_cc = 0.0
            file_count = 0

            for path, node in self.graph.files.items():
                try:
                    from pathlib import Path

                    content = Path(path).read_text(encoding="utf-8", errors="ignore")
                    mi = mi_visit(content, True)
                    cc_list = cc_visit(content)
                    total_mi += mi
                    total_cc += sum(c.complexity for c in cc_list)
                    file_count += 1
                except Exception:
                    continue

            if file_count > 0:
                self.snapshot.radon_mi_score = total_mi / file_count
                self.snapshot.cyclomatic_score = total_cc / file_count
        except ImportError:
            warnings.warn(
                "radon não instalado — usando valores padrão para MI e CC. "
                "Instale com: pip install radon",
                stacklevel=2,
            )
            self.snapshot.radon_mi_score = 50.0
            self.snapshot.cyclomatic_score = 5.0

        self.snapshot.cyclomatic_score = max(
            0.0, 100.0 - self.snapshot.cyclomatic_score * 5
        )

    def _estimate_coverage(self) -> None:
        test_files = sum(
            1 for p in self.graph.get_file_nodes()
            if "test" in p.lower() or "spec" in p.lower()
        )
        prod_files = max(self.graph.file_count - test_files, 1)

        if test_files > 0 and test_files / prod_files > 0:
            self.snapshot.test_coverage_score = min(100.0, (test_files / prod_files) * 100)
        else:
            self.snapshot.test_coverage_score = None

        typed_functions = 0
        total_functions = 0
        for node in self.graph.files.values():
            for func in node.functions:
                total_functions += 1
                if func.get("return_annotation") or func.get("has_type_hints"):
                    typed_functions += 1

        self.snapshot.type_coverage_score = (
            (typed_functions / max(total_functions, 1)) * 100
        )

    def _calculate_cri(self) -> None:
        cfg = self.config
        weights = {
            "radon_mi": cfg.get("weight_radon_mi", 0.15),
            "cyclomatic": cfg.get("weight_cyclomatic", 0.15),
            "god_objects": cfg.get("weight_god_objects", 0.15),
            "boundary": cfg.get("weight_boundary_violations", 0.20),
            "context_cost": cfg.get("weight_context_cost", 0.20),
            "test": cfg.get("weight_test_coverage", 0.10),
            "type": cfg.get("weight_type_coverage", 0.05),
        }

        test_score = self.snapshot.test_coverage_score if self.snapshot.test_coverage_score is not None else 50.0

        cri = (
            self.snapshot.radon_mi_score * weights["radon_mi"]
            + self.snapshot.cyclomatic_score * weights["cyclomatic"]
            + self.snapshot.god_object_score * weights["god_objects"]
            + self.snapshot.boundary_violation_score * weights["boundary"]
            + self.snapshot.context_cost_score * weights["context_cost"]
            + test_score * weights["test"]
            + self.snapshot.type_coverage_score * weights["type"]
        )

        self.snapshot.cri_score = round(cri, 2)

        if self.snapshot.cri_score >= 90:
            self.snapshot.cri_classification = "🟢 Excelente"
        elif self.snapshot.cri_score >= 70:
            self.snapshot.cri_classification = "🟡 Saudável"
        elif self.snapshot.cri_score >= 50:
            self.snapshot.cri_classification = "🟠 Atenção"
        elif self.snapshot.cri_score >= 30:
            self.snapshot.cri_classification = "🔴 Débito alto"
        else:
            self.snapshot.cri_classification = "⚫ Reescrever"

    def _calculate_entropy(self) -> None:
        cfg = self.config
        entropy = (
            len(self.snapshot.boundary_violations) * 3
            + len(self.snapshot.dependency_violations) * 4
            + len(self.snapshot.god_classes) * 3
            + len(self.snapshot.large_files) * 2
            + len(self.snapshot.high_context_cost_files) * 2
            + len(self.snapshot.responsibility_conflicts) * 2
            + self.snapshot.cycle_count * cfg.get("penalty_cycle", 8)
            + max(0, len(self.snapshot.agp_domains) - cfg.get("agp_max_domains", 3))
            * cfg.get("penalty_agp_high", 3)
        )

        self.snapshot.architectural_entropy = round(entropy, 2)

        if self.snapshot.architectural_entropy <= 20:
            self.snapshot.entropy_classification = "🟢 Excelente"
        elif self.snapshot.architectural_entropy <= 40:
            self.snapshot.entropy_classification = "🟡 Boa"
        elif self.snapshot.architectural_entropy <= 60:
            self.snapshot.entropy_classification = "🟠 Atenção"
        elif self.snapshot.architectural_entropy <= 80:
            self.snapshot.entropy_classification = "🔴 Ruim"
        else:
            self.snapshot.entropy_classification = "⚫ Crítica"
