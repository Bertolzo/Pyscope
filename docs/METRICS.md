# FASM Metrics

**Layer**: 5
**Purpose**: Define how phenomena are quantified

---

## Metric Validation Protocol

Every metric must define:

```
Name:
Phenomenon:
Observable Aspect:
Units:
Bounds:
Formula:
Interpretation:
Invariant:
State Dimension:
```

If any field is missing, REJECT THE METRIC.

---

## Hierarchy

```
Phenomenon (Layer 2)
   ↓
Observable Aspect (multiple per phenomenon)
   ↓
Metric (one or more per aspect)
```

Metrics are *instruments*, not phenomena. A metric can be replaced
without redefining its phenomenon. The mapping from metric to phenomenon
is stable; the formula of the metric is revisable.

---

## Metrics

### Entropy Score

**Name**: Entropy Score
**Phenomenon**: Architectural Entropy
**Observable Aspect**: magnitude
**Units**: points
**Bounds**: [0, ∞)
**Formula**: E = Σ(cost_i × violation_i) for all files i
**Interpretation**: Accumulated architectural debt
**Invariant**: E >= 0
**State Dimension**: entropy.current

---

### Entropy Velocity

**Name**: Entropy Velocity
**Phenomenon**: Architectural Entropy
**Observable Aspect**: velocity
**Units**: points/day
**Bounds**: (-∞, ∞)
**Formula**: dE/dt = 2a·t + b (derivative of quadratic fit at current time)
**Interpretation**: Speed of architectural deterioration
**Invariant**: none (can be positive or negative)
**State Dimension**: entropy.velocity

---

### Entropy Acceleration

**Name**: Entropy Acceleration
**Phenomenon**: Architectural Entropy
**Observable Aspect**: acceleration
**Units**: points/day²
**Bounds**: (-∞, ∞)
**Formula**: d²E/dt² = 2a (second derivative, constant for quadratic)
**Interpretation**: Acceleration of architectural deterioration
**Invariant**: none (can be positive or negative)
**State Dimension**: entropy.acceleration

---

### ACP (Architectural Coupling Pressure)

**Name**: ACP
**Phenomenon**: Structural Pressure
**Observable Aspect**: inter-domain dependency ratio
**Units**: %
**Bounds**: [0, 100]
**Formula**: ACP = 100 - (cross_domain_edges / max_acceptable × 50)
**Interpretation**: Amount of structural interaction across domains
**Invariant**: 0 <= ACP <= 100
**State Dimension**: acp

---

### Dependency Density

**Name**: Dependency Density
**Phenomenon**: Structural Pressure
**Observable Aspect**: coupling intensity
**Units**: ratio
**Bounds**: [0, 1]
**Formula**: DD = actual_edges / max_possible_edges
**Interpretation**: Intensity of interconnections in the system
**Invariant**: 0 <= DD <= 1
**State Dimension**: dependency_density

---

### DCI (Design Cohesion Index)

**Name**: DCI
**Phenomenon**: Structural Cohesion
**Observable Aspect**: intra-module vs inter-module edge ratio
**Units**: %
**Bounds**: [0, 100]
**Formula**: DCI = 100 - contamination_ratio × 100
**Interpretation**: Degree to which related components remain grouped
**Invariant**: 0 <= DCI <= 100
**State Dimension**: dci

---

### Boundary Leakage

**Name**: Boundary Leakage
**Phenomenon**: Operational Boundary Leakage
**Observable Aspect**: file-level cross-domain imports
**Units**: ratio
**Bounds**: [0, 1]
**Formula**: BL = file_edges_between_communities / total_file_edges
**Interpretation**: Transfer of responsibility between domains at file level
**Invariant**: 0 <= BL <= 1
**State Dimension**: boundary_leakage

---

### CRI (Composite)

**Name**: CRI
**Phenomenon**: Architectural Health
**Observable Aspect**: composite response to change
**Units**: score
**Bounds**: [0, 100] (real) or [0, 1] (synthetic)
**Formula**: CRI = w1×entropy + w2×acp + w3×dci + w4×agp + ...
**Interpretation**: Overall architectural health (composite indicator)
**Invariant**: 0 <= CRI <= 100
**State Dimension**: cri

**Known limitation (CIR-4B)**: CRI is a *first-order projection* dominated
by ACP-related components in synthetic architectures. This is
documented in LIMITATIONS.md (L17). The current weights are
heuristic, not data-driven. No re-weighting is permitted before C1
observation. CRI is an *indicator*, not a definition: architectural
health exists independently of CRI.

---

### AGP (Architectural Governance Purity)

**Name**: AGP
**Phenomenon**: Governance Compliance
**Observable Aspect**: domain count vs declared limit
**Units**: %
**Bounds**: [0, 100]
**Formula**: AGP = 100 - (domain_count - 1) × 15 (for domain_count <= max_domains)
**Interpretation**: Degree of adherence to architectural rules
**Invariant**: 0 <= AGP <= 100
**State Dimension**: agp

---

### Context Radius

**Name**: Context Radius
**Phenomenon**: Architectural Reachability
**Observable Aspect**: transitive reach
**Units**: files
**Bounds**: [0, ∞)
**Formula**: CR = |visited_nodes| - 1 (BFS from source, source excluded)
**Interpretation**: Amount of system affected by a change
**Invariant**: CR >= 0
**State Dimension**: context_radius

---

### Half-Life

**Name**: Half-Life
**Phenomenon**: Architectural Drift
**Observable Aspect**: velocity (rate of entropy change)
**Units**: months
**Bounds**: (0, ∞) or inf
**Formula**: T½ = (E_target - E_current) / velocity
**Interpretation**: Time until operational collapse (linear extrapolation)
**Invariant**: T½ > 0 or T½ = inf
**State Dimension**: none (derived from entropy.velocity)

**Note**: Half-Life is an *operational indicator*, not a prediction.
The PredictionEngine (Layer 4) is responsible for prediction. Half-Life
uses linear extrapolation; prediction uses Taylor expansion.

---

### Graph Drift

**Name**: Graph Drift
**Phenomenon**: Architectural Drift
**Observable Aspect**: magnitude
**Units**: ratio (Jaccard distance)
**Bounds**: [0, 1]
**Formula**: GD = 1 - |E1 ∩ E2| / |E1 ∪ E2|
**Interpretation**: Overall change in dependency structure
**Invariant**: 0 <= GD <= 1
**State Dimension**: none (derived metric)

---

## Rules

1. Every metric must have units.
2. Every metric must have invariants.
3. Every metric must have interpretation.
4. Every metric must map to a phenomenon and an observable aspect.
5. Every metric must be representable in S(t) (or be explicitly
   derived from S(t) components).
6. Metrics cannot be redefined by lower layers.
7. Composite metrics (CRI) are indicators of phenomena whose nature
   is composite, not definitions of those phenomena.
8. Metric weights are heuristic and must not be adjusted to fit
   observed data before C1.

---

## Evolution Policy

Metrics are **frequently revised**. A metric can be:
- Added (when a new observable aspect requires a new instrument)
- Replaced (when a better instrument is found)
- Refined (formula change, bounds change, units change)

Metric changes require:
- MINOR bump if the phenomenon mapping is preserved
- MAJOR bump if the phenomenon mapping changes
- PATCH bump if only the formula is updated (same bounds, same units,
  same phenomenon)
