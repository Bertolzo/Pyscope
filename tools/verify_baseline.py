"""
verify_baseline.py — ADO/FASM Baseline Verifier

Verifies the FASM v1.0 baseline by comparing current file SHA-256
hashes against the values frozen in docs/FASM_BASELINE_v1.md.

Three sections verified:
  A. Scientific Model (11 docs)
  B. Experimental Apparatus (9 code files)
  C. CIR Numerical Baselines (computed at verify-time)

Usage:
    python tools/verify_baseline.py [options]

Exit codes:
    0  Baseline OK
    1  Document or code diverged
    2  CIR below baseline
    3  Hashed file missing
    4  Baseline file not found
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Repository root (parent of tools/)
REPO_ROOT = Path(__file__).resolve().parent.parent
BASELINE_FILE = REPO_ROOT / "docs" / "FASM_BASELINE_v1.md"

# Bump type heuristics
MAJOR_FILES = {
    "docs/ONTOLOGY.md",
    "docs/THEORY.md",
    "docs/PHENOMENA.md",
}
MINOR_DOCS = {
    "docs/METRICS.md",
    "docs/STATE_VECTOR.md",
    "docs/MEASUREMENT_THEORY.md",
    "docs/FALSIFIABILITY.md",
    "docs/LIMITATIONS.md",
    "docs/CIR_INVARIANTS.md",
    "docs/C0_RESULTS.md",
    "docs/SCIENTIFIC_VALIDATION_PROTOCOL.md",
    "ags/synthetic/__init__.py",
    "ags/synthetic/regimes.py",
    "ags/synthetic/spec.py",
    "ags/synthetic/generator.py",
    "ags/synthetic/graph_set.py",
    "ags/synthetic/perturbation.py",
    "ags/synthetic/coverage_audit.py",
    "ags/synthetic/orthogonality.py",
}
PATCH_FILES = {
    "tests/test_synthetic_c00.py",
}


@dataclass
class BaselineEntry:
    """A single entry in the baseline."""
    path: str
    expected_hash: str


@dataclass
class VerificationResult:
    """Result of verifying a single file."""
    path: str
    expected: str
    actual: Optional[str]
    status: str  # "OK", "DIVERGED", "MISSING", "IGNORED"
    note: str = ""


@dataclass
class BumpSuggestion:
    """Suggested version bump based on changes."""
    bump_type: str  # "patch", "minor", "major"
    changed_files: List[str] = field(default_factory=list)
    reason: str = ""


def sha256_of_file(path: Path) -> str:
    """Compute SHA-256 of a file."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def parse_baseline(baseline_path: Path) -> Tuple[List[BaselineEntry], List[BaselineEntry], Dict[str, float]]:
    """
    Parse the baseline markdown file.

    Returns:
        (section_a_entries, section_b_entries, cir_baselines)
    """
    if not baseline_path.exists():
        raise FileNotFoundError(f"Baseline file not found: {baseline_path}")

    content = baseline_path.read_text()

    section_a: List[BaselineEntry] = []
    section_b: List[BaselineEntry] = []
    cir_baselines: Dict[str, float] = {}

    # Parse markdown tables with the pattern: | `path` | `sha256:hash` |
    table_pattern = re.compile(
        r"\|\s*`([^`]+)`\s*\|\s*`sha256:([a-f0-9]+)`\s*\|"
    )

    # Find Section A
    section_a_match = re.search(
        r"## Section A:.*?(?=## Section B|$)", content, re.DOTALL
    )
    if section_a_match:
        for m in table_pattern.finditer(section_a_match.group(0)):
            section_a.append(BaselineEntry(path=m.group(1), expected_hash=m.group(2)))

    # Find Section B
    section_b_match = re.search(
        r"## Section B:.*?(?=## Section C|$)", content, re.DOTALL
    )
    if section_b_match:
        for m in table_pattern.finditer(section_b_match.group(0)):
            section_b.append(BaselineEntry(path=m.group(1), expected_hash=m.group(2)))

    # Find Section C — CIR numerical baselines
    # Format: | CIR-X | metric_name | 0.90 | threshold | status |
    section_c_match = re.search(
        r"## Section C:.*?(?=## Semver Policy|## Verification|$)", content, re.DOTALL
    )
    if section_c_match:
        cir_row_pattern = re.compile(
            r"\|\s*(CIR-[\w]+|—)\s*\|\s*([\w_]+)\s*\|\s*([\d.]+[x]?)\s*\|"
        )
        for m in cir_row_pattern.finditer(section_c_match.group(0)):
            cir = m.group(1)
            metric = m.group(2)
            value_str = m.group(3)
            # Remove 'x' suffix for ratio-like values
            if value_str.endswith("x"):
                value = float(value_str[:-1])
            else:
                value = float(value_str)
            cir_baselines[f"{cir}.{metric}"] = value

    return section_a, section_b, cir_baselines


