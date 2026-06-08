# ADO — Architectural Dynamics Observatory

**Version:** 1.0.0
**Status:** Frozen Baseline
**Frozen at:** 2026-06-04

---

## What is ADO?

**ADO (Architectural Dynamics Observatory)** is a falsifiable observational
model for software architecture dynamics.

It is:

- An **observatory** — it observes state and evolution
- **Architectural** — focused on software structure
- **Dynamics** — focused on how structure changes over time
- **Formal** — based on explicit axioms, phenomena, and metrics

ADO is **not**:

- A static analyzer
- A metric framework
- A refactoring tool
- A code quality linter

---

## The Five Layers of the Observatory

```
Code (Python project)
   ↓
Observation (ArchitecturalGraph)
   ↓
State Vector (S(t))
   ↓
Hypotheses (Causal Integrity Rules)
   ↓
Falsification (F1-F4 conditions)
```

Each layer transforms input into output through an explicit, testable
procedure. The transformations are documented in
`docs/MEASUREMENT_THEORY.md`.

---

## Relationship to FASM

FASM is the **formal model** that ADO is built upon:

- **FASM** = the mathematical/computational model (ontology, theory,
  phenomena, state vector, dynamics, metrics, invariants)
- **ADO** = the observatory that implements FASM as a falsifiable
  observation system
- **AGS** = the software implementation of ADO

```
FASM (formalism)
   ↓
ADO (observatory)
   ↓
AGS (implementation)
```

When this document says "ADO observes X", it means:
the formal model FASM defines X, ADO operationalizes it, Pyscope computes it.

---

## Current Status: Pre-Pyscope Observation Frozen Baseline

ADO v1.0 is **frozen**. C0 (Calibration) is complete:

| Milestone | Status |
|-----------|--------|
| C0.0: Synthetic regimes | ✓ Complete |
| C0.5: Internal scientific audit | ✓ Complete |
| CIR-1: Identifiability | ✓ PASS (min 90%) |
| CIR-2: Perturbation stability | ✓ PASS (a, b, c) |
| CIR-3: Graph space coverage | ✓ PASS (7 metrics) |
| CIR-4A: Primitive orthogonality | ✓ PASS (max \|corr\|=0.71) |
| CIR-4B: Composite dominance | ⚠ Documented (effective 2-3D) |

**Next stage:** Pyscope — Observation of real projects (Django, FastAPI,
Celery, Airflow, Requests). This is where the model transitions from
synthetic self-consistency to external validity.

---

## Frozen Documents

The following 11 documents constitute the **Scientific Model** baseline
and are immutable until the next version bump:

- `ONTOLOGY.md` — entities (L0)
- `THEORY.md` — axioms (L1)
- `PHENOMENA.md` — phenomena + causal factors (L2)
- `STATE_VECTOR.md` — formal state definition (L3)
- `METRICS.md` — 11 metrics (L5)
- `FALSIFIABILITY.md` — F1-F4 conditions
- `LIMITATIONS.md` — 17 documented limitations
- `MEASUREMENT_THEORY.md` — phenomenon → metric chain
- `CIR_INVARIANTS.md` — formal CIR specifications
- `C0_RESULTS.md` — C0 verification report
- `SCIENTIFIC_VALIDATION_PROTOCOL.md` — 10-question checklist

See `docs/FASM_BASELINE_v1.md` for hashes and CIR numerical baselines.

---

## Naming Hierarchy

| Term | Meaning |
|------|---------|
| **ADO** | Architectural Dynamics Observatory (this observatory) |
| **FASM** | Formal Architectural State Model (the formal model) |
| **Pyscope** | Architectural Governance System (the implementation) |
| **Architectural Digital Twin** | The observed entity (state + evolution + prediction) |

**Use:**

- "ADO observes X" when referring to the observatory
- "FASM defines X" when referring to the formal model
- "AGS computes X" when referring to the implementation

---

## What ADO Claims

When all CIRs pass and F1-F4 are satisfied, ADO is a **valid
observational system** for Python software architecture within the
scope defined by `LIMITATIONS.md`.

ADO does **not** claim (see LIMITATIONS.md for full list):

- Predictive power over future state
- Causal mechanisms for observed patterns
- Normative valuation of regimes
- Cross-language validity
- Runtime behavior modeling

These are explicitly excluded.

---

## Entry Point

For new readers:

1. Read this document (5 min)
2. Read `docs/FASM_BASELINE_v1.md` (10 min)
3. Read `docs/C0_RESULTS.md` (15 min)
4. Read `docs/LIMITATIONS.md` (10 min)
5. Read `docs/FALSIFIABILITY.md` (15 min)

For verification:

```bash
python tools/verify_baseline.py
```

For implementation details:

- `ags/synthetic/` — experimental apparatus
- `ags/core/` — graph extraction and analysis
- `ags/intelligence/` — evolution, prediction
- `ags/storage/` — persistence
- `ags/cli/` — command-line interface

---

## Versioning

ADO uses **Semantic Versioning** for its baseline:

| Bump | Trigger | Example |
|------|---------|---------|
| PATCH | whitespace, typo, formatting | v1.0.0 → v1.0.1 |
| MINOR | new metric, new CIR, new invariant | v1.0.0 → v1.1.0 |
| MAJOR | axiom changed, phenomenon redefined | v1.0.0 → v2.0.0 |

The baseline is verified by `tools/verify_baseline.py`. Any change
to a hashed document or CIR value requires an explicit version bump.

---

## Declaration

> **ADO v1.0 Frozen Baseline — Pre-Pyscope Observation State**
>
> This is the first formally frozen version of the Architectural
> Dynamics Observatory. The synthetic experimental apparatus has
> passed C0 verification (CIR-1, CIR-2, CIR-3, CIR-4A). The system
> is approved to enter C1: real project observation.
>
> Any modification to the frozen documents, the experimental
> apparatus, or the CIR baselines requires an explicit version bump
> and is governed by `tools/verify_baseline.py`.
