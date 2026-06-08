# Architectural Phenomena

**Layer**: 2
**Purpose**: Define what can be observed in software architecture

---

## Definition

A **phenomenon** is a class of observable events in the architecture that:

- Exists independently of any specific metric
- Has an observational definition that can be expressed in natural language
- Can be falsified by empirical observation
- Survives the removal of any particular instrument (metric, analyzer, or tool)

A phenomenon is **NOT**:
- A property of a metric ("the value of ACP")
- A composite of other phenomena (composites are indicators, not phenomena)
- An operational definition (these belong to Theory, Layer 1)

---

## Hierarchy

```
Phenomenon (Layer 2)
   ↓
Observable Aspects (magnitude, velocity, acceleration, distribution, ...)
   ↓
Metrics (Layer 5)
```

A phenomenon can have multiple observable aspects. Each aspect is
operationalized by one or more metrics. Phenomena are stable across
metric evolution; observable aspects may be refined as understanding
deepens.

---

## Phenomena

### 1. Architectural Entropy

**Description**: Accumulation of architectural inconsistencies that
increase the cost of future modifications. Entropy is cumulative and
irreversible in the absence of deliberate refactoring.

**Observable aspects**:
- magnitude (current accumulated inconsistencies)
- velocity (rate of entropy change, points/day)
- acceleration (second derivative, points/day²)

**Measured by**: Entropy Score, Entropy Velocity, Entropy Acceleration

**Causal factors**:
- New module added without refactoring
- Circular dependency introduced
- Incomplete refactoring
- Cross-domain coupling increased
- Layer violation introduced

**Falsification**: If long-term architectural cost can decrease
spontaneously (without intervention), the cumulative-entropy hypothesis
is rejected.

---

### 2. Structural Pressure

**Description**: Amount and intensity of structural interaction across
architectural boundaries. Pressure is the *quantity* of inter-domain
interactions; it does not distinguish healthy from unhealthy coupling.

**Observable aspects**:
- inter-domain dependency count
- inter-domain dependency ratio
- fan-out concentration
- coupling intensity (density of interconnections)

**Measured by**: ACP, Dependency Density, Coupling Intensity

**Causal factors**:
- Domain boundaries poorly defined
- Shared modules between domains
- Infrastructure leaks into application
- High fan-out in central modules

**Note**: Structural Pressure is *neutral*. High pressure can be
healthy (necessary cross-domain coordination) or unhealthy (boundary
erosion). Pressure alone does not characterize architecture quality.

**Falsification**: If architectural quality is independent of
inter-domain interaction count, pressure is not a meaningful construct.

---

### 3. Structural Cohesion

**Description**: Degree to which related components remain grouped
within their intended boundaries. Cohesion is the inverse of boundary
erosion at the module level.

**Observable aspects**:
- intra-module vs inter-module edge ratio
- community detection agreement with declared modules
- module organization stability over time

**Measured by**: DCI (Design Cohesion Index)

**Causal factors**:
- Module reorganization
- Team structure changes
- Domain evolution
- Refactoring vs accretion

**Falsification**: If modules can be defined arbitrarily without
affecting architectural quality, cohesion is not a meaningful property.

---

### 4. Operational Boundary Leakage

**Description**: Transfer of responsibility between architectural
domains at the file level, where files in the same module but different
domains import each other. Leakage is distinct from Pressure because
it captures *violations*, not *interactions*.

**Observable aspects**:
- file-level cross-domain imports
- boundary violations in unit tests
- domain containment at file granularity

**Measured by**: Boundary Leakage Ratio

**Causal factors**:
- Convenience imports
- Circular dependencies
- Lack of clear interfaces
- Time pressure during development

**Falsification**: If architectural defects are uncorrelated with
file-level boundary violations, leakage is not a meaningful construct.

---

### 5. Architectural Drift

**Description**: Difference between current architecture and a
reference state (previous snapshot, declared design, or baseline).
Drift captures the *temporal* dimension of architectural change.

