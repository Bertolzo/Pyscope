"""
FixtureSpec — Construction rules (not expected values).

Expectations are DERIVED from these rules, not hardcoded.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from ags.synthetic.regimes import RegimeName, RegimeRange, REGIME_TAXONOMY


@dataclass(frozen=True)
class FixtureSpec:
    """
    Construction rules for a synthetic architecture.

    FASM Analysis:
    - Ontology: Architecture
    - Theory: Axiom 1 (Architecture is graphable)
    - Phenomenon: All structural phenomena
    - Causal Factors: Construction parameters cause specific metric behaviors
    - State Vector: All dimensions
    - Invariants: Deterministic given seed
    - Applicability: Controlled experimental conditions

    Important: This spec defines CONSTRUCTION RULES, not expected values.
    Expected values are derived from the rules.
    """

    regime: RegimeName
    seed: int = 42

    # Optional explicit overrides (rare — used for special tests)
    domains: Optional[int] = None
    modules_per_domain: Optional[int] = None
    files_per_module: Optional[int] = None

    @property
    def regime_range(self) -> RegimeRange:
        return REGIME_TAXONOMY[self.regime]

    def to_dict(self) -> dict:
        return {
            "regime": self.regime.value,
            "seed": self.seed,
            "domains": self.domains,
            "modules_per_domain": self.modules_per_domain,
            "files_per_module": self.files_per_module,
        }
