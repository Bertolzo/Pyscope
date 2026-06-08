# Architectural Memory

**Layer**: 7
**Purpose**: Define state history, similarity, and recall

---

## Definition

Memory is the capacity to compare architectural states over time and across projects.

Memory is a concept, not an implementation.

The mechanism (vector store) is an implementation detail.

---

## Concepts

### State History

**Definition**: Temporal sequence of states.

**Purpose**: Track evolution over time.

**Example**:
```
S(t=0) = {entropy: 20, acp: 85, ...}
S(t=30) = {entropy: 25, acp: 82, ...}
S(t=60) = {entropy: 30, acp: 78, ...}
```

---

### Similarity

**Definition**: Comparison between states.

**Purpose**: Find similar architectural patterns.

**Example**:
```
similarity(S_project_A, S_project_B) = 0.87
```

---

### Recall

**Definition**: Retrieval of relevant past states.

**Purpose**: Learn from history.

**Example**:
```
recall(current_state, top_k=5) → [
    {project: "Django", similarity: 0.92, outcome: "healthy"},
    {project: "Celery", similarity: 0.85, outcome: "complex"},
    ...
]
```

---

## Embedding

The State Vector can be converted to a numerical vector for memory operations.

```
embedding = [0.72, 0.18, 0.33, 0.85, 0.90, 0.12, 0.78, 0.95, 3, 0.45]
```

**Dimension**: 10

---

## Implementation (Future)

The embedding can be stored in a vector store.

This is an implementation detail, not part of the FASM.

---

## Rules

1. Memory stores state representations.
2. Memory never stores implementation artifacts directly.
3. Memory cannot be redefined by lower layers.
4. The mechanism is an implementation detail.
