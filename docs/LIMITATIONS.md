# LIMITATIONS — FASM Scope and Bounds

## Purpose

This document defines what FASM **cannot** do and where its claims
**do not apply**. It is the boundary specification of the model.

Written before FALSIFIABILITY.md because:
> Limitations define the space where falsification is valid.

Without this document, falsification conditions would be written too
broadly and later need to be relativized by limitations discovered
during observation.

---

## I. Epistemic Limitations

### L1: No prediction of future state

FASM observes snapshots. It does not predict.

- **In scope**: "State S(t) has these properties at time t"
- **Out of scope**: "State S(t+1) will have these properties"

**Implication for falsification:** F1-F3 falsify the *current* model,
not future predictions. Predictive claims require a separate validation
framework (C2 time-series correlation).

### L2: No self-validation (circularity)

FASM cannot validate itself. All validation requires external reference:
- **C0**: synthetic self-consistency (weakest)
- **C1**: real project observation (stronger)
- **C2**: literature correlation (strongest)

**Implication for falsification:** F4 (orthogonality) only proves
within-model independence. Cross-model orthogonality requires C2.

### L3: Static snapshot only

FASM analyzes static graph snapshots. It does not model:
- Runtime behavior (call graphs, dynamic dispatch)
- Test execution paths
- Build-time vs runtime dependencies

**Implication:** If a system's structural properties are runtime-dependent,
FASM measures only the static import graph, not the actual behavior.

### L4: Observations are approximations (Axiom 7)

Every metric is an approximation of a phenomenon:
- ACP approximates "structural coupling pressure" via edge counts
- DCI approximates "design cohesion" via community detection
- Leakage approximates "boundary violations" via file-level imports

**Implication:** Metric values are bounded by the measurement procedure.
Different procedures would yield different values. FASM does not claim
its measurements are "the" measurements, only that they are *consistent*.

### L5: No causal claims from correlation

CIR-1, CIR-2, CIR-3, CIR-4 are **empirical** invariants. They do not
prove causal mechanisms. Causal claims would require intervention
experiments (not feasible in software architecture at scale).

**Implication:** The regime taxonomy is a *descriptive* taxonomy,
not a *causal* taxonomy. Regimes cluster observations; they do not
explain *why* observations cluster.

---

## II. Operational Limitations

### L6: Python-only

Current implementation analyzes Python projects only. The graph extraction
pipeline uses Python AST and import resolution.

- **Out of scope**: Java, C#, JavaScript, Go, Rust, etc.
- **Workaround**: Would require language-specific extraction layers

**Implication:** All real-project observations (C1) must be Python projects.

### L7: Import-based dependency model

FASM models **imports**, not **usage**. Two files may import each other
but never call each other's functions at runtime.

- **In scope**: Static dependency structure
- **Out of scope**: Dynamic call structure, dead code, conditional imports
- **Parser behavior**: repeated import syntax does not create duplicate edges; the parser treats `import a, b` as separate dependency edges and resolves `from pkg import sub` to the submodule when possible.

**Implication:** A module with high ACP may have low actual coupling
if the imports are unused or conditional.

### L8: Community detection is approximate

FASM uses Louvain community detection. Louvain:
- Is non-deterministic (different runs may produce different communities)
- Has resolution limits (cannot detect very small or very large communities)
- Optimizes modularity, not domain structure

**Implication:** DCI and ACP values are sensitive to Louvain's output.
Different community detection algorithms would yield different values.

**Mitigation:** CIR-4 redefined DCI as 1 - cross_module_ratio (not
community-based) to reduce this dependency.

### L9: Scale limits

Tested up to 10k files, <60s analysis, <1.5GB memory.

- **Above 10k files**: Performance degrades
- **Above 100k files**: Likely to fail (untested)
- **Below 100 files**: Statistics may be unstable (small sample effects)

**Implication:** Very large monorepos may need sampling or
hierarchical analysis.

### L10: Radon-dependent metrics

CRI computation uses Radon (Maintainability Index + Cyclomatic Complexity).
On synthetic graphs, these are degraded because synthetic graphs lack
real source code.

