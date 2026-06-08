# Pyscope Ontology

**Layer**: 0
**Purpose**: Define what exists in architecture

---

## Entities

### Architecture

A system composed of components and relationships.

**Attributes**:
- Components (modules, files, classes)
- Relationships (dependencies, imports)
- Boundaries (domain separators)
- State (vector representation)

---

### Boundary

A separator between architectural domains.

**Types**:
- Logical boundary (domain separation)
- Physical boundary (directory structure)
- Dependency boundary (import rules)

---

### Dependency

A directed relationship between components.

**Types**:
- File import (service.py → repository.py)
- Module dependency (module:application → module:domain)
- Inheritance (class → base class)
- Composition (class → member class)

---

### Violation

A dependency that crosses a boundary incompatibly with architectural governance.

**Types**:
- Layer violation (infrastructure → domain)
- Cycle violation (A → B → A)
- Boundary violation (domain A → domain B)

---

### State

The minimal vector representation of an architecture at an instant t.

**Representation**: ArchitecturalStateVector

**Dimensions**:
- entropy
- acp
- dci
- boundary_leakage
- cri
- agp
- context_radius
- dependency_density

---

### Dynamics

The evolution of state over time.

**Components**:
- velocity (rate of change)
- acceleration (rate of rate of change)
- drift (structural divergence)
- regression (quality degradation)

---

### Governance

A decision based on current state, future state, and rules.

**Decisions**:
- ALLOW
- WARN
- BLOCK

---

### Memory

The capacity to compare architectural states over time and across projects.

**Concepts**:
- State history
- Similarity comparison
- Relevant recall

---

### Causal Factor

A reason WHY a phenomenon occurs.

**Examples**:
- New module added
- Circular dependency introduced
- Incomplete refactoring
- Cross-domain coupling increased

---

## Relationships

```
Architecture
    ├── contains → Component
    ├── has → Boundary
    ├── exhibits → Dependency
    ├── produces → Violation
    ├── possesses → State
    ├── evolves → Dynamics
    ├── governed by → Governance
    └── remembered by → Memory

Dependency
    ├── crosses → Boundary
    └── caused by → Causal Factor

Violation
    ├── caused by → Causal Factor
    └── detected by → Governance

State
    ├── measured by → Metrics
    └── transformed by → Dynamics
```

---

## Rules

1. No implementation may introduce a new entity without updating this document.
2. All entities must be explicitly declared and justified.
3. Entities cannot be redefined by lower layers.
