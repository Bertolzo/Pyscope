# Scientific Validation Protocol

**Layer**: 9 (Calibration)
**Purpose**: Checklist for validating all changes against the FASM

---

## Overview

Every change to the AGS system MUST pass the Scientific Validation Protocol.

The protocol ensures that:

- The change respects the FASM hierarchy
- No conceptual drift occurs
- All epistemic limits are respected
- The model remains internally consistent

---

## The 10 Questions

### Q1 — Ontology

Which ontology entities are affected?

- Architecture
- Boundary
- Dependency
- Violation
- State
- Dynamics
- Governance
- Memory
- Causal Factor

**Rule**: Every affected entity must be explicitly listed.

---

### Q2 — Theory

Which axioms are involved?

1. Architecture is graphable
2. Architecture has state
3. Architecture changes
4. Entropy is cumulative
5. Half-Life is not prediction
6. CRI is composite
7. Observations are approximations
8. Architecture has epistemic limits

**Rule**: If a change conflicts with an axiom, the change is REJECTED.
**Rule**: If a change introduces a new principle, it must be documented.

---

### Q3 — Phenomena

Which phenomena are affected?

- Architectural Entropy
- Structural Pressure
- Structural Cohesion
- Operational Boundary Leakage
- Architectural Drift
- Governance Compliance
- Architectural Reachability
- Architectural Integrity

**Rule**: Every metric must map to a phenomenon.
**Rule**: If a metric has no phenomenon, the change is REJECTED.

---

### Q4 — Causal Factors

Which causal factors explain the observed change?

Examples:

- New module added
- Circular dependency introduced
- Incomplete refactoring
- Cross-domain coupling increased

**Rule**: Every observation should have an associated causal factor.

---

### Q5 — State Vector

Which state dimensions are affected?

| Index | Dimension | Unit | Bounds |
|-------|-----------|------|--------|
| 0 | entropy.current | points | [0, ∞) |
| 1 | entropy.velocity | points/day | (-∞, ∞) |
| 2 | entropy.acceleration | points/day² | (-∞, ∞) |
| 3 | acp | % | [0, 100] |
| 4 | dci | % | [0, 100] |
| 5 | boundary_leakage | ratio | [0, 1] |
| 6 | cri | score | [0, 100] |
| 7 | agp | % | [0, 100] |
| 8 | context_radius | files | [0, ∞) |
| 9 | dependency_density | ratio | [0, 1] |

**Rule**: If a measurement cannot be represented in S(t), the change is REJECTED.

---

### Q6 — Metrics

Which metrics are affected?

| Name | Phenomenon | Unit | Invariant |
|------|------------|------|-----------|
| Entropy Score | Architectural Entropy | points | E >= 0 |
| Entropy Velocity | Rate of Change | points/day | real |
| Entropy Acceleration | Acceleration | points/day² | real |
| ACP | Structural Pressure | % | [0, 100] |
| DCI | Structural Cohesion | % | [0, 100] |
| Boundary Leakage | Operational Leakage | ratio | [0, 1] |
| CRI | Architectural Integrity | score | [0, 100] |
| AGP | Governance Compliance | % | [0, 100] |
| Context Radius | Architectural Reachability | files | >= 0 |
| Dependency Density | Coupling Intensity | ratio | [0, 1] |
| Half-Life | Rate of Change | months | > 0 or inf |

**Rule**: Each metric must define Phenomenon, Units, Bounds, Formula, Interpretation, Invariant, State Dimension.

---

### Q7 — Invariants

Which invariants must remain true?

**Rule**: All invariants must remain true after the change.
**Rule**: No invariant may be relaxed for a specific case.

---

### Q8 — Governance

What governance behavior changes?

Decisions affected:

- ALLOW
- WARN
- BLOCK

**Rule**: Governance changes must be traceable to metrics or axioms.
**Rule**: Governance never consumes raw implementation details.

---

### Q9 — Memory

What memory representation changes?

**Rule**: Memory stores state representations, not implementation artifacts.
**Rule**: All state dimensions must be convertible to embedding.

---

### Q10 — Applicability

What is the domain of applicability?

- What can the model explain after this change?
- What can the model NOT explain?
- What is the observation uncertainty?

**Rule**: No metric may claim to measure what AGS cannot explain.
**Rule**: Observation limitations must be documented.

---

## Checklist Template

```
## FASM Analysis

### Q1 — Ontology
Entities affected: ...

### Q2 — Theory
Axioms involved: ...

### Q3 — Phenomena
Phenomena affected: ...

### Q4 — Causal Factors
Causal factors: ...

### Q5 — State Vector
Dimensions affected: ...

### Q6 — Metrics
Metrics affected: ...

### Q7 — Invariants
Invariants to preserve: ...

### Q8 — Governance
Governance impact: ...

### Q9 — Memory
Memory impact: ...

### Q10 — Applicability
Domain of applicability: ...
Observation uncertainty: ...

### Verdict
APPROVED or REJECTED
Justification: ...
```

---

## Rules

1. Every change must answer all 10 questions.
2. If any question cannot be answered, the change is REJECTED.
3. The FASM is the source of truth.
4. The model is primary. The implementation is secondary.
