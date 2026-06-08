# Causal Integrity Rules (CIR) — Formal Specification

## Purpose

The C0.0 experimental system must satisfy three causal integrity rules
that distinguish a real experimental apparatus from a self-confirming
generator. These rules ensure that:

1. The model is identifiable in observation space
2. The regimes are causally stable (attractors, not artifacts)
3. The sampled space covers real architectural topologies

## The Three CIR

### CIR-1: Identifiability (already achieved)

**Statement:** P(R_obs | R_spec) is sharply peaked for all regimes.

**Operational form:**
```
For each regime R in REGIME_TAXONOMY:
    For N=20 seeds:
        Generate G from R_spec
        Classify G -> R_obs
        Count matches where R_obs == R_spec
    Identifiability(R) = matches / N
    Pass if Identifiability(R) >= 0.80 for all R
```

**Current results:** Mean 99%, min 90% (COUPLED).

**Why this matters:** Without CIR-1, the regime labels are arbitrary
and the model cannot be used to classify real architectures.

---

### CIR-2: Perturbation Stability (newly added)

**Statement:** Regimes are attractors in parameter space. Small
perturbations stay within the regime basin; large perturbations
transition to neighboring regimes (not random ones).

**Three sub-tests:**

#### CIR-2a: Within-Regime Stability

```
For each regime R, N=10 seeds:
    Generate G from R_spec
    Classify G -> R_obs
    Stability(R) = count(R_obs == R) / N
    Pass if Stability(R) >= 0.80 for all R
```

**Current results:** All 11 regimes at ≥80% stability.

#### CIR-2b: Cross-Regime Separation

```
For each regime R:
    Within-dist(R) = avg structural distance between R-graphs
    Between-dist(R) = avg structural distance to graphs of other regimes
    Separation(R) = Between-dist(R) / Within-dist(R)
    Pass if Separation(R) > 1.0 for all R
```

**Current results:** All 11 regimes with separation > 1.0 (range 1.01-2.17).

#### CIR-2c: Spec Continuity

```
For each regime R:
    Sample midpoint M of R's parameter range
    Perturb M by +/- 25% of range width
    Continuity(R) = count(classify(perturbed) ∈ {R, neighbors(R)}) / N
    Pass if Continuity(R) >= 0.50 for all R
```

**Note:** Uses relative epsilon (25% of range width) to handle regimes
with different range magnitudes uniformly.

**Current results:** All 11 regimes at 50-100% continuity.

**Why this matters:** Without CIR-2, regime boundaries are arbitrary
thresholds. Real systems have gradients, not step functions.

---

### CIR-3: Graph Space Coverage (newly added)

**Statement:** C0.0 samples a non-degenerate region of the graph manifold.
The sampled space covers the structural diversity of real architectures.

**Operational form:**

```
For N_graphs = 11 regimes * 5 seeds:
    Compute statistics: edge_count, density, degree_variance, diameter
    Compute topology class: DAG, MESH, MODULAR, HUB, etc.

    Pass if:
        - edge_count range >= 10x
        - edge_count CV >= 0.5
        - density spread >= 0.1
        - degree_variance CV >= 0.5
        - diameter spread >= 2
        - at least 3 distinct topology classes
        - no single class dominates > 70%
```

**Current results:**
- edge_count_range: 580x (✓)
- edge_count_cv: 1.52 (✓)
- density_spread: 0.252 (✓)
- degree_variance_cv: 1.66 (✓)
- diameter_spread: 5 (✓)
- topology_diversity: 3 classes (DAG, MODULAR, GENERAL) (✓)
- topology_balance: 60.6% (✓, < 70%)

**Why this matters:** Without CIR-3, C0.0 could sample only a restricted
topology class (e.g., only DAGs) and miss real architectural phenomena.

---

## What CIR-1/2/3 Together Guarantee

If all three pass, the C0.0 system provides:

1. **Identifiability**: The classifier can tell regimes apart
2. **Stability**: Regimes are meaningful (not threshold artifacts)
3. **Coverage**: The sampled space is non-degenerate

Together: the regimes correspond to **distinct, stable, causally-grounded
attractors in a representative region of graph space**.

## What CIR-1/2/3 Do NOT Guarantee

- **External validity**: The regimes may not match real architectures
  → This is the role of C1 (real project observation)
- **Exhaustiveness**: There may be regimes we haven't discovered
  → This is the role of C2 (literature correlation)
- **Predictive power**: The model may not predict future state
  → This is the role of C2 (time-series correlation)

## FASM Validation

CIR-1, CIR-2, CIR-3 satisfy the L5 (Invariants) layer of FASM.

They are the **operational expressions** of FASM Invariant:
> "Real systems have stable attractors in phase space"

## Source Code

The CIR tests are implemented in the synthetic experimental apparatus (Section B of the baseline). See:
- Regime taxonomy — RegimeName, REGIME_TAXONOMY
- CIR-2 tests — Perturbation module (within-regime stability, cross-regime separation, spec continuity)
- CIR-3 tests — Coverage audit (graph statistics, topology diversity)
- Test suite — C0.0 verification tests

These are apparatus-level details. The FASM model specifies only the operational conditions above.
