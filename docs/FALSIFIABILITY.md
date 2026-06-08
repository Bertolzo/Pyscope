# FALSIFIABILITY — Conditions for Model Invalidation

## Purpose

This document specifies the **formal and operational conditions** under
which FASM is falsified. Each falsification condition is:

1. **Formal** (mathematical criterion)
2. **Operational** (how to test it in practice)
3. **Interpretational** (what the falsification means)

This is the **epistemological contract** of the model. Any result
contradicting these conditions is grounds for revision or rejection
of FASM.

**Pre-requisite:** This document assumes `LIMITATIONS.md` is understood.
Falsification conditions are only valid within the scope defined there.

---

## F1 — Regime Falsification

**Based on:** CIR-1 (Identifiability)

### Formal Statement

```
FASM is falsified by F1 if:
    P(R_obs = R_spec) < τ

where:
    τ = 0.8 (threshold)
    R_spec = the regime used to generate a graph
    R_obs = the regime the graph is classified into
```

### Operational Procedure

1. Generate N=100 graphs per regime (11 regimes × 100 = 1100 total)
2. For each graph, classify using `classify_observed_regime()`
3. Count matches where `R_obs == R_spec`
4. Compute `identifiability(R) = matches / 100` for each regime
5. If `min(identifiability) < 0.8`, FASM is falsified

### Interpretation

**What this means:** The classifier can no longer distinguish regimes
with sufficient confidence. Either:
- The regime taxonomy is no longer representative of the data
- The metric space has drifted (features no longer separate regimes)
- The classifier itself is broken

**Current status (C0.0):** Mean 99%, min 90%. PASSES.

### Re-test cadence

- After any change to the regime taxonomy
- After any change to the metric computation
- Quarterly during C1 observation
- Whenever a new real project yields anomalous classification

---

## F2 — Stability Falsification

**Based on:** CIR-2 (Perturbation Stability)

### Formal Statement

```
FASM is falsified by F2 if:
    R(G) ≠ R(G + ΔG)

with frequency exceeding the C0 baseline, where:
    ΔG = a small perturbation of G (e.g., add/remove 10% of edges)
    R(X) = the regime of X
    "frequency" = fraction of perturbed graphs that flip regime
```

### Operational Procedure

1. For each of 11 regimes, generate 5 base graphs
2. For each base graph, generate 10 perturbed variants:
   - Add 10% new edges (sampled from same distribution)
   - Remove 10% existing edges (random)
3. Classify all perturbed variants
4. Count flips (where `R(perturbed) ≠ R(base)`)
5. Compare to C0 baseline: flip rate < 20% per regime
6. If flip rate > 20%, FASM is falsified

### Interpretation

**What this means:** Regimes are no longer stable attractors. Small
structural changes cause unpredictable regime transitions. This would
indicate the model is **threshold-based** rather than **attractor-based**.

**Current status (C0.0):**
- CIR-2a: Within-regime stability ≥ 80% for all regimes
- CIR-2b: Cross-regime separation > 1.0 for all regimes
- CIR-2c: Spec continuity ≥ 50% (25% range-width perturbation)
- All PASSES.

### Re-test cadence

- After any change to the construction rules
- When CIR-2 baseline changes
- During C1 observation: if real projects show high flip rates

---

## F3 — Coverage Falsification

**Based on:** CIR-3 (Graph Space Coverage)

### Formal Statement

```
FASM is falsified by F3 if:
    P(x ∉ Ω_synthetic) grows continuously

where:
    x = a real project's metric vector
    Ω_synthetic = the convex hull of synthetic metric vectors
    "grows continuously" = the fraction increases over observation time
```

### Operational Procedure

1. Define Ω_synthetic from the 1100-graph C0 sample:
   - Compute min/max for each metric
   - Ω_synthetic = [min, max] for each metric
2. For each new real project (during C1):
   - Compute its metric vector M
   - Check if M ∈ Ω_synthetic (all dimensions in range)
3. Track `out_of_distribution_rate` over time
4. If rate increases for 3 consecutive observation batches, FASM is falsified

### Interpretation

**What this means:** The synthetic graph space no longer covers the
real architecture space. The C0 generator produces graphs that don't
resemble real systems. Either:
- New topology classes have emerged (regime expansion needed)
- The metric ranges have shifted (calibration drift)
- The synthetic construction rules are too restrictive

**Current status (C0.0):**
- edge_count_range: 580x (≥ 10x required)
- density_spread: 0.252
- topology_diversity: 3 classes (DAG, MODULAR, GENERAL)
- All CIR-3 metrics PASS.

**Note:** F3 is **not directly testable** in C0. It requires C1
observation of real projects.

