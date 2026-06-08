# Architectural Governance

**Layer**: 6
**Purpose**: Define decisions based on state

---

## Definition

Governance produces decisions based on:

- Current State
- Future State
- Dynamics
- Rules

Governance never consumes raw implementation details directly.

---

## Decision Types

### ALLOW

**Condition**: All rules satisfied.
**Action**: Proceed with merge/deployment.
**Example**: CRI > 80, no regressions, no violations.

---

### WARN

**Condition**: Some rules violated, but not critical.
**Action**: Proceed with caution.
**Example**: CRI between 60-80, minor regressions.

---

### BLOCK

**Condition**: Critical rules violated.
**Action**: Stop merge/deployment.
**Example**: CRI < 60, major regressions, FATAL violations.

---

## Rules

### Budget Rules

| Metric | Limit | Warning | Critical |
|--------|-------|---------|----------|
| Entropy | 100 | 60% | 80% |
| Coupling | 100 | 40% | 60% |
| Domain | 5 | 60% | 80% |
| CRI | 100 | 40% | 60% |

---

### Regression Rules

| Metric | Threshold | Action |
|--------|-----------|--------|
| CRI decrease | > 5 points | BLOCK |
| Entropy increase | > 10 points | BLOCK |
| New cycles | > 0 | BLOCK |

---

### Severity Rules

| Severity | Action |
|----------|--------|
| FATAL | BLOCK |
| CRITICAL | BLOCK |
| ERROR | WARN |
| WARNING | INFO |
| INFO | None |

---

## Governance Engine

```python
GovernanceReport = {
    budgets: List[BudgetStatus],
    violations: List[Violation],
    regression_detected: bool,
    regression_details: List[str],
    merge_allowed: bool,
    gate_status: str
}
```

---

## Rules

1. Governance produces decisions, not measurements.
2. Governance consumes State Vector, not raw data.
3. Every rule must be traceable to metrics or axioms.
4. Governance cannot be redefined by lower layers.