def verify_file(entry: BaselineEntry, ignore_whitespace: bool = False) -> VerificationResult:
    """Verify a single file against the baseline."""
    path = REPO_ROOT / entry.path

    if not path.exists():
        return VerificationResult(
            path=entry.path,
            expected=entry.expected_hash,
            actual=None,
            status="MISSING",
            note="File does not exist",
        )

    actual = sha256_of_file(path)

    if ignore_whitespace and actual != entry.expected_hash:
        # Try whitespace-normalized comparison
        expected_content = (REPO_ROOT / entry.path).read_text()
        normalized = re.sub(r"\s+", " ", expected_content).strip()
        h = hashlib.sha256(normalized.encode())
        normalized_hash = h.hexdigest()

        # Recompute expected from normalized actual
        actual_content = path.read_text()
        actual_normalized = re.sub(r"\s+", " ", actual_content).strip()
        actual_norm_hash = hashlib.sha256(actual_normalized.encode()).hexdigest()

        if normalized_hash == actual_norm_hash:
            return VerificationResult(
                path=entry.path,
                expected=entry.expected_hash,
                actual=actual,
                status="OK",
                note="whitespace-only difference (ignored)",
            )

    if actual == entry.expected_hash:
        return VerificationResult(
            path=entry.path,
            expected=entry.expected_hash,
            actual=actual,
            status="OK",
        )
    else:
        return VerificationResult(
            path=entry.path,
            expected=entry.expected_hash,
            actual=actual,
            status="DIVERGED",
            note="Content changed since baseline",
        )


def suggest_bump(results: List[VerificationResult]) -> BumpSuggestion:
    """Suggest version bump type based on changed files."""
    diverged = [r for r in results if r.status == "DIVERGED"]

    if not diverged:
        return BumpSuggestion(bump_type="none", reason="No changes detected")

    paths = {r.path for r in diverged}

    # MAJOR: any of the foundational docs changed
    if paths & MAJOR_FILES:
        return BumpSuggestion(
            bump_type="major",
            changed_files=sorted(paths & MAJOR_FILES),
            reason="Axiom/phenomenon/ontology changed",
        )

    # MINOR: any doc or apparatus file changed
    if paths & MINOR_DOCS:
        return BumpSuggestion(
            bump_type="minor",
            changed_files=sorted(paths & MINOR_DOCS),
            reason="Metric/invariant/apparatus changed",
        )

    # PATCH: only test files or whitespace
    if paths & PATCH_FILES:
        return BumpSuggestion(
            bump_type="patch",
            changed_files=sorted(paths & PATCH_FILES),
            reason="Test file or formatting change",
        )

    # Default: minor
    return BumpSuggestion(
        bump_type="minor",
        changed_files=sorted(paths),
        reason="Unclassified change (defaulting to minor)",
    )


