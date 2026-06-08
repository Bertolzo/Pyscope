"""
C1.0 — Requests HEAD observation.
Clones, builds graph, computes snapshot, classifies regime.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REQUESTS_REPO = "https://github.com/psf/requests.git"
WORKDIR = Path("/tmp/opencode/c1_requests")


def clone_requests(target: Path) -> Path:
    """Clone Requests HEAD."""
    if target.exists():
        shutil.rmtree(target)

    print(f"Cloning {REQUESTS_REPO} → {target}")
    result = subprocess.run(
        ["git", "clone", "--depth", "1", REQUESTS_REPO, str(target)],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        print(f"Clone failed:\n{result.stderr}")
        sys.exit(1)

    # Get commit hash
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        capture_output=True, text=True, cwd=str(target),
    )
    commit = result.stdout.strip() if result.returncode == 0 else "unknown"
    print(f"Commit: {commit}")
    return target


def main():
    print("=" * 60)
    print("C1.0 — Requests HEAD Observation")
    print("=" * 60)

    # 1. Clone
    clone_requests(WORKDIR)

    # 2. Build graph
    print("\nBuilding graph...")
    from ags.core.graph.builders import GraphBuilder

    builder = GraphBuilder(str(WORKDIR))
    graph = builder.build()

    print(f"  Files:  {graph.file_count}")
    print(f"  Modules:{graph.module_count}")
    print(f"  Edges:  {graph.edge_count}")

    # 3. Compute ObservationSnapshot
    print("\nComputing ObservationSnapshot...")
    from ags.core.observation import compute_observation_snapshot

    snap = compute_observation_snapshot(graph)

    # 4. Classify regime
    print("\nClassifying regime...")
    from ags.core.observation import classify_from_snapshot

    cls = classify_from_snapshot(snap)

    # 5. Report
    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)
    print(f"\nTotal nodes:    {snap.total_nodes}")
    print(f"Total edges:    {snap.total_edges}")
    print(f"  Cross-domain: {snap.cross_domain_edges}")
    print(f"  Intra-domain: {snap.intra_domain_edges}")
    print(f"  Unknown:      {snap.unknown_edges}")

    print(f"\nMetrics [0,1]:")
    print(f"  cross_domain_ratio:    {snap.cross_domain_ratio:.4f}")
    print(f"  intra_domain_ratio:    {snap.intra_domain_ratio:.4f}")
    print(f"  file_level_leakage:    {snap.file_level_leakage:.4f}")
    print(f"  cycle_density:         {snap.cycle_density:.4f}")
    print(f"  observation_quality:   {snap.observation_quality:.4f}")

    print(f"\nRegime Classification:")
    print(f"  Regime:          {cls.regime.value}")
    print(f"  Distance:        {cls.distance_1:.4f}")
    print(f"  2nd nearest:     {cls.second_nearest_regime.value} ({cls.distance_2:.4f})")
    print(f"  Margin:          {cls.margin:.4f}")
    print(f"  Confidence:      {cls.confidence:.4f}")

    print(f"\nC1.0 Gate Check:")
    quality_pass = snap.observation_quality >= 0.90
    margin_pass = cls.margin >= 0.10
    distance_pass = cls.distance_1 <= 0.25
    print(f"  quality >= 0.90?  {'PASS' if quality_pass else 'FAIL'} ({snap.observation_quality:.4f})")
    print(f"  margin  >= 0.10?  {'PASS' if margin_pass else 'FAIL'} ({cls.margin:.4f})")
    print(f"  distance <= 0.25? {'PASS' if distance_pass else 'FAIL'} ({cls.distance_1:.4f})")

    print(f"\nAll regimes (sorted by distance):")
    for name, dist in cls.all_distances:
        marker = " ← nearest" if name == cls.regime.value else ""
        print(f"  {name:20s}  {dist:.4f}{marker}")

    # Export
    output = {
        "project": "requests",
        "commit": subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True, text=True, cwd=str(WORKDIR),
        ).stdout.strip(),
        "snapshot": snap.to_dict(),
        "classification": {
            "regime": cls.regime.value,
            "nearest_regime": cls.nearest_regime.value,
            "second_nearest_regime": cls.second_nearest_regime.value,
            "distance_1": cls.distance_1,
            "distance_2": cls.distance_2,
            "margin": cls.margin,
            "confidence": cls.confidence,
        },
        "gates": {
            "quality_pass": quality_pass,
            "margin_pass": margin_pass,
            "distance_pass": distance_pass,
        },
    }
    out_path = Path("c1_requests_result.json")
    out_path.write_text(json.dumps(output, indent=2, default=str))
    print(f"\nResult exported to {out_path}")


if __name__ == "__main__":
    main()
