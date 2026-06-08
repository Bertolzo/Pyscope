# FASM Baseline v2.0

**Version:** 2.0.0
**Date frozen:** 2026-06-04
**Statement:** FASM v2.0 Frozen Baseline — Pre-Pyscope Observation State
**Previous version:** v1.0.0 (frozen 2026-06-04)
**Bump type:** MAJOR (phenomenon reframe)


## Status

This is the **first formally frozen version** of the FASM baseline.
The synthetic experimental apparatus (ADO/Pyscope) has passed C0
verification (CIR-1, CIR-2, CIR-3, CIR-4A). The system is approved
 to enter Pyscope: real project observation.

Any modification to the frozen documents, the experimental apparatus,
or the CIR baselines requires an explicit version bump and is governed
by `tools/verify_baseline.py`.

---

## Section A: Scientific Model

11 documents, each pinned by SHA-256:

| File | SHA-256 |
|------|---------|
| `docs/ONTOLOGY.md` | `sha256:ee8adf95c4dfbb594ac130ac24ab746c86f74d3db3a3df3324cdfbcd887ac490` |
| `docs/THEORY.md` | `sha256:968b62e567ea1e4c0d0746a5adb310f3b715e8d7f9ef939e870f7d8ad722e0d4` |
| `docs/PHENOMENA.md` | `sha256:c057027598b957247f29dee09ec538bce7476a3e61b94d04790922b0b3d1a0e2` |
| `docs/STATE_VECTOR.md` | `sha256:b1852607f77a9777e7b0c21c3c7413dc10f3cda2dfc54bcf8686258306514f53` |
| `docs/METRICS.md` | `sha256:59d65c884496445c934f601c18a155248122c1cb2353c7d6d4fed28149ed7716` |
| `docs/FALSIFIABILITY.md` | `sha256:2e295ea4d45fe6d4e7136363295e5641aa5ae94b6610c1fefbdd2d1444311337` |
| `docs/LIMITATIONS.md` | `sha256:447d36ef09d7f2be7463c61246fe9ceebfd46920a552696674168e4ed17f864a` |
| `docs/MEASUREMENT_THEORY.md` | `sha256:1d6464442c1f22ca83623292985e25e82db2461bba39a18f569633d5ad3ed683` |
| `docs/CIR_INVARIANTS.md` | `sha256:175834d6c3dc3f222664c56d935159a364a8c7ac542ab412398e09e67a5fd9ae` |
| `docs/C0_RESULTS.md` | `sha256:84cff8a9e385c4b0be6296d953723589180cc0bc1ef492da9c54fbd0989945e5` |
| `docs/SCIENTIFIC_VALIDATION_PROTOCOL.md` | `sha256:9ecc7a34ed1e0200fd899ca40ebb08fffa638c7eeee2d02f119cf48b2dba4991` |

---

## Section B: Experimental Apparatus

9 source files, each pinned by SHA-256:

| File | SHA-256 |
|------|---------|
| `ags/synthetic/__init__.py` | `sha256:de157cc6df3f8359737589058826d230f9a730bd74a2e87712e6ab9a0b317a53` |
| `ags/synthetic/regimes.py` | `sha256:c1293e4877cf4aa51002c5f280c24b33e36591368b8031744b236daa5385da89` |
| `ags/synthetic/spec.py` | `sha256:0a9448ae53194e9cdb494f45ad674af987ff36906832e7f1728102f817c6a7ee` |
| `ags/synthetic/generator.py` | `sha256:6f2e12ec90c597724a5187dbc12df80dc5626e17c11fe616f25205f656357517` |
| `ags/synthetic/graph_set.py` | `sha256:238631269ebb12c681428f07ee0f9e578ba7e3ca8748caab9c24b61575a82b91` |
| `ags/synthetic/perturbation.py` | `sha256:7fbe6aa238ebdaa90ddd3580acc99a24381c6923958c9c53ffe50fe10405de95` |
| `ags/synthetic/coverage_audit.py` | `sha256:9f5337228198e9088ec668e17bfeaf9fd64c91a5096348a6dd96a8ce1376b377` |
| `ags/synthetic/orthogonality.py` | `sha256:aedc3fe3c1ab61177cc46a00ec7fa48dcf55748430ab5f86823e6c3458622764` |
| `tests/test_synthetic_c00.py` | `sha256:dde88006daae8d1160439a51c93befa6322000a0b4334b4927a6d4b35570c286` |

---

## Section C: CIR Numerical Baselines

| CIR | Metric | Baseline | Threshold | Status |
|-----|--------|----------|-----------|--------|
| CIR-1 | min_identifiability | 0.90 | ≥ 0.80 | ✓ PASS |
| CIR-2a | min_stability | 0.80 | ≥ 0.80 | ✓ PASS |
| CIR-2b | min_separation | 1.01 | > 1.00 | ✓ PASS |
| CIR-2c | min_continuity | 0.50 | ≥ 0.50 | ✓ PASS |
| CIR-3 | edge_count_range | 580x | ≥ 10x | ✓ PASS |
| CIR-3 | density_spread | 0.252 | ≥ 0.10 | ✓ PASS |
| CIR-3 | topology_diversity | 3 | ≥ 3 | ✓ PASS |
| CIR-4A | max_pearson | 0.71 | < 0.80 | ✓ PASS |
| CIR-4B | max_dominance | 0.94 | (documented) | ⚠ KNOWN |
| — | effective_rank | 2.65 | ≥ 3.0 | ⚠ PARTIAL |

