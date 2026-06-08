# Pyscope Theory

**Layer**: 1
**Purpose**: Define architectural truths

---

## Axioms

Fundamental truths that cannot be violated.

### Axioma 1 — Architecture is graphable

Every architecture can be represented as a directed graph.

```
Architecture → Graph
```

**Status**: Fundamental axiom
**Justification**: All software systems have components and dependencies.

---

### Axioma 2 — Architecture has state

Every architecture possesses a state vector S(t) at time t.

```
Architecture → State Vector
```

**Status**: Fundamental axiom
**Justification**: Architecture can be characterized by measurable properties.

---

### Axioma 3 — Architecture changes

Architectural changes produce observable changes in state.

```
Change → State Delta
```

**Status**: Fundamental axiom
**Justification**: Software evolves over time.

---

### Axioma 7 — Observations are approximations

All architectural observations are estimations derived from source code artifacts.

The State Vector is a model of architecture, not architecture itself.

```
Architecture → Observation → State Vector (approximate)
```

**Status**: Fundamental axiom
**Justification**: AST parsing, import extraction, community detection, and graph inference each introduce observation error.

---

### Axioma 8 — Architecture has epistemic limits

O modelo Pyscope pode explicar fenômenos estruturais e dinâmicos.

O modelo Pyscope não pode explicar resultados de negócio, produtividade de times ou satisfação de equipe.

```
Pyscope can explain: structure, coupling, drift, entropy, governance
Pyscope cannot explain: revenue, velocity, morale, product-market fit
```

**Status**: Fundamental axiom
**Justification**: Scientific models must declare their domain of applicability.

---

## Principles

Guiding rules that shape the model.

### Principle 1 — Entropy is cumulative

E(t) ≥ 0 for all t. Entropy is never negative.

**Status**: Principle
**Justification**: Architectural debt accumulates; it doesn't disappear spontaneously.

---

### Principle 2 — Half-Life is not prediction

Half-Life is an operational indicator.

PredictionEngine is who predicts.

**Status**: Principle
**Justification**: Half-Life uses linear extrapolation; prediction uses Taylor expansion.

---

### Principle 3 — CRI is composite

CRI = f(entropy, acp, dci, agp, layer_purity, coverage)

CRI is not a physical measurement.

**Status**: Principle
**Justification**: CRI combines multiple phenomena into a single score.

---

### Principle 4 — Metrics are projections

All Pyscope metrics are projections or transformations of S(t).

**Status**: Principle
**Justification**: The State Vector is the canonical representation.

---

## Operational Definitions

Measurable concepts that can change as understanding evolves.

### Definition 1 — ACP measures structural pressure

ACP ≠ Boundary Leakage.

ACP measures "how many structural relationships cross boundaries," regardless of correctness.

**Status**: Operational definition
**May change**: Yes — if better understanding emerges.

---

### Definition 2 — Boundary Leakage measures operational violations

A architecture can have low ACP and high Leakage.

Example: few dependencies, but all wrong.

**Status**: Operational definition
**May change**: Yes — if better understanding emerges.

---

### Definition 3 — Dynamics require temporal data

Instantaneous metrics must never be classified as dynamics.

**Status**: Operational definition
**May change**: No — this is definitional.

---

## Two-Dimensional Coupling Model

| ACP | Leakage | Interpretation |
|-----|---------|----------------|
| High | Low | Complex but healthy |
| Low | High | Architecture of PowerPoint |
| High | High | Collapse zone |
| Low | Low | Clean and simple |

---

## Relationships to Other Layers

```
Theory
    ├── constrains → Phenomena
    ├── validates → State Vector
    ├── guides → Metrics
    └── informs → Governance
```

---

## Rules

1. No implementation may violate an axiom.
2. If code conflicts with an axiom, AXIOM WINS.
3. Principles may be refined but not violated.
4. Operational definitions may change as understanding evolves.
