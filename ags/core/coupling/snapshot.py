"""
CouplingReport — Modelo de dados de acoplamento.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from pydantic import BaseModel, Field


class ACPResult(BaseModel):
    """Architectural Coupling Pressure."""

    domain_count: int = 0
    total_cross_imports: int = 0
    cross_import_matrix: Dict[str, Dict[str, int]] = Field(default_factory=dict)
    acp_score: float = 0.0
    acp_classification: str = ""
    most_coupled_pairs: List[Tuple[str, str, int]] = Field(default_factory=list)


class DCIResult(BaseModel):
    """Domain Contamination Index."""

    bidirectional_pairs: List[Tuple[str, str]] = Field(default_factory=list)
    contaminated_communities: List[int] = Field(default_factory=list)
    contamination_ratio: float = 0.0
    dci_score: float = 0.0
    dci_classification: str = ""


class CouplingReport(BaseModel):
    """Relatório completo de acoplamento."""

    acp: Optional[ACPResult] = None
    dci: Optional[DCIResult] = None
    context_radius_avg: float = 0.0
    context_radius_max: int = 0
    context_radius_classification: str = ""
    dependency_density: float = 0.0
    communities_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()
