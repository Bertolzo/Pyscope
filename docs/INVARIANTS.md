# Architectural Invariants

**Layer**: 5 (Metrics)
**Purpose**: Universal constraints that must hold true for all architectural states

---

## Invariant Catalog

### Entropy

| Invariant | Constraint | Violation |
|-----------|------------|-----------|
| E1 | entropy.current >= 0 | Negative entropy (impossible) |
| E2 | entropy.velocity is real | Any float is valid |
| E3 | entropy.acceleration is real | Any float is valid |

---

### ACP (Structural Coupling Pressure)

| Invariant | Constraint | Violation |
|-----------|------------|-----------|
| A1 | acp >= 0 | Negative pressure (impossible) |
| A2 | acp <= 100 | Over 100% pressure (impossible) |
| A3 | 0 <= acp <= 100 | Invalid range |

---

### DCI (Structural Cohesion)

| Invariant | Constraint | Violation |
|-----------|------------|-----------|
| D1 | dci >= 0 | Negative cohesion (impossible) |
| D2 | dci <= 100 | Over 100% cohesion (impossible) |
| D3 | 0 <= dci <= 100 | Invalid range |

---

### Boundary Leakage

| Invariant | Constraint | Violation |
|-----------|------------|-----------|
| B1 | boundary_leakage >= 0 | Negative leakage (impossible) |
| B2 | boundary_leakage <= 1 | Over 100% leakage (impossible) |
| B3 | 0 <= leakage <= 1 | Invalid range |

---

### CRI (Architectural Integrity)

| Invariant | Constraint | Violation |
|-----------|------------|-----------|
| C1 | cri >= 0 | Negative integrity (impossible) |
| C2 | cri <= 100 | Over 100% integrity (impossible) |
| C3 | 0 <= cri <= 100 | Invalid range |

---

### AGP (Governance Compliance)

| Invariant | Constraint | Violation |
|-----------|------------|-----------|
| G1 | agp >= 0 | Negative compliance (impossible) |
| G2 | agp <= 100 | Over 100% compliance (impossible) |
| G3 | 0 <= agp <= 100 | Invalid range |

---

### Context Radius

| Invariant | Constraint | Violation |
|-----------|------------|-----------|
| R1 | context_radius >= 0 | Negative radius (impossible) |
| R2 | context_radius == 0 for depth=0 | Source node excluded |

---

### Dependency Density

| Invariant | Constraint | Violation |
|-----------|------------|-----------|
| Dd1 | dependency_density >= 0 | Negative density (impossible) |
| Dd2 | dependency_density <= 1 | Over 100% density (impossible) |
| Dd3 | 0 <= dd <= 1 | Invalid range |

---

### Half-Life

| Invariant | Constraint | Violation |
|-----------|------------|-----------|
| H1 | half_life_months > 0 | Negative time (impossible) |
| H2 | half_life_months == inf for velocity <= 0 | Recovery mode |

---

### State Vector

| Invariant | Constraint | Violation |
|-----------|------------|-----------|
| S1 | embedding.dimension == 10 | Invalid embedding |

---

## Enforcement

Invariants are enforced at two levels:

1. **Model validation**: Field constraints on state vector components
2. **Automated verification**: Continuous validation of all invariant constraints

---

## Rules

1. Every metric must have at least one invariant.
2. Invariants cannot be relaxed for specific cases.
3. If an invariant is violated, the model is in an invalid state.
4. New invariants must be added to both this document and the test suite.

---

## Observation & Classification Invariants

These invariants are checked by the C1 observation pipeline and the
classification tests. They ensure that snapshots, parsers and the taxonomy
remain within the expected scope used by the research protocol.

| Invariant | Constraint | Test / Enforcement |
|-----------|------------|--------------------|
| O1 | `total_imports_attempted` is present and >= 0 | `compute_observation_snapshot` requires this field; stored in JSON outputs |
| O2 | `observation_quality` in [0,1] and equals observed_edges / total_imports_attempted when imports attempted > 0 | Verified by `tests/test_observation.py` |
| O3 | `snapshot` contains fields: `total_nodes`, `total_edges`, `cross_domain_edges`, `intra_domain_edges`, `unknown_dynamic_edges`, `total_imports_attempted`, `observation_quality` | Required by `tools/c1_observe.py` and `tests/*` |
| O4 | `REGIME_TAXONOMY` length == 11 (canonical baseline) | `tests/test_synthetic_c00.py::TestRegimeTaxonomy::test_taxonomy_has_11_regimes` |
| O5 | `classify_from_snapshot(...).all_distances` length == len(REGIME_TAXONOMY) | `tests/test_classification.py` asserts one distance per regime |
| O6 | `classification` outputs `regime`, `nearest_regime`, `second_nearest_regime`, `distance_1`, `distance_2`, `structural_distance_1`, `margin`, `confidence` | Used by report generators and JSON exports |
| O7 | Parser provides `parser_version` and `graph_builder_version` in snapshot | Exported to C1 JSONs for traceability |
| O8 | Streaming mode (`GraphBuilder(config={"streaming": True})`) must produce equivalent `snapshot` fields (possibly with fewer resolved edges) and must not OOM on very large repos | Exercised manually in `tools/c1_observe.py` and by large-repo runs |
| O9 | Dynamic import calls (`__import__`, `importlib.import_module`) are counted toward `total_imports_attempted` even if unresolved | Allows observation_quality to reflect parser uncertainty |

Notes:
- The canonical taxonomy (O4) is a design decision for C1.0; expanding the taxonomy is part of C2.0 and must be accompanied by baseline updates and falsifiability tests.
- `observation_quality` intentionally penalizes sub-observation; when `total_imports_attempted` is large and resolved edges are few (Airflow), quality will be near zero.
- Tests depend on invariants O1–O6. Changing them requires updating tests and the `docs/FASM_BASELINE_v1.md` baseline.