**Observable aspects**:
- magnitude (overall change, e.g. Jaccard distance)
- velocity (rate of drift per unit time)
- acceleration (rate of drift's rate of change)

**Measured by**: Graph Drift (Jaccard), Entropy Velocity, Half-Life

**Causal factors**:
- Feature development
- Refactoring
- Team growth
- Incomplete migrations
- Tooling changes

**Note**: Drift is not inherently bad. Healthy refactoring produces
drift; accretion produces drift. Drift's *interpretation* depends on
the kind of change.

**Falsification**: If architectural evolution is uncorrelated with
measured drift, drift is not a meaningful construct.

---

### 6. Governance Compliance

**Description**: Degree of adherence to declared architectural rules
and constraints. Compliance measures the gap between the intended
architecture and the observed architecture.

**Observable aspects**:
- domain count vs declared limit
- layer violation count
- cycle count vs declared limit
- file size vs declared limit

**Measured by**: AGP (Architectural Governance Purity)

**Causal factors**:
- Rule enforcement (or lack thereof)
- Team education
- Tool adoption
- Code review rigor

**Falsification**: If architectural defects are uncorrelated with
declared-rule violations, governance compliance is not a meaningful
metric of architectural quality.

---

### 7. Architectural Reachability

**Description**: Amount of the system affected by a change in a
specific component. Reachability captures the *propagation potential*
of modifications.

**Observable aspects**:
- direct reach (fan-out, immediate dependents)
- transitive reach (BFS up to depth limit)
- global reach (total affected files)

**Measured by**: Context Radius, Fan-In, Fan-Out

**Causal factors**:
- Module coupling
- Dependency structure
- Abstraction level
- Use of central utilities

**Falsification**: If change impact is uncorrelated with graph
reachability, reachability is not a meaningful construct.

---

### 8. Architectural Health

**Description**: Capacity of the architecture to absorb changes
without disproportionate degradation. Health is *resilience* under
modification, not absence of problems.

**Observable aspects**:
- response to small changes (should be local)
- response to large changes (should not be catastrophic)
- recovery time after stress
- mean time between architectural failures

**Measured by**: CRI (Composite), Half-Life, predicted degradation

**Note**: Architectural Health is the *only* phenomenon in this
catalog that has a natural composite measurement (CRI). This is because
health is itself a composite property of the system. However, health
*exists independently of CRI*: an architecture can be healthy or
unhealthy even if CRI is not computed. CRI is one instrument for
observing health; it is not the definition of health.

**Causal factors**:
- All other phenomena (Entropy, Pressure, Cohesion, Drift, Compliance,
  Reachability) contribute to Health
- External factors (team experience, tooling, code review culture)

**Falsification**: If architectural degradation is unrelated to
modification patterns, health is not a meaningful property.

---

## Causal Factor Matrix

Why do phenomena occur?

| Causal Factor | Affected Phenomena |
|---------------|-------------------|
| New module added | Drift, Entropy, Reachability |
| Circular dependency | Entropy, Compliance, Drift |
| Incomplete refactoring | Entropy, Drift, Health |
| Cross-domain coupling | Pressure, Leakage |
| Team structure change | Cohesion, Drift |
| Rule enforcement | Compliance, Health |
| Convenience imports | Leakage, Drift |
| Central utility usage | Reachability, Pressure |
| Tooling change | Drift, Entropy |
| Code review rigor | Compliance, Health |

---

## Rules

1. Every phenomenon must exist independently of any specific metric.
2. Every metric must map to a phenomenon (or to an observable aspect of a phenomenon).
3. Composite indicators (CRI) are *not* phenomena. They are instruments
   for observing phenomena whose nature is composite (e.g. Health).
4. Observable aspects may be added or refined as understanding deepens;
   phenomena should remain stable across the lifetime of the model.
5. Phenomena cannot be redefined by lower layers (Layers 3-10).
6. Causal factors explain *why* phenomena occur, not *how* they are measured.
7. If a phenomenon's definition depends on a metric, the phenomenon
   is instrumental and must be reframed or removed.

---

## Evolution Policy

Phenomena are **stable** — they define what the observatory believes
exists in the world. New phenomena are added only when:
1. A reproducible observation cannot be explained by existing phenomena, AND
2. The new phenomenon has a natural language definition that survives
   removal of any specific instrument, AND
3. The new phenomenon is falsifiable.

Observable aspects are **evolving** — they are refined as measurement
practice improves. New aspects can be added without bumping the
phenomenon version.

Metrics are **frequently revised** — they are instruments, not
reality. New metrics can be added or replaced without bumping the
phenomenon or observable aspect versions.