- **In scope (real projects)**: Full CRI with Radon components
- **Degraded (synthetic)**: CRI_synthetic = weighted sum of primitive metrics
  (no Radon)

**Implication:** CRI values on synthetic graphs are approximations.
Comparisons between synthetic CRI and real CRI should be done carefully.

---

## III. Comparative Limitations

FASM metrics are **not direct replacements** for existing software
metrics. They measure related but distinct phenomena.

### L11: vs CBO (Coupling Between Objects)

| Aspect | CBO | FASM ACP |
|--------|-----|----------|
| Granularity | Class-level | Module/domain-level |
| Counts | Methods called on other classes | Cross-domain edges |
| Direction | Undirected | Directed |
| Scope | Single class | Whole graph |

**CBO ≠ ACP.** A class with high CBO may be in a module with low ACP
if other classes in the same module are not coupled.

### L12: vs LCOM (Lack of Cohesion of Methods)

| Aspect | LCOM | FASM DCI |
|--------|------|----------|
| Granularity | Class-level | Module/domain-level |
| Measures | Method-method interaction via shared instance vars | Cross-community edges |
| Direction | N/A | Implied by community structure |
| Scope | Single class | Whole graph |

**LCOM ≠ DCI.** LCOM measures *internal* class cohesion; DCI measures
*external* module contamination. High LCOM does not imply low DCI.

### L13: vs RFC (Response For a Class)

| Aspect | RFC | FASM Context Radius |
|--------|-----|---------------------|
| Granularity | Class-level | File-level |
| Measures | Methods potentially invoked | Files potentially affected |
| Trigger | External method call | Change in a file |
| Scope | Single class | Whole graph (BFS from node) |

**RFC ≠ Context Radius.** RFC counts *response* to a call; Context
Radius counts *impact* of a change. They are related but measure
different things.

### L14: No direct correspondence to any single classical metric

FASM is a *composite* framework. It is not:
- A CBO calculator
- An LCOM calculator
- An RFC calculator
- A cyclomatic complexity calculator

It is a *unified observation system* that produces multiple metrics
simultaneously from a single graph extraction.

**Implication:** When comparing to literature (C2), expect partial
correlations, not exact equivalences.

---

## IV. Scope of the Synthetic System (C0)

### L15: Synthetic ≠ Real

C0.0 produces synthetic graphs. These:
- Are valid DiGraphs
- Satisfy CIR-1, CIR-2, CIR-3, CIR-4A
- Do **not** represent real-world distributions

**Implication:** C0 results are *necessary* but not *sufficient* for
real-world validity. C1 observation is required.

### L16: Regime taxonomy is descriptive, not normative

The 11 regimes are a *classification* of possible graph structures.
They are not a *prescription* of good/bad architecture.

- **PERFECT** is not "good" — it's "no cross-domain edges"
- **PATHOLOGICAL** is not "bad" — it's "high coupling + cycles + leakage"

Value judgments are applied separately (governance layer), not in
the regime taxonomy.

### L17: CIR-4B currently fails

Composite Dominance test (no single CRI component > 70%) is **not met**
in the current implementation:
- Coupling contribution: ~0.94
- Cohesion contribution: ~0.88
- Containment: ~0.00
- Stability: ~0.20

**Interpretation:** CRI is effectively a weighted version of (1-ACP)
with small corrections from (1-Leakage) and (1-cycle_density).

**This is documented as a limitation, not a bug.** The system is
genuinely 2-3 dimensional in practice, not 4. CIR-4A (primitive
independence) passes; CIR-4B (composite balance) is aspirational.

---

## V. What These Limitations Mean for FASM

FASM is a **descriptive observation system** for Python software
architecture, with:

- **Strong claims** within scope (Python, static imports, 10k file limit)
- **Weak claims** outside scope (runtime, other languages, very large systems)
- **No claims** about future prediction, causal mechanisms, or normative
  valuation of regimes

This is the **epistemic contract**. Any extension beyond these bounds
requires explicit additional validation.
