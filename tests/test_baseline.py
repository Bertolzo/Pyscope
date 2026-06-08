"""
Tests for the FASM baseline verification system.

These tests verify that:
1. The baseline file exists and is parseable
2. All 11 Section A documents match the baseline
3. All 9 Section B code files match the baseline
4. The verifier detects divergences correctly
5. The bump suggestion heuristic works

Run with: python -m pytest tests/test_baseline.py -v
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

# Add tools/ to path for direct imports
REPO_ROOT = Path(__file__).resolve().parent.parent
TOOLS_DIR = REPO_ROOT / "tools"
sys.path.insert(0, str(TOOLS_DIR))

from verify_baseline import (  # noqa: E402
    BASELINE_FILE,
    parse_baseline,
    verify_file,
    suggest_bump,
    sha256_of_file,
    BaselineEntry,
    VerificationResult,
    BumpSuggestion,
)


class TestBaselineFile:
    """Baseline file exists and is parseable."""

    def test_baseline_file_exists(self):
        assert BASELINE_FILE.exists(), f"Baseline file missing: {BASELINE_FILE}"

    def test_baseline_file_is_markdown(self):
        content = BASELINE_FILE.read_text()
        assert content.startswith("# FASM Baseline v")

    def test_baseline_has_version(self):
        content = BASELINE_FILE.read_text()
        import re
        assert re.search(r"Version:\*\*\s+v?\d+\.\d+\.\d+", content), \
            "Version must follow semver (X.Y.Z)"

    def test_baseline_has_three_sections(self):
        content = BASELINE_FILE.read_text()
        assert "## Section A: Scientific Model" in content
        assert "## Section B: Experimental Apparatus" in content
        assert "## Section C: CIR Numerical Baselines" in content

    def test_baseline_has_semver_policy(self):
        content = BASELINE_FILE.read_text()
        assert "PATCH" in content
        assert "MINOR" in content
        assert "MAJOR" in content


class TestParseBaseline:
    """The parse_baseline function returns correct data."""

    def test_parse_returns_section_a(self):
        section_a, _, _ = parse_baseline(BASELINE_FILE)
        assert len(section_a) == 11, f"Expected 11 docs in Section A, got {len(section_a)}"

    def test_parse_returns_section_b(self):
        _, section_b, _ = parse_baseline(BASELINE_FILE)
        assert len(section_b) == 9, f"Expected 9 files in Section B, got {len(section_b)}"

    def test_section_a_excludes_audit(self):
        """AUDIT.md is evolutive and must not be in the frozen baseline."""
        section_a, _, _ = parse_baseline(BASELINE_FILE)
        paths = [e.path for e in section_a]
        assert "docs/AUDIT.md" not in paths
        assert "docs/ARCHITECTURE.md" not in paths

    def test_section_a_includes_core(self):
        section_a, _, _ = parse_baseline(BASELINE_FILE)
        paths = [e.path for e in section_a]
        for required in [
            "docs/ONTOLOGY.md",
            "docs/THEORY.md",
            "docs/PHENOMENA.md",
            "docs/METRICS.md",
            "docs/FALSIFIABILITY.md",
            "docs/LIMITATIONS.md",
            "docs/MEASUREMENT_THEORY.md",
        ]:
            assert required in paths, f"Missing required doc: {required}"

    def test_section_b_includes_apparatus(self):
        _, section_b, _ = parse_baseline(BASELINE_FILE)
        paths = [e.path for e in section_b]
        for required in [
            "ags/synthetic/regimes.py",
            "ags/synthetic/generator.py",
            "ags/synthetic/orthogonality.py",
            "tests/test_synthetic_c00.py",
        ]:
            assert required in paths, f"Missing required file: {required}"

    def test_section_c_has_cir_baselines(self):
        _, _, cir = parse_baseline(BASELINE_FILE)
        assert len(cir) >= 5, f"Expected at least 5 CIR baselines, got {len(cir)}"


class TestVerifyFile:
    """The verify_file function works correctly."""

    def test_verify_matching_file(self):
        section_a, _, _ = parse_baseline(BASELINE_FILE)
        result = verify_file(section_a[0])
        assert result.status == "OK", f"Expected OK, got {result.status}"

    def test_verify_missing_file(self):
        entry = BaselineEntry(
            path="docs/THIS_FILE_DOES_NOT_EXIST.md",
            expected_hash="0" * 64,
        )
        result = verify_file(entry)
        assert result.status == "MISSING"

    def test_verify_diverged_file(self):
        section_a, _, _ = parse_baseline(BASELINE_FILE)
        entry = BaselineEntry(
            path=section_a[0].path,
            expected_hash="0" * 64,  # wrong hash
        )
        result = verify_file(entry)
        assert result.status == "DIVERGED"


class TestSuggestBump:
    """The suggest_bump function returns correct bump types."""

    def test_no_changes_returns_none(self):
        suggestion = suggest_bump([])
        assert suggestion.bump_type == "none"

    def test_ontology_change_returns_major(self):
        result = VerificationResult(
            path="docs/ONTOLOGY.md",
            expected="0" * 64,
            actual="1" * 64,
            status="DIVERGED",
        )
        suggestion = suggest_bump([result])
        assert suggestion.bump_type == "major"

    def test_theory_change_returns_major(self):
        result = VerificationResult(
            path="docs/THEORY.md",
            expected="0" * 64,
            actual="1" * 64,
            status="DIVERGED",
        )
        suggestion = suggest_bump([result])
        assert suggestion.bump_type == "major"

    def test_phenomena_change_returns_major(self):
        result = VerificationResult(
            path="docs/PHENOMENA.md",
            expected="0" * 64,
            actual="1" * 64,
            status="DIVERGED",
        )
        suggestion = suggest_bump([result])
        assert suggestion.bump_type == "major"

    def test_metrics_change_returns_minor(self):
        result = VerificationResult(
            path="docs/METRICS.md",
            expected="0" * 64,
            actual="1" * 64,
            status="DIVERGED",
        )
        suggestion = suggest_bump([result])
        assert suggestion.bump_type == "minor"

    def test_apparatus_change_returns_minor(self):
        result = VerificationResult(
            path="ags/synthetic/regimes.py",
            expected="0" * 64,
            actual="1" * 64,
            status="DIVERGED",
        )
        suggestion = suggest_bump([result])
        assert suggestion.bump_type == "minor"

    def test_test_change_returns_patch(self):
        result = VerificationResult(
            path="tests/test_synthetic_c00.py",
            expected="0" * 64,
            actual="1" * 64,
            status="DIVERGED",
        )
        suggestion = suggest_bump([result])
        assert suggestion.bump_type == "patch"


class TestBaselineIntegrity:
    """Integration tests: the baseline verifies cleanly."""

    def test_all_section_a_files_match(self):
        """All 11 Section A files should match the baseline hashes."""
        section_a, _, _ = parse_baseline(BASELINE_FILE)
        for entry in section_a:
            result = verify_file(entry)
            assert result.status == "OK", f"{entry.path} status={result.status}"

    def test_all_section_b_files_match(self):
        """All 9 Section B files should match the baseline hashes."""
        _, section_b, _ = parse_baseline(BASELINE_FILE)
        for entry in section_b:
            result = verify_file(entry)
            assert result.status == "OK", f"{entry.path} status={result.status}"

    def test_hashes_are_valid_sha256(self):
        """All baseline hashes should be valid SHA-256 hex strings."""
        section_a, section_b, _ = parse_baseline(BASELINE_FILE)
        for entry in section_a + section_b:
            assert len(entry.expected_hash) == 64
            assert all(c in "0123456789abcdef" for c in entry.expected_hash)


class TestVerifierCLI:
    """Integration tests for the verify_baseline.py CLI."""

    def test_cli_passes(self):
        """Running verify_baseline.py with no changes should exit 0."""
        result = subprocess.run(
            [sys.executable, "tools/verify_baseline.py"],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
        )
        assert result.returncode == 0, f"CLI failed: {result.stderr}"
        assert "PASSED" in result.stdout

    def test_cli_json(self):
        """JSON output should be valid JSON."""
        import json
        result = subprocess.run(
            [sys.executable, "tools/verify_baseline.py", "--json"],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
        )
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["passed"] is True
        assert data["total_files"] == 20  # 11 docs + 9 code

    def test_cli_suggest_bump(self):
        """suggest-bump should return 'none' when no changes."""
        result = subprocess.run(
            [sys.executable, "tools/verify_baseline.py", "--suggest-bump"],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
        )
        assert result.returncode == 0
        assert "NONE" in result.stdout

    def test_cli_scientific_only(self):
        """--section=scientific should only verify Section A."""
        result = subprocess.run(
            [sys.executable, "tools/verify_baseline.py", "--section=scientific"],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
        )
        assert result.returncode == 0
        assert "Section A" in result.stdout
        assert "Section B" not in result.stdout or "apparatus" not in result.stdout.lower()

    def test_cli_apparatus_only(self):
        """--section=apparatus should only verify Section B."""
        result = subprocess.run(
            [sys.executable, "tools/verify_baseline.py", "--section=apparatus"],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
        )
        assert result.returncode == 0
        assert "Section B" in result.stdout
