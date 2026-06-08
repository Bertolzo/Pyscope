"""
PredictionEngine — Camada 5 do AGS.

Previsão de colapso arquitetural.
Simplificado no Sprint 1 — Sprint 4 adiciona Prophet/ARIMA.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class PredictionResult(BaseModel):
    days: int
    predicted_entropy: float
    predicted_cri: float
    confidence: float
    risk_level: str
    critical_date: str = ""


class PredictionReport(BaseModel):
    """Relatório de predição."""

    predictions: List[PredictionResult] = Field(default_factory=list)
    ai_maintainability_tokens: float = 0.0
    collapse_probability_90d: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()


class PredictionEngine:
    """Motor de predição — simplificado para Sprint 1."""

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        self.config = config or {}
        self.snapshot = PredictionReport()

    def analyze(
        self,
        structural_snapshot: Any,
        coupling_snapshot: Any,
        evolution_snapshot: Any,
        history: Optional[List[Dict[str, Any]]] = None,
    ) -> PredictionReport:
        self.structural = structural_snapshot
        self.coupling = coupling_snapshot
        self.evolution = evolution_snapshot
        self.history = history or []

        self._calculate_predictions()
        self._calculate_ai_maintainability()
        self._calculate_collapse_probability()

        return self.snapshot

    def _calculate_predictions(self) -> None:
        E0 = getattr(self.structural, "architectural_entropy", 0)
        CRI0 = getattr(self.structural, "cri_score", 100)
        dE = getattr(self.evolution, "entropy_first_derivative", 0)
        d2E = getattr(self.evolution, "entropy_second_derivative", 0)

        predictions: List[PredictionResult] = []

        for days in self.config.get("prediction_days", [30, 60, 90]):
            predicted_E = E0 + dE * days + 0.5 * d2E * (days**2)
            predicted_E = max(0, min(150, predicted_E))

            predicted_CRI = max(0, CRI0 - (predicted_E - E0) * 0.5)

            confidence = self._calculate_confidence(days)

            if predicted_E > 100:
                risk = "🔴 FATAL"
            elif predicted_E > 80:
                risk = "🔴 CRÍTICO"
            elif predicted_E > 60:
                risk = "🟠 ALTO"
            elif predicted_E > 40:
                risk = "🟡 MÉDIO"
            else:
                risk = "🟢 BAIXO"

            critical_date = ""
            if dE > 0 and predicted_E > 80:
                days_to_critical = (80 - E0) / dE if dE > 0 else float("inf")
                if 0 < days_to_critical < 365:
                    from datetime import datetime, timedelta

                    critical_date = (datetime.now() + timedelta(days=int(days_to_critical))).isoformat()[:10]

            predictions.append(PredictionResult(
                days=days,
                predicted_entropy=round(predicted_E, 2),
                predicted_cri=round(predicted_CRI, 2),
                confidence=round(confidence, 2),
                risk_level=risk,
                critical_date=critical_date,
            ))

        self.snapshot.predictions = predictions

    def _calculate_confidence(self, days: int) -> float:
        if not self.history:
            return max(0.3, 1.0 - days / 200)

        entropies = [h.get("architectural_entropy", h.get("entropy", 0)) for h in self.history[-20:]]
        if len(entropies) < 3:
            return 0.3

        import numpy as np

        variance = float(np.var(entropies))
        base_confidence = max(0.3, 1.0 - (variance / 100))
        time_decay = max(0.3, 1.0 - (days / 365))
        return round(base_confidence * time_decay, 2)

    def _calculate_ai_maintainability(self) -> None:
        total_files = getattr(self.structural, "total_files", 0)
        avg_context = 500.0

        high_cost = getattr(self.structural, "high_context_cost_files", [])
        if high_cost:
            avg_context = sum(f.get("context_cost", 0) for f in high_cost) / len(high_cost)

        entropy = getattr(self.structural, "architectural_entropy", 0)
        complexity_factor = 1 + (entropy / 100)

        tokens = avg_context * total_files * complexity_factor * 4

        gradient = getattr(self.evolution, "gradient_classification", "")
        if gradient == "collapsing":
            tokens *= 2

        self.snapshot.ai_maintainability_tokens = round(tokens, 0)

    def _calculate_collapse_probability(self) -> None:
        if not self.snapshot.predictions:
            self.snapshot.collapse_probability_90d = 0.0
            return

        p90 = next((p for p in self.snapshot.predictions if p.days == 90), None)
        if not p90:
            self.snapshot.collapse_probability_90d = 0.0
            return

        E90 = p90.predicted_entropy
        if E90 > 100:
            prob = 0.95
        elif E90 > 80:
            prob = 0.75
        elif E90 > 60:
            prob = 0.45
        elif E90 > 40:
            prob = 0.20
        else:
            prob = 0.05

        gradient = getattr(self.evolution, "gradient_classification", "")
        if gradient == "collapsing":
            prob = min(1.0, prob + 0.15)
        elif gradient == "degrading":
            prob = min(1.0, prob + 0.05)

        self.snapshot.collapse_probability_90d = round(prob, 2)
