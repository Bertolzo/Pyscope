# Architectural Applicability

**Layer**: 9 (Applicability)
**Purpose**: Define the epistemic limits of the Pyscope model

---

## Core Principle

The Pyscope model is a model of architecture, not architecture itself.

All architectural observations are estimations derived from source code artifacts.

The State Vector is a representation of architecture, not the architecture itself.

---

## What Pyscope Can Explain

### Structural Phenomena

- **Structural coupling**: How many dependencies cross architectural boundaries
- **Boundary violations**: File-level operational leakage between domains
- **Architectural drift**: How architecture diverges from its baseline over time
- **Governance compliance**: How well the architecture adheres to governance rules
- **Architectural reachability**: Blast radius of a change

### Dynamic Phenomena

- **Entropy evolution**: How architectural debt accumulates over time
- **Rate of deterioration**: Speed of architectural degradation
- **Acceleration of deterioration**: When degradation is accelerating
- **Structural divergence**: How architecture changes between snapshots

---

## What Pyscope Cannot Explain

### Non-structural Outcomes

- **Business success**: Revenue, market share, product-market fit
- **Developer productivity**: Lines of code per developer, velocity
- **Team satisfaction**: Morale, turnover, collaboration quality
- **Product quality**: Feature correctness, user experience
- **Delivery performance**: Release frequency, time to market

### Non-structural Causes

- **Why a specific bug occurred**: AGS observes structure, not behavior
- **Why a team chose a design**: AGS observes outcomes, not decisions
- **Why a project succeeded**: AGS observes architecture, not execution

---

## What Pyscope May Correlate With

Pyscope may correlate with these outcomes, but does NOT directly measure them:

| Outcome | Relationship | Mechanism |
|---------|-------------|-----------|
| Maintainability | Direct correlation | High entropy → harder to maintain |
| Change failure rate | Moderate correlation | High coupling → cascading failures |
| MTTR | Moderate correlation | High context radius → more files to understand |
| Delivery velocity | Weak correlation | High entanglements → slower delivery |
| Cognitive load | Direct correlation | High complexity → harder to understand |

---

## Observation Limitations

### Source of Truth Limitations

| Limitation | Impact | Mitigation |
|------------|--------|------------|
| AST parsing errors | Missing dependencies | Graceful degradation |
| Dynamic imports | Undetected dependencies | Static analysis best-effort |
| Configuration files | Ignored runtime wiring | Manual annotation |
| External services | Undetected couplings | Boundary configuration |

### Temporal Limitations

| Limitation | Impact | Mitigation |
|------------|--------|------------|
| Snapshot frequency | Missing short-term changes | More frequent snapshots |
| History depth | Inaccurate trends | Configurable window |
| Polyfit accuracy | Approximation error | Higher-order models |

---

## Scientific Humility

The Pyscope model makes no claim to:

- Predict business outcomes
- Replace human architectural judgment
- Measure unobservable architectural properties
- Provide certainty about future states

The model provides:

- Observable measurements
- Quantifiable trends
- Reproducible metrics
- Formalized governance

---

## Rules

1. No metric may claim to measure what Pyscope cannot explain.
2. Correlation claims must be explicitly caveated.
3. Observation limitations must be documented for each metric.
4. Epistemic limits cannot be removed without updating this document.
