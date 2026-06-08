# FASM — Formal Architectural State Model

**Version**: 1.0
**Date**: 2026-06-03
**Status**: Active

---

## Purpose

The FASM is the authoritative model for Pyscope (Architectural Governance System).

The codebase is NOT the source of truth.

The ontology, theory, state model, dynamics model, and invariants are the source of truth.

Every proposal, implementation, refactor, metric, test, optimization, bug fix, benchmark, prediction, governance rule, or memory mechanism MUST be validated against the FASM before acceptance.

---

## The Architectural Digital Twin

What is emerging is not just a formal model — it's an **Architectural Digital Twin**.

```
FASM (formalism)
    ↓
Architectural Twin (observed entity)
    ↓
Governance Engine (decisions)
    ↓
Architectural Decisions (outcomes)
```

The FASM is the mathematical model that sustains a digital twin of the architecture.

This positioning moves Pyscope from "static analysis tool" to "architectural observability system with state model."

---

## FASM Hierarchy

The model is organized in the following order:

```
Layer 0  — Ontology
Layer 1  — Theory
Layer 2  — Phenomena
Layer 3  — Causal Factors
Layer 4  — State Vector
Layer 5  — Dynamics
Layer 6  — Metrics
Layer 7  — Governance
Layer 8  — Memory
Layer 9  — Applicability
Layer 10 — Calibration
Layer 11 — Implementation
```

Dependency direction is strictly top-down.

- Implementation cannot redefine Metrics.
- Metrics cannot redefine Dynamics.
- Dynamics cannot redefine State.
- State cannot redefine Phenomena.
- Phenomena cannot redefine Theory.
- Theory cannot redefine Ontology.

Violations must be rejected.

---

## Layer Definitions

### Layer 0 — Ontology

Defines what exists.

Allowed entities:

- Architecture
- Boundary
- Dependency
- Violation
- State
- Dynamics
- Governance
- Memory
- Causal Factor

No implementation may introduce a new entity without updating the Ontology.

---

### Layer 1 — Theory

Defines architectural truths.

Organized into three categories:

#### Axioms (fundamental truths)

1. Every architecture can be represented as a graph.
2. Every architecture possesses a state vector.
3. Architectural changes produce observable changes in state.
4. Entropy is cumulative (E(t) ≥ 0).
5. Half-Life is not prediction — it's an operational indicator.
6. CRI is a composite metric, not a physical measurement.
7. Observations are approximations — the State Vector is a model of architecture, not architecture itself.
8. Architecture has epistemic limits — Pyscope can explain structure, not business outcomes.

#### Principles (guiding rules)

1. Entropy is cumulative (E(t) ≥ 0).
2. Half-Life is not prediction — it's an operational indicator.
3. CRI is a composite metric, not a physical measurement.

#### Operational Definitions (measurable concepts)

1. ACP measures structural pressure (not error).
2. Boundary Leakage measures operational violations.
3. Dynamics require temporal data.

No implementation may violate an axiom.

If code conflicts with an axiom:

**AXIOM WINS.**

---

### Layer 2 — Phenomena

Observable architectural phenomena:

- Architectural Entropy
- Structural Pressure
- Structural Cohesion
- Operational Leakage
- Architectural Integrity
- Governance Compliance
- Architectural Reachability

Metrics must map to phenomena.

If a metric has no phenomenon:

**REJECT IT.**

---

### Layer 3 — Causal Factors

Explains WHY phenomena occur.

Examples:

- New module added
- Circular dependency introduced
- Incomplete refactoring
- Cross-domain coupling increased

Without causality, you have observability.

With causality, you have explainability.

---

### Layer 4 — State Vector

Canonical representation:

```python
S(t) = {
    entropy: EntropyDynamics,
    acp: float,
    dci: float,
    boundary_leakage: float,
    cri: float,
    agp: float,
    context_radius: int,
    dependency_density: float
}
```

All measurements must ultimately become dimensions of S(t).

If a measurement cannot be represented in S(t):

**REJECT IT.**

---

### Layer 5 — Dynamics

Represents state evolution.

Examples:

- velocity
- acceleration
- drift
- regression
- half-life

Rules:

- Dynamics require temporal data.
- Instantaneous metrics must never be classified as dynamics.

---

### Layer 6 — Metrics

Metrics quantify state.

Each metric must define:

- Phenomenon measured
- Units
- Bounds
- Invariants
- Formula
- Interpretation

Metrics without units are invalid.
Metrics without invariants are invalid.
Metrics without interpretation are invalid.

---

### Layer 7 — Governance

Produces decisions.

Allowed outputs:

- ALLOW
- WARN
- BLOCK

Governance consumes:

- Current State
- Future State
- Dynamics

Governance never consumes raw implementation details directly.

---

### Layer 8 — Memory

Transforms state into retrievable knowledge.

Concepts:

- State History: temporal sequence of states
- Similarity: comparison between states
- Recall: retrieval of relevant past states

Memory is a concept, not an implementation.

The mechanism (sqlite-vec, FAISS, pgvector) is an implementation detail.

---

### Layer 9 — Applicability

Defines the epistemic limits of the model.

What AGS can explain:

- Structural coupling
- Boundary violations
- Architectural drift
- Entropy evolution
- Governance compliance

What AGS cannot explain:

- Business success
- Developer productivity
- Team satisfaction
- Product-market fit
- Revenue

All architectural observations are estimations derived from source code artifacts.

Observation error must be documented for every metric.

---

### Layer 10 — Calibration

Validates and tunes the model.

Responsibilities:

- Synthetic validation (Verification)
- Real project observation
- Literature correlation
- Threshold tuning
- Weight tuning

ACP=90 means nothing without calibration.

---

### Layer 11 — Implementation

Executable realization of the model.

Code is the last step.

The model is the product.

The implementation is just one realization of the model.

---

## Scientific Validation Protocol

Every proposal MUST answer all 10 questions:

1. **Ontology**: Which ontology entities are affected?
2. **Theory**: Which axioms are involved?
3. **Phenomena**: Which phenomena are affected?
4. **Causal Factors**: Which causal factors explain the change?
5. **State Vector**: Which state dimensions are affected?
6. **Metrics**: Which metrics are affected?
7. **Invariants**: Which invariants must remain true?
8. **Governance**: What governance behavior changes?
9. **Memory**: What memory representation changes?
10. **Applicability**: What is the domain of applicability and observation uncertainty?

If any question cannot be answered:

**REJECT THE CHANGE.**

---

## Metric Validation Protocol

For every new metric provide:

```
Name:
Phenomenon:
Units:
Bounds:
Formula:
Interpretation:
Invariant:
State Dimension:
```

If any field is missing:

**REJECT THE METRIC.**

---

## Implementation Validation Protocol

Before accepting code:

1. Validate Ontology
2. Validate Theory
3. Validate Phenomena
4. Validate Causal Factors
5. Validate State Vector
6. Validate Dynamics
7. Validate Metrics
8. Validate Governance
9. Validate Memory
10. Validate Applicability
11. Validate Calibration

Only then validate implementation.

Never start from code.

Always start from FASM.

---

## Response Format

For every architectural proposal return:

```markdown
## FASM Analysis

### Ontology
...

### Theory
...

### Phenomena
...

### Causal Factors
...

### State Vector
...

### Dynamics
...

### Metrics
...

### Governance
...

### Memory
...

### Applicability
...

### Verdict
APPROVED or REJECTED
with justification.
```

The FASM is the source of truth.

The model is primary.

The implementation is secondary.