**Notes:**

- CIR-4B is **documented as a known finding** in `LIMITATIONS.md` (L17)
  and `AUDIT.md`. The system is effectively 2-3 dimensional, not 4.
- `effective_rank = 2.65` is below the `≥ 3.0` aspirational target.
  The system is genuine 2-3D, not 4D.

---

## Semver Policy

ADO uses **Semantic Versioning** for its baseline:

| Bump | Trigger | Example |
|------|---------|---------|
| PATCH (`v1.0.0` → `v1.0.1`) | whitespace, typo, formatting | doc reformatted |
| MINOR (`v1.0.0` → `v1.1.0`) | new metric, new CIR, new invariant | add Half-Life |
| MAJOR (`v1.0.0` → `v2.0.0`) | axiom changed, phenomenon redefined, ontology altered | new entity |

**Bump type heuristics** (used by `verify_baseline.py --suggest-bump`):

| File changed | Suggested bump |
|--------------|----------------|
| `ONTOLOGY.md`, `THEORY.md`, `PHENOMENA.md` | MAJOR |
| `METRICS.md`, `STATE_VECTOR.md`, `MEASUREMENT_THEORY.md` | MINOR |
| `FALSIFIABILITY.md`, `LIMITATIONS.md` | MINOR |
| `CIR_INVARIANTS.md`, `C0_RESULTS.md` | MINOR |
| `ags/synthetic/*` | MINOR |
| `tests/*` | PATCH |
| whitespace only | PATCH |

---

## Verification

To verify this baseline against the current state of the repository:

```bash
python tools/verify_baseline.py
```

Options:

```bash
# Verify only one section
python tools/verify_baseline.py --section=scientific
python tools/verify_baseline.py --section=apparatus
python tools/verify_baseline.py --section=cirs

# Update baseline (after explicit version bump decision)
python tools/verify_baseline.py --update --confirm

# Suggest bump type
python tools/verify_baseline.py --suggest-bump

# Ignore whitespace changes (PATCH-level)
python tools/verify_baseline.py --ignore-whitespace

# JSON output (for CI)
python tools/verify_baseline.py --json
```

**Exit codes:**

| Code | Meaning |
|------|---------|
| 0 | Baseline OK |
| 1 | Document or code diverged |
| 2 | CIR below baseline |
| 3 | Hashed file missing |
| 4 | Baseline file not found |

---

## Conflict Resolution

If a CIR value improves but a hashed document changed:

1. **Baseline has priority.** Bump version first.
2. Run `verify_baseline.py --suggest-bump` to identify correct bump type.
3. Update baseline with `verify_baseline.py --update --confirm`.
4. Document the change in `AUDIT.md` (the evolutive artifact).

---

## What This Baseline Does Not Cover

- **Real-project validity** (C1) — out of scope
- **Literature correlation** (C2) — out of scope
- **Predictive power** — out of FASM scope (L1)
- **Cross-language validity** — out of FASM scope (L6)
- **Runtime behavior** — out of FASM scope (L3)

These are explicitly excluded by `LIMITATIONS.md`.

---

## Declaration

> **FASM v2.0 Frozen Baseline — Pre-C1 Observation State**
>
> This is the second formally frozen version of the FASM/ADO baseline.
> The synthetic experimental apparatus has passed C0 verification
> (CIR-1, CIR-2, CIR-3, CIR-4A). The system is approved to enter C1:
> real project observation.
>
> **v2.0 changes from v1.0:**
> - PHENOMENA.md: Reframed from 8 phenomena to 8 phenomena with explicit
>   observable aspects hierarchy. Architectural Integrity reframe as
>   Architectural Health. Coupling Intensity and Rate of Change demoted
>   to observable aspects (not independent phenomena).
> - STATE_VECTOR.md: Replaced Python code blocks with mathematical notation
>   (formatação).
> - METRICS.md: Added Dependency Density and Graph Drift as explicit
>   metrics. Each metric now has Phenomenon + Observable Aspect mapping.
>   CRI limitation (CIR-4B) documented explicitly.
> - MEASUREMENT_THEORY.md: Restructured to match new PHENOMENA hierarchy.
>   Removed AGS source file references.
> - CIR_INVARIANTS.md: Removed AGS source file references.
> - SCIENTIFIC_VALIDATION_PROTOCOL.md: Added Axioma 8 to Q2 axioms list
>   (was missing, present in THEORY.md).
>
> Any modification to the frozen documents, the experimental
> apparatus, or the CIR baselines requires an explicit version bump
> and is governed by `tools/verify_baseline.py`.
