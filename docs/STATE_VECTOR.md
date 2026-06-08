# Architectural State Vector

**Layer**: 3
**Purpose**: Define how observations are represented

---

## Definition

The Architectural State Vector is the minimal representation of an architecture at time t.

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

---

## Nested Structure

### EntropyDynamics

```python
entropy: {
    current: float,        # points
    velocity: float,       # points/day
    acceleration: float,   # points/day²
    polyfit_a: float,
    polyfit_b: float,
    polyfit_c: float
}
```

---

## Dimensions

| Path | Phenomenon | Unit | Bounds |
|------|------------|------|--------|
| entropy.current | Architectural Entropy | points | [0, ∞) |
| entropy.velocity | Rate of Entropy Change | points/day | (-∞, ∞) |
| entropy.acceleration | Acceleration of Entropy | points/day² | (-∞, ∞) |
| acp | Structural Pressure | % | [0, 100] |
| dci | Structural Cohesion | % | [0, 100] |
| boundary_leakage | Operational Leakage | ratio | [0, 1] |
| cri | Architectural Integrity | score | [0, 100] |
| agp | Governance Compliance | % | [0, 100] |
| context_radius | Architectural Reachability | files | [0, ∞) |
| dependency_density | Coupling Intensity | ratio | [0, 1] |

---

## Embedding

The State Vector can be converted to a numerical vector for memory operations.

```
embedding(S(t)) = [
    entropy.current,
    entropy.velocity,
    entropy.acceleration,
    acp,
    dci,
    boundary_leakage,
    cri,
    agp,
    context_radius,
    dependency_density,
]
```

**Dimension**: 10

---

## Invariants

| Component | Constraint | Violation |
|-----------|------------|-----------|
| entropy.current | ≥ 0 | Negative entropy (impossible) |
| acp | [0, 100] | Out of range |
| dci | [0, 100] | Out of range |
| boundary_leakage | [0, 1] | Out of range |
| cri | [0, 100] | Out of range |
| agp | [0, 100] | Out of range |
| context_radius | ≥ 0 | Negative radius (impossible) |
| dependency_density | [0, 1] | Out of range |

---

## Interpretation

The State Vector is the canonical representation of architectural state.

All FASM metrics are projections of this vector.

All Governance decisions consume this vector.

All Memory operations store this vector.

---

## Rules

1. All measurements must ultimately become dimensions of S(t).
2. If a measurement cannot be represented in S(t), REJECT IT.
3. The State Vector cannot be redefined by lower layers.
4. The State Vector is the single source of truth for architectural state.