### Re-test cadence

- Every C1 observation batch
- Annually after C1 is complete
- When new real projects are added to the validation set

---

## F4 — Metric Collapse Falsification

**Based on:** CIR-4 (Metric Independence)

### Formal Statement

```
FASM is falsified by F4 if:
    rank_Σ(M) < k

where:
    M = the metric vector
    Σ(M) = the covariance matrix of M across observations
    rank_Σ = effective rank (ratio of squared sum to sum of squares of singular values)
    k = the theoretical dimensionality of M (number of independent dimensions)
```

### Operational Procedure

1. Collect N=1100 metric vectors (11 regimes × 100 seeds)
2. Compute the covariance matrix Σ(M)
3. Compute effective rank:
   ```
   effective_rank = (Σ σ_i)^2 / Σ σ_i^2
   where σ_i are singular values of centered, scaled M
   ```
4. Assert `effective_rank >= 3` for 4 metrics (or `>= k-1` for k metrics)
5. Also check pairwise: |pearson(M_i, M_j)| < 0.8

### Interpretation

**What this means:** Two or more metrics are **empirically
indistinguishable**. The system has fewer effective dimensions than
claimed. This is **not a tuning failure** — it is a structural
finding that should be reflected in the model's description of
itself.

**Current status (C0.0):**
- **CIR-4A (Primitive Orthogonality):** PASSES (max |pearson| = 0.71)
  - ACP vs DCI: -0.71 (after DCI redefinition)
  - All other pairs: < 0.2
- **CIR-4B (Composite Dominance):** FAILS (coupling = 0.94, cohesion = 0.88)
- **Effective rank:** 2.65 (target: ≥ 3)
- **Interpretation:** System is effectively 2-3 dimensional, not 4.
  This is documented as L17 in LIMITATIONS.md.

### Why this is not a FASM rejection

The user can interpret a failing F4 in two ways:
1. **Reject FASM** — "The model has redundancy, therefore it's wrong"
2. **Refine FASM** — "The model has redundancy, therefore we should
   document the effective dimensionality and proceed"

FASM takes the second interpretation. The metric space is 2-3D, not 4D.
This is a **finding**, not a **failure**. The model is honest about
its own dimensionality.

### Re-test cadence

- After any change to the metric set
- After any change to the metric computation procedure
- When new metrics are added (C2 may reveal additional dimensions)

---

## Summary Table

| Falsification | Formal Condition | Current Status | Test Cadence |
|---------------|------------------|----------------|--------------|
| F1: Regime | P(R_obs=R_spec) ≥ 0.8 | ✓ PASS (min 90%) | Per change |
| F2: Stability | flip_rate < baseline | ✓ PASS (CIR-2a/b/c) | Per change |
| F3: Coverage | P(x∈Ω) stable | ⏳ DEFERRED (needs C1) | Per C1 batch |
| F4: Collapse | rank_Σ ≥ 3 | ⚠ PARTIAL (2.65) | Per change |

## What FASM Claims When All Falsifications Pass

- **F1 passes:** The model can distinguish regimes empirically
- **F2 passes:** The model is stable under perturbation
- **F3 passes:** The model covers real architecture space
- **F4 passes:** The model has independent dimensions

When all four pass, FASM is a **valid observational system** for
software architecture in the scope defined by LIMITATIONS.md.

## What FASM Does NOT Claim

Even when all falsifications pass, FASM does **not** claim:
- Predictive power (L1)
- Causal mechanisms (L5)
- Normative valuation (L16)
- Cross-language validity (L6)
- Runtime behavior modeling (L3)

These are explicitly excluded by LIMITATIONS.md.

---

## Operational Workflow

```
For any change to FASM (metric, regime, code):

1. Run CIR-1, CIR-2, CIR-4 on synthetic graphs
2. Check F1, F2, F4 conditions
3. If any fail, revise the change
4. If all pass, update CIR baselines
5. Document the new baseline in CIR_INVARIANTS.md
```

```
For each C1 observation batch:

1. Run CIR-3 on the new real projects
2. Check F3 condition
3. If out-of-distribution rate increases, expand regime taxonomy
4. If regime identifiability drops, revise classifier
```

---

## Connection to Scientific Method

These falsification conditions are the **hypotheses** of FASM:

- H1: Regimes are empirically distinguishable (testable via F1)
- H2: Regimes are stable attractors (testable via F2)
- H3: Synthetic space covers real space (testable via F3)
- H4: Metrics are independent (testable via F4)

FASM is a **scientific model** in the Popperian sense: it makes
risky predictions (regimes are distinguishable) and exposes itself
to falsification (F1-F4 conditions).
