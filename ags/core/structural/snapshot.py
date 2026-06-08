"""
StructuralSnapshot — Modelo de dados do estado estrutural.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class StructuralSnapshot(BaseModel):
    """Snapshot do estado estrutural do repositório."""

    # CRI
    radon_mi_score: float = 0.0
    cyclomatic_score: float = 0.0
    god_object_score: float = 0.0
    boundary_violation_score: float = 0.0
    context_cost_score: float = 0.0
    test_coverage_score: Optional[float] = None
    type_coverage_score: float = 0.0
    cri_score: float = 0.0
    cri_classification: str = ""

    # Entropy
    architectural_entropy: float = 0.0
    entropy_classification: str = ""

    # AGP
    agp_score: float = 0.0
    agp_domains: List[str] = Field(default_factory=list)
    agp_classification: str = ""

    # Cycles
    cycles: List[Dict[str, Any]] = Field(default_factory=list)
    cycle_count: int = 0

    # Violations
    boundary_violations: List[Dict[str, Any]] = Field(default_factory=list)
    dependency_violations: List[Dict[str, Any]] = Field(default_factory=list)
    large_files: List[Dict[str, Any]] = Field(default_factory=list)
    god_classes: List[Dict[str, Any]] = Field(default_factory=list)
    high_context_cost_files: List[Dict[str, Any]] = Field(default_factory=list)
    responsibility_conflicts: List[Dict[str, Any]] = Field(default_factory=list)

    # Counters
    total_files: int = 0
    total_lines: int = 0
    total_functions: int = 0
    total_classes: int = 0

    # Project
    project_path: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()