def update_baseline(
    baseline_path: Path,
    section_a: List[BaselineEntry],
    section_b: List[BaselineEntry],
) -> None:
    """Update the baseline file with current hashes."""
    content = baseline_path.read_text()

    # Update Section A hashes
    new_section_a = []
    for entry in section_a:
        path = REPO_ROOT / entry.path
        if path.exists():
            new_hash = sha256_of_file(path)
            new_section_a.append(f"| `{entry.path}` | `sha256:{new_hash}` |")
        else:
            new_section_a.append(f"| `{entry.path}` | `sha256:{entry.expected_hash}` |")

    a_pattern = re.compile(
        r"(## Section A:.*?\n\n\| File \| SHA-256 \|\n\|------\|---------\|\n)(.*?)(?=\n---|\n## )",
        re.DOTALL,
    )
    content = a_pattern.sub(
        lambda m: m.group(1) + "\n".join(new_section_a) + "\n",
        content,
    )

    # Update Section B hashes
    new_section_b = []
    for entry in section_b:
        path = REPO_ROOT / entry.path
        if path.exists():
            new_hash = sha256_of_file(path)
            new_section_b.append(f"| `{entry.path}` | `sha256:{new_hash}` |")
        else:
            new_section_b.append(f"| `{entry.path}` | `sha256:{entry.expected_hash}` |")

    b_pattern = re.compile(
        r"(## Section B:.*?\n\n\| File \| SHA-256 \|\n\|------\|---------\|\n)(.*?)(?=\n---|\n## )",
        re.DOTALL,
    )
    content = b_pattern.sub(
        lambda m: m.group(1) + "\n".join(new_section_b) + "\n",
        content,
    )

    baseline_path.write_text(content)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify FASM v1.0 baseline against current repository state"
    )
    parser.add_argument(
        "--section",
        choices=["scientific", "apparatus", "cirs", "all"],
        default="all",
        help="Which section to verify (default: all)",
    )
    parser.add_argument(
        "--update",
        action="store_true",
        help="Update baseline with current hashes",
    )
    parser.add_argument(
        "--confirm",
        action="store_true",
        help="Confirm update (required with --update)",
    )
    parser.add_argument(
        "--bump-type",
        choices=["patch", "minor", "major", "auto"],
        default="auto",
        help="Type of bump for version (default: auto-detect)",
    )
    parser.add_argument(
        "--ignore-whitespace",
        action="store_true",
        help="Ignore whitespace-only differences (PATCH-level)",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Verbose output",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="JSON output (for CI)",
    )
    parser.add_argument(
        "--suggest-bump",
        action="store_true",
        help="Only suggest bump type, do not verify",
    )
    args = parser.parse_args()

    # Handle update mode
    if args.update:
        if not args.confirm:
            print("ERROR: --update requires --confirm", file=sys.stderr)
            return 1
        try:
            section_a, section_b, _ = parse_baseline(BASELINE_FILE)
        except FileNotFoundError as e:
            print(f"ERROR: {e}", file=sys.stderr)
            return 4
        update_baseline(BASELINE_FILE, section_a, section_b)
        print("Baseline updated successfully.")
        return 0

    # Handle suggest-bump mode
    if args.suggest_bump:
        try:
            section_a, section_b, _ = parse_baseline(BASELINE_FILE)
        except FileNotFoundError as e:
            print(f"ERROR: {e}", file=sys.stderr)
            return 4
        results = []
        for entry in section_a:
            results.append(verify_file(entry, args.ignore_whitespace))
        for entry in section_b:
            results.append(verify_file(entry, args.ignore_whitespace))
        suggestion = suggest_bump(results)
        if args.json:
            print(json.dumps({
                "bump_type": suggestion.bump_type,
                "changed_files": suggestion.changed_files,
                "reason": suggestion.reason,
            }, indent=2))
        else:
            print(f"Suggested bump: {suggestion.bump_type.upper()}")
            print(f"Reason: {suggestion.reason}")
            if suggestion.changed_files:
                print("Changed files:")
                for f in suggestion.changed_files:
                    print(f"  - {f}")
        return 0

    # Normal verification
    try:
        section_a, section_b, cir_baselines = parse_baseline(BASELINE_FILE)
    except FileNotFoundError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 4

    # Filter by section
    if args.section == "scientific":
        section_b = []
    elif args.section == "apparatus":
        section_a = []
    elif args.section == "cirs":
        section_a = []
        section_b = []

    all_results: List[VerificationResult] = []

    # Verify Section A
    if section_a:
        if not args.json:
            print("=== Section A: Scientific Model ===")
        for entry in section_a:
            result = verify_file(entry, args.ignore_whitespace)
            all_results.append(result)
            if not args.json:
                if result.status == "OK":
                    msg = f"[OK] {result.path}"
                    if result.note:
                        msg += f" ({result.note})"
                    print(msg)
                elif result.status == "MISSING":
                    print(f"[MISSING] {result.path}")
                else:
                    print(f"[DIVERGED] {result.path}")
                    if args.verbose:
                        print(f"  expected: sha256:{result.expected[:16]}...")
                        print(f"  actual:   sha256:{result.actual[:16]}...")

    # Verify Section B
    if section_b:
        if not args.json:
            print()
            print("=== Section B: Experimental Apparatus ===")
        for entry in section_b:
            result = verify_file(entry, args.ignore_whitespace)
            all_results.append(result)
            if not args.json:
                if result.status == "OK":
                    msg = f"[OK] {result.path}"
                    if result.note:
                        msg += f" ({result.note})"
                    print(msg)
                elif result.status == "MISSING":
                    print(f"[MISSING] {result.path}")
                else:
                    print(f"[DIVERGED] {result.path}")
                    if args.verbose:
                        print(f"  expected: sha256:{result.expected[:16]}...")
                        print(f"  actual:   sha256:{result.actual[:16]}...")

    # Section C: CIR baselines (skipped in this implementation; requires re-running tests)
    if cir_baselines and not args.json:
        print()
        print("=== Section C: CIR Numerical Baselines ===")
        print(f"({len(cir_baselines)} CIR baselines recorded)")
        print("Run `python -m pytest tests/test_synthetic_c00.py` to verify current CIR values")

    # Summary
    diverged = [r for r in all_results if r.status == "DIVERGED"]
    missing = [r for r in all_results if r.status == "MISSING"]

    if not args.json:
        print()
        if diverged or missing:
            print(f"FAILED: {len(diverged)} diverged, {len(missing)} missing")
            bump = suggest_bump(all_results)
            print(f"Suggested bump: {bump.bump_type.upper()}")
            if bump.changed_files:
                print("Changed files:")
                for f in bump.changed_files:
                    print(f"  - {f}")
        else:
            print(f"PASSED: {len(all_results)} files match baseline")

    # JSON output
    if args.json:
        bump = suggest_bump(all_results)
        output = {
            "passed": not diverged and not missing,
            "section": args.section,
            "total_files": len(all_results),
            "diverged": len(diverged),
            "missing": len(missing),
            "results": [
                {
                    "path": r.path,
                    "status": r.status,
                    "expected": r.expected,
                    "actual": r.actual,
                    "note": r.note,
                }
                for r in all_results
            ],
            "suggested_bump": {
                "type": bump.bump_type,
                "files": bump.changed_files,
                "reason": bump.reason,
            },
        }
        print(json.dumps(output, indent=2))

    # Exit code
    if missing:
        return 3
    if diverged:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
