# MEASUREMENT THEORY — Phenomenon to State Dimension

## Purpose

This document formalizes the **measurement chain** that connects
abstract phenomena to concrete state vector dimensions. It bridges
PHENOMENA.md (what exists) with METRICS.md (how it's quantified) and
STATE_VECTOR.md (how it's represented).

The chain is:

```
Phenomenon
   ↓ (refines)
Observable Aspect
   ↓ (operationalizes)
Metric
   ↓ (projects to)
State Vector Dimension
```

This document is the **definitional contract** for each metric. When
disputes arise about what a metric means (especially during C2
literature correlation), this document is the reference.

---

## I. Architectural Entropy → entropy.*

### Phenomenon
**Architectural Entropy** — the cumulative "disorder" in the system,
integrated over time.

### Observable aspects
- magnitude (current accumulated inconsistencies)
- velocity (rate of entropy change, points/day)
- acceleration (second derivative, points/day²)

### Observable
Weighted sum of: boundary violations, god objects, cycles, AGP excess.

### Measurement Procedure
1. Count boundary violations, god objects, cycles, and AGP excess
2. Compute weighted sum: E = Σ(weight_i × count_i) for each type
3. Total is unbounded: E ∈ [0, ∞)

Weights are heuristic and calibrated during C1 observation.

Velocity and acceleration are derived from time-series data (not
available for single snapshots).

### Metric
**Entropy** — `0.0 ≤ E < ∞` (unbounded)
- 0: no disorder
- Higher: more disorder

### State Vector Dimension
`S(t).entropy: EntropyDynamics` (nested entity with current, velocity,
acceleration)

### Limitations
- The weights are heuristic
- Velocity and Acceleration are derived from time-series data

---

## II. Structural Pressure → S(t).acp, S(t).dependency_density

### Phenomenon
**Structural Pressure** — the amount and intensity of structural
interaction across architectural boundaries.

### Observable aspects
- inter-domain dependency ratio (ACP)
- coupling intensity (Dependency Density)

### Observable
**Cross-domain imports** — `import` statements in one domain that
reference symbols in another domain.

### Measurement Procedure (ACP)
1. Build the import graph `G = (V, E)` where V = files, E = imports
   - The parser treats `import a, b` as separate edges and resolves `from pkg import sub` to the imported submodule when possible.
   - Duplicate import edges are consolidated by the graph representation, so repeated syntax does not create repeated edges.
2. For each domain D_i, let `files(D_i)` = files in D_i
3. For each edge (u, v):
   - If `domain(u) ≠ domain(v)`, count as `cross_domain_edge`
4. Compute: `ACP = cross_domain_edges / total_edges`

### Measurement Procedure (Dependency Density)
1. Compute `n = |V|`, `e = |E|`
2. Compute: `density = e / (n * (n-1))`

### Metric
**ACP** — `0.0 ≤ ACP ≤ 1.0`
- 0.0: no cross-domain coupling (perfect isolation)
- 1.0: all edges are cross-domain (full coupling)

**DependencyDensity** — `0.0 ≤ density ≤ 1.0`
- 0.0: no edges (isolated nodes)
- 1.0: complete graph

### State Vector Dimension
`S(t).acp ∈ [0, 1]` and `S(t).dependency_density ∈ [0, 1]`

### Limitations
- Domain identification is heuristic (file path + module name)
- Circular imports count once
- Type imports vs runtime imports are not distinguished
- Maximum edges assumes directed graph (correct for imports)
- Does not account for self-loops

---

## III. Structural Cohesion → S(t).dci

### Phenomenon
**Structural Cohesion** — the degree to which the system's logical
boundaries (domains, modules) are respected by its actual structure.

### Observable aspects
- intra-module vs inter-module edge ratio

### Observable
**Cross-module file dependencies** — files in one module that import
files in another module.

### Measurement Procedure
1. Build the import graph `G = (V, E)`
2. For each file f, identify its module `M(f)` (from path)
3. For each edge (u, v):
   - If `M(u) ≠ M(v)`, count as `cross_module_edge`
4. Compute: `DCI = 1.0 - (cross_module_edges / total_edges)`

### Metric
**DCI (Design Cohesion Index)** — `0.0 ≤ DCI ≤ 1.0`
- 1.0: all imports stay within their module (perfect cohesion)
- 0.0: all imports cross modules (no cohesion)

### State Vector Dimension
`S(t).dci ∈ [0, 1]`

### Historical Note
DCI was previously defined as `1 - community_contamination`. This
was redefined in CIR-4 because Louvain community detection produced
the same communities as domain grouping, making DCI collinear with
ACP. The current definition uses cross-module ratio, which is
genuinely independent from cross-domain ratio.

### Limitations
- Module identification is heuristic (file path)
- "Module" is not formally defined; we use the first path component
- Does not distinguish between cyclic and acyclic cross-module imports

---

## IV. Operational Boundary Leakage → S(t).boundary_leakage

### Phenomenon
**Operational Boundary Leakage** — the violation of domain boundaries
at the file level, where files in the same module but different
domains import each other.

### Observable aspects
- file-level cross-domain imports

### Observable
**File-level boundary violations** — imports marked as
`is_boundary_violation=True` during graph construction.

### Measurement Procedure
1. Build the import graph `G = (V, E)` with edge attribute
   `is_boundary_violation: bool`
2. Count edges where `is_boundary_violation == True`
3. Compute: `Leakage = boundary_violations / total_edges`

### Metric
**Leakage** — `0.0 ≤ Leakage ≤ 1.0`
- 0.0: no file-level boundary violations
- 1.0: all edges are boundary violations (complete leakage)

### State Vector Dimension
`S(t).boundary_leakage` ∈ [0, 1]

### Limitations
- Only available when the graph was constructed with boundary awareness
- Real projects may not have this flag (extractor must set it)
- In the synthetic generator, this is the `file_level_leakage` parameter

---

## V. Architectural Drift → S(t).entropy.velocity, Half-Life

### Phenomenon
**Architectural Drift** — the difference between current architecture
and a reference state.

### Observable aspects
- magnitude (Graph Drift, Jaccard distance)
- velocity (Entropy Velocity)
- acceleration (Entropy Acceleration)

### Observable
**Graph differences** — set difference between current and previous
edge sets.

### Measurement Procedure (magnitude)
1. Compute `E_now` (current edge set) and `E_prev` (previous edge set)
2. Compute: `GD = 1 - |E_now ∩ E_prev| / |E_now ∪ E_prev|`

### Measurement Procedure (velocity)
See Section I (Entropy Velocity).

### Metric
**Graph Drift** — `0.0 ≤ GD ≤ 1.0`
- 0.0: identical graphs
- 1.0: no shared edges

**Half-Life** — months
- Linear extrapolation of entropy to 2× current value
- See METRICS.md for full definition

### State Vector Dimension
No canonical state dimension; derived from entropy sub-dynamics.

### Limitations
- Reference state must be defined (previous snapshot, baseline, declared design)
- Linear extrapolation is a simplification (see CIR-2 for stability)

---

## VI. Governance Compliance → S(t).agp

### Phenomenon
**Governance Compliance** — the degree of adherence to declared
architectural rules and constraints.

### Observable aspects
- domain count vs declared limit
- layer violation count

### Observable
Number of distinct domains detected in the project.

### Measurement Procedure
1. Identify domains from file paths or module names
2. Compute: `AGP = 100 - (domain_count - 1) * 15`
3. Clamp to [0, 100]

### Metric
**AGP** — `0 ≤ AGP ≤ 100`
- 100: 1 domain (no governance pressure)
- 0: 8+ domains (extreme pressure)

### State Vector Dimension
`S(t).agp ∈ [0, 100]`

### Limitations
- Domain detection is heuristic
- The 15-point penalty per domain is arbitrary

---

## VII. Architectural Reachability → S(t).context_radius

### Phenomenon
**Architectural Reachability** — the amount of the system affected by
a change in a specific component.

### Observable aspects
- transitive reach (BFS up to depth limit)

### Observable
BFS-reachable files from a given file, up to a depth limit.

### Measurement Procedure
1. For each file f, run BFS up to depth d (default 3)
2. Count unique reachable files
3. Compute: `context_radius(f) = |reachable| - 1`

### Metric
**ContextRadius** — `0 ≤ CR ≤ N-1` (N = total files)

### State Vector Dimension
`S(t).context_radius ∈ [0, N-1]`

### Limitations
- Depth limit is arbitrary
- Counts all reachable files, not just those that would actually
  need to change

---

## VIII. Architectural Health → S(t).cri

### Phenomenon
**Architectural Health** — the capacity of the architecture to
absorb changes without disproportionate degradation.

### Observable aspects
- composite response to change
- resilience under modification

### Observable
A weighted combination of multiple primitive metrics.

### Measurement Procedure (synthetic)
1. Compute primitive metrics: ACP, DCI, Leakage, CycleDensity
2. Apply weights:
   - w_coupling = 0.30
   - w_cohesion = 0.30
   - w_containment = 0.20
   - w_stability = 0.20
3. Compute: `CRI = 0.30*(1-ACP) + 0.30*DCI + 0.20*(1-Leakage) + 0.20*(1-CycleDensity)`

### Measurement Procedure (real)
Uses Radon for MI and Cyclomatic Complexity, plus heuristic estimates
for God Objects, Boundary Violations, Context Cost, Test Coverage,
and Type Coverage.

### Metric
**CRI** — `0.0 ≤ CRI ≤ 1.0` (synthetic) or `0.0 ≤ CRI ≤ 100` (real)
- Higher is better (less risk)
- The two scales are NOT directly comparable

### State Vector Dimension
`synthetic_cri ∈ [0, 1]` and `real_cri ∈ [0, 100]`

### Limitations
- CRI is a **weighted average**, not an independent phenomenon
- The weights are heuristic (not derived from data)
- CIR-4B (Composite Dominance) currently FAILS — CRI is dominated
  by coupling/cohesion (see LIMITATIONS.md L17)
- CRI is an *indicator* of health, not the definition of health.
  Health exists independently of CRI.

---

## IX. Cyclomatic Density → CycleDensity (synthetic only)

### Phenomenon
**Architectural Drift** (sub-aspect: structural cyclicity) — the
degree to which the dependency graph contains cycles.

### Observable
**Cycles in the import graph** — strongly connected components with
more than one node.

### Measurement Procedure
1. Build the import graph `G = (V, E)`
2. Compute `n_scc = number of strongly connected components`
3. Compute `n = number of nodes, e = number of edges`
4. Compute cyclomatic complexity: `C = e - n + n_scc`
5. Compute: `cycle_density = C / max(e, 1)`

### Metric
**CycleDensity** — `0.0 ≤ CycleDensity ≤ 1.0`
- 0.0: DAG (no cycles)
- 1.0: complete graph (all possible cycles)

### State Vector Dimension
Synthetic system only — not part of the canonical S(t).

### Limitations
- `n_scc` counts trivial SCCs (single nodes) as 1, so this is a
  lower bound on actual cyclomatic complexity
- Does not distinguish 2-cycles from longer cycles

---

## Summary: The Complete Measurement Chain

| Phenomenon | Observable Aspect | Metric | State Dim | CIR Status |
|------------|-------------------|--------|-----------|------------|
| Architectural Entropy | magnitude, velocity, acceleration | Entropy, Velocity, Acceleration | S(t).entropy.* | N/A |
| Structural Pressure | inter-domain ratio, coupling intensity | ACP, Dependency Density | S(t).acp, S(t).dependency_density | CIR-4A ✓ |
| Structural Cohesion | intra-module ratio | DCI | S(t).dci | CIR-4A ✓ |
| Boundary Leakage | file-level cross-domain imports | Leakage | S(t).boundary_leakage | CIR-4A ✓ |
| Architectural Drift | magnitude, velocity, acceleration | Graph Drift, Entropy Velocity, Half-Life | derived | N/A |
| Governance Compliance | domain count | AGP | S(t).agp | N/A |
| Architectural Reachability | transitive reach | ContextRadius | S(t).context_radius | N/A |
| Architectural Health | composite | CRI | S(t).cri | CIR-4B ✗ |

---

## What This Document Is

This is the **definitional contract** for FASM metrics. When in doubt:
- What is X measuring? → See the Observable section
- How is X computed? → See the Measurement Procedure section
- What does X mean? → See the Phenomenon section
- What are X's limits? → See the Limitations section

When comparing to literature (C2):
- Compare the **Phenomenon**, not just the **Metric name**
- Different metrics can measure the same phenomenon (L11-L14)
- Same metric name can measure different phenomena (version differences)
