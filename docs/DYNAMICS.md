# Architectural Dynamics

**Layer**: 4
**Purpose**: Define how state changes over time

---

## Definition

Dynamics represents the evolution of state over time.

Dynamics answers: "Where is the system going?"

Not: "How is the system?"

---

## Components

### Velocity

**Definition**: Rate of change of a dimension.

**Formula**: dE/dt = 2a·t + b (for quadratic fit)

**Unit**: dimension/day

**Example**: entropy.velocity = 0.5 points/day

---

### Acceleration

**Definition**: Rate of rate of change.

**Formula**: d²E/dt² = 2a (for quadratic fit)

**Unit**: dimension/day²

**Example**: entropy.acceleration = 0.01 points/day²

---

### Drift

**Definition**: Structural divergence from baseline.

**Formula**: Jaccard Distance

**Unit**: ratio [0, 1]

**Example**: drift_ratio = 0.25 (25% divergence)

---

### Regression

**Definition**: Quality degradation between snapshots.

**Formula**: Comparison of state dimensions.

**Unit**: boolean + details

**Example**: regression_detected = True

---

### Half-Life

**Definition**: Time until operational collapse (linear extrapolation).

**Formula**: T½ = (E_target - E_current) / velocity

**Unit**: months

**Example**: half_life_months = 6.5

**Important**: Half-Life is NOT prediction. It's an operational indicator.

---

## Rules

1. Dynamics require temporal data.
2. Instantaneous metrics must never be classified as dynamics.
3. Dynamics cannot be redefined by lower layers.
4. Half-Life belongs to Dynamics, not Prediction.

---

## Relationships

```
State Vector (L3)
    ↓
Dynamics (L4)
    ↓
Prediction (uses Dynamics)
    ↓
Governance (uses Prediction)
```
