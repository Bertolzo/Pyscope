# Pyscope Validation Phase Plan

## Overview

Phase-based validation of Pyscope using external tools and strategic fallbacks, with syntactic equivalence in commands so comparisons remain fair and reproducible.

This document complements the internal `pytest -q` validation already executed for Pyscope.

## Phase 1 — Import coverage (text)

- Primary: `grep`
- Fallback 1: `rg` (ripgrep)
- Fallback 2: `git grep`

### Standard command

```bash
<tool> -rE "^(import |from )" --include="*.py" <directory>
```

### Guarantee

All three support the same regular expression syntax and recursion flags. If none are available, use:

```bash
find <directory> -name '*.py' -print0 | xargs -0 grep -E "^(import |from )"
```

### Purpose

Verify that Pyscope captures project-local imports and does not omit static import statements that should be part of its dependency graph.

## Phase 2 — Graph inspection (visual)

- Primary: `pydeps`
- Fallback 1: `pyreverse`
- Fallback 2: `snakefood`

### Standard commands

```bash
pydeps --cluster -o output.png <project>
pyreverse -o png -p project <directory>
sfood <directory> | sfood-graph | dot -Tpng > output.png
```

### Guarantee

All tools produce a `.dot` or image artifact that can be inspected visually. The validation is fair when we compare the same representation class: package/module dependency graph.

### Purpose

Confirm that the Pyscope dependency structure is coherent with an independent dependency graph visualization.

## Phase 3 — Reference inspection (LSP)

- Primary: `pylsp`
- Fallback 1: `pyright`
- Fallback 2: `jedi-language-server`

### Guarantee

The output is a comparable set of reference locations for a symbol or module. The validation compares the set of referring files reported by the LSP with the dependent files reported by AGS.

### Purpose

Validate that Pyscope identifies the same strong dependency relationships that a symbol-level reference analysis reveals.

## Phase 4 — Cohesion by call graph

- Primary: `pyan3`
- Fallback 1: `code2flow`
- Fallback 2: `python -m trace --count`

### Standard command

```bash
pyan3 <directory>/*.py --dot > calls.dot
```

### Guarantee

The call graph must provide a comparable representation of internal vs external calls. If the fallback only produces a visual artifact, use it to derive the same edge-level cohesion data.

### Purpose

Check whether Pyscope DCI trends align with a call-graph-based view of component cohesion.

## Phase 5 — Structural violation search

- Primary: `ast-grep`
- Fallback 1: `serena`
- Fallback 2: Python `ast.parse` script

### Guarantee

All approaches should implement the same structural rule, such as: “domain modules must not import infra modules.” The validation result is a count/list of violations.

### Purpose

Validate that Pyscope leakage metrics are proportional to actual structural import violations.

## Summary table

| Phase | Primary | Fallback 1 | Fallback 2 | Equivalence guarantee |
|------|---------|------------|------------|----------------------|
| 1 | grep | rg | git grep | same regex semantics and recursive search |
| 2 | pydeps | pyreverse | snakefood | `.dot`/image output for graph comparison |
| 3 | pylsp | pyright | jedi-lsp | same symbol-reference output model |
| 4 | pyan3 | code2flow | trace | call graph edge output for cohesion analysis |
| 5 | ast-grep | serena | ast.parse | same structural import violation rule |

## Notes

- This validation plan is designed to be reproducible and resilient: a failing tool does not stop the comparison.
-- The goal is not to find the best tool, but to confirm the Pyscope result across equivalent artifact types.
- When using fallbacks, preserve the same command shape and the same interpretation of the output.

## Recommended usage

1. Run Pyscope and export its JSON report and graph.
2. Run the primary tool for each phase.
3. If the primary tool is unavailable, use the fallback.
4. Compare outputs on the same project and record discrepancies.
5. Document findings in `docs/AGS_SECOND_AGENT_CORRELATION.md` or a dedicated validation report.
