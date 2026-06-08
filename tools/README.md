# ADO Tools

Operational tools for the Architectural Dynamics Observatory.

## verify_baseline.py

Verifies the FASM v1.0 baseline against the current state of the
repository. Reads `docs/FASM_BASELINE_v1.md` and computes SHA-256
hashes of all frozen documents and source files, comparing them
against the baseline.

### Usage

```bash
# Verify all sections
python tools/verify_baseline.py

# Verify only one section
python tools/verify_baseline.py --section=scientific
python tools/verify_baseline.py --section=apparatus
python tools/verify_baseline.py --section=cirs

# JSON output (for CI)
python tools/verify_baseline.py --json

# Verbose output
python tools/verify_baseline.py --verbose

# Suggest bump type (without verifying)
python tools/verify_baseline.py --suggest-bump

# Ignore whitespace-only differences
python tools/verify_baseline.py --ignore-whitespace

# Update baseline (after explicit decision to bump version)
python tools/verify_baseline.py --update --confirm
```

### Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Baseline OK — all hashes match |
| 1 | Document or code diverged |
| 2 | CIR below baseline (future use) |
| 3 | Hashed file missing |
| 4 | Baseline file not found |

### Sections Verified

- **Section A: Scientific Model** — 11 frozen documents
  (ONTOLOGY, THEORY, PHENOMENA, STATE_VECTOR, METRICS,
  FALSIFIABILITY, LIMITATIONS, MEASUREMENT_THEORY,
  CIR_INVARIANTS, C0_RESULTS, SCIENTIFIC_VALIDATION_PROTOCOL)

- **Section B: Experimental Apparatus** — 9 source files
  (`ags/synthetic/*.py` + `tests/test_synthetic_c00.py`)

- **Section C: CIR Numerical Baselines** — recorded values
  (verification requires running pytest; this tool only reports
  the recorded count)

### Bump Type Heuristics

When a hash diverges, the tool suggests a bump type based on which
file changed:

| File changed | Suggested bump |
|--------------|----------------|
| `docs/ONTOLOGY.md`, `docs/THEORY.md`, `docs/PHENOMENA.md` | MAJOR |
| `docs/METRICS.md`, `docs/STATE_VECTOR.md`, `docs/MEASUREMENT_THEORY.md` | MINOR |
| `docs/FALSIFIABILITY.md`, `docs/LIMITATIONS.md` | MINOR |
| `docs/CIR_INVARIANTS.md`, `docs/C0_RESULTS.md` | MINOR |
| `ags/synthetic/*` | MINOR |
| `tests/*` | PATCH |
| Whitespace only | PATCH |

### When to Run

- **Pre-commit:** Before committing changes to frozen documents
- **CI:** On every PR, to block drift
- **Pre-release:** Before declaring a new version
- **Manual:** When investigating baseline integrity

### CI Integration

```yaml
# Example GitHub Actions step
- name: Verify FASM baseline
  run: python tools/verify_baseline.py
```

If the baseline fails, the PR should be blocked. The developer
must:

1. Run `python tools/verify_baseline.py --suggest-bump` to see
   the recommended bump type
2. If MAJOR/MINOR: justify the change in `docs/AUDIT.md`
3. Run `python tools/verify_baseline.py --update --confirm` to
   regenerate the baseline
4. Update the version in `docs/FASM_BASELINE_v1.md` and
   `docs/ARCHITECTURE.md`

### What This Tool Does Not Do

- It does not re-run CIR tests to verify numerical baselines
  (this requires `pytest tests/test_synthetic_c00.py`)
- It does not enforce the baseline is up-to-date with the code
  (this is a separate process)
- It does not hash the verifier itself (to avoid self-reference)
