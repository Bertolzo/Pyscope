"""
GovernanceEngine — Camada 6 do AGS.

Transforma métricas em decisões: gates, policies, violations, severity.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class BudgetStatus(BaseModel):
    name: str
    limit: float
    current: float
    remaining: float
    percentage: float
    status: str


class Violation(BaseModel):
    rule: str
    file: str
    value: float
    limit: float
    severity: str
    message: str


class GovernanceReport(BaseModel):
    """Relatório de governança."""

    budgets: List[BudgetStatus] = Field(default_factory=list)
    violations: List[Violation] = Field(default_factory=list)
    regression_detected: bool = False
    regression_details: List[str] = Field(default_factory=list)
    merge_allowed: bool = True
    gate_status: str = "PASS"

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()


class GovernanceEngine:
    """Motor de governança — Camada 6 do AGS."""

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        self.config = config or {}
        self.snapshot = GovernanceReport()

    def analyze(
        self,
        structural_snapshot: Any,
        coupling_snapshot: Any,
        evolution_snapshot: Any,
        previous_snapshot: Any = None,
        baseline_snapshot: Any = None,
    ) -> GovernanceReport:
        self.structural = structural_snapshot
        self.coupling = coupling_snapshot
        self.evolution = evolution_snapshot
        self.previous = previous_snapshot
        self.baseline = baseline_snapshot

        self._check_budgets()
        self._check_regression_gate()
        self._check_severity()
        self._determine_merge_status()

        return self.snapshot

    def _check_budgets(self) -> None:
        budgets: List[BudgetStatus] = []

        entropy_limit = self.config.get("entropy_budget", 100)
        entropy_current = getattr(self.structural, "architectural_entropy", 0)
        entropy_remaining = max(0, entropy_limit - entropy_current)
        entropy_pct = (entropy_current / entropy_limit) * 100 if entropy_limit > 0 else 0
        entropy_status = "ok" if entropy_pct < 60 else "warning" if entropy_pct < 80 else "exceeded"
        budgets.append(BudgetStatus(
            name="Entropy", limit=entropy_limit, current=entropy_current,
            remaining=entropy_remaining, percentage=entropy_pct, status=entropy_status,
        ))

        if self.coupling and getattr(self.coupling, "acp", None):
            acp_score = self.coupling.acp.acp_score
            acp_current = 100 - acp_score
            acp_remaining = max(0, 100 - acp_current)
            acp_pct = acp_current
            acp_status = "ok" if acp_pct < 40 else "warning" if acp_pct < 60 else "exceeded"
            budgets.append(BudgetStatus(
                name="Coupling", limit=100, current=acp_current,
                remaining=acp_remaining, percentage=acp_pct, status=acp_status,
            ))

        domain_limit = self.config.get("domain_budget", 5)
        domain_current = len(getattr(self.structural, "agp_domains", []))
        domain_remaining = max(0, domain_limit - domain_current)
        domain_pct = (domain_current / domain_limit) * 100 if domain_limit > 0 else 0
        domain_status = "ok" if domain_pct < 60 else "warning" if domain_pct < 80 else "exceeded"
        budgets.append(BudgetStatus(
            name="Domain", limit=domain_limit, current=domain_current,
            remaining=domain_remaining, percentage=domain_pct, status=domain_status,
        ))

        cri_score = getattr(self.structural, "cri_score", 100)
        cri_current = 100 - cri_score
        cri_remaining = max(0, 100 - cri_current)
        cri_pct = cri_current
        cri_status = "ok" if cri_pct < 40 else "warning" if cri_pct < 60 else "exceeded"
        budgets.append(BudgetStatus(
            name="CRI", limit=100, current=cri_current,
            remaining=cri_remaining, percentage=cri_pct, status=cri_status,
        ))

        self.snapshot.budgets = budgets

    def _check_regression_gate(self) -> None:
        if not self.previous:
            return

        regressions: List[str] = []

        cri_current = getattr(self.structural, "cri_score", 0)
        cri_previous = getattr(self.previous, "cri_score", cri_current)
        threshold = self.config.get("regression_cri_threshold", 5)
        if cri_current < cri_previous - threshold:
            regressions.append(f"CRI regrediu: {cri_previous:.1f} → {cri_current:.1f}")

        entropy_current = getattr(self.structural, "architectural_entropy", 0)
        entropy_previous = getattr(self.previous, "architectural_entropy", entropy_current)
        threshold = self.config.get("regression_entropy_threshold", 10)
        if entropy_current > entropy_previous + threshold:
            regressions.append(f"Entropia aumentou: {entropy_previous:.1f} → {entropy_current:.1f}")

        cycles_current = getattr(self.structural, "cycle_count", 0)
        cycles_previous = getattr(self.previous, "cycle_count", cycles_current)
        if cycles_current > cycles_previous:
            regressions.append(f"Novos ciclos: {cycles_previous} → {cycles_current}")

        self.snapshot.regression_detected = len(regressions) > 0
        self.snapshot.regression_details = regressions

    def _check_severity(self) -> None:
        violations: List[Violation] = []

        for bv in getattr(self.structural, "boundary_violations", []):
            if bv.get("type") == "syspath_insert":
                violations.append(Violation(
                    rule="syspath_insert", file=bv.get("file", ""),
                    value=1, limit=0, severity="CRITICAL",
                    message=f"sys.path.insert em {bv.get('file', '')}",
                ))

        cycle_count = getattr(self.structural, "cycle_count", 0)
        if cycle_count > 0:
            violations.append(Violation(
                rule="dependency_cycle", file="",
                value=cycle_count, limit=0, severity="CRITICAL",
                message=f"{cycle_count} ciclos de dependência detectados",
            ))

        for gc in getattr(self.structural, "god_classes", []):
            if gc.get("lines", 0) > 500:
                violations.append(Violation(
                    rule="super_god_object", file=gc.get("file", ""),
                    value=gc.get("lines", 0), limit=200, severity="ERROR",
                    message=f"God Object {gc.get('name', '')}: {gc.get('lines', 0)} linhas",
                ))

        for lf in getattr(self.structural, "large_files", []):
            if lf.get("lines", 0) > 1000:
                violations.append(Violation(
                    rule="very_large_file", file=lf.get("file", ""),
                    value=lf.get("lines", 0), limit=300, severity="ERROR",
                    message=f"Arquivo {lf.get('lines', 0)} linhas",
                ))

        for lf in getattr(self.structural, "large_files", []):
            lines = lf.get("lines", 0)
            if 300 < lines <= 1000:
                violations.append(Violation(
                    rule="large_file", file=lf.get("file", ""),
                    value=lines, limit=300, severity="WARNING",
                    message=f"Arquivo {lines} linhas",
                ))

        for hcc in getattr(self.structural, "high_context_cost_files", []):
            violations.append(Violation(
                rule="high_context_cost", file=hcc.get("file", ""),
                value=hcc.get("context_cost", 0), limit=1500, severity="WARNING",
                message=f"Context Cost = {hcc.get('context_cost', 0)}",
            ))

        test_cov = getattr(self.structural, "test_coverage_score", None)
        if test_cov is not None and test_cov < 80:
            violations.append(Violation(
                rule="low_test_coverage", file="",
                value=test_cov, limit=80, severity="INFO",
                message=f"Cobertura de testes = {test_cov:.1f}%",
            ))

        self.snapshot.violations = violations

    def _determine_merge_status(self) -> None:
        if self.snapshot.regression_detected:
            self.snapshot.merge_allowed = False
            self.snapshot.gate_status = "BLOCKED: Regressão arquitetural detectada"
            return

        fatal_count = sum(1 for v in self.snapshot.violations if v.severity == "FATAL")
        if fatal_count > 0:
            self.snapshot.merge_allowed = False
            self.snapshot.gate_status = f"BLOCKED: {fatal_count} violação(ões) FATAL"
            return

        critical_count = sum(1 for v in self.snapshot.violations if v.severity == "CRITICAL")
        if critical_count > 0:
            self.snapshot.merge_allowed = False
            self.snapshot.gate_status = f"BLOCKED: {critical_count} violação(ões) CRITICAL"
            return

        error_count = sum(1 for v in self.snapshot.violations if v.severity == "ERROR")
        if error_count > 0:
            self.snapshot.merge_allowed = True
            self.snapshot.gate_status = f"WARNING: {error_count} erro(s) — merge permitido com cautela"
            return

        warning_count = sum(1 for v in self.snapshot.violations if v.severity == "WARNING")
        if warning_count > 0:
            self.snapshot.merge_allowed = True
            self.snapshot.gate_status = f"WARNING: {warning_count} aviso(s)"
            return

        self.snapshot.merge_allowed = True
        self.snapshot.gate_status = "PASS: Todas as regras atendidas"
