"""
C1.0 — Generic project HEAD observation.
Usage: python tools/c1_observe.py <project_name> <repo_url> [workdir_name]
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

BASE_DIR = Path("/tmp/opencode")
ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


def observe(project_name: str, repo_url: str, workdir_name: str | None = None) -> dict:
    if workdir_name is None:
        workdir_name = f"c1_{project_name.lower()}"
    target = BASE_DIR / workdir_name

    print("=" * 60)
    print(f"C1.0 — {project_name} HEAD Observation")
    print("=" * 60)

    # 1. Clone
    if target.exists():
        shutil.rmtree(target)
    print(f"\nCloning {repo_url} → {target}")
    result = subprocess.run(
        ["git", "clone", "--depth", "1", repo_url, str(target)],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        print(f"Clone failed:\n{result.stderr}")
        sys.exit(1)

    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        capture_output=True, text=True, cwd=str(target),
    )
    commit = result.stdout.strip() if result.returncode == 0 else "unknown"
    print(f"  Commit: {commit}")

    # 2. Build graph
    print("\nBuilding graph...")
    from ags.core.graph.builders import GraphBuilder
    # enable streaming parsing to handle large repositories without OOM
    builder = GraphBuilder(str(target), config={"streaming": True})
    graph = builder.build()
    print(f"  Files:  {graph.file_count}")
    print(f"  Modules:{graph.module_count}")
    print(f"  Edges:  {graph.edge_count}")

    # 3. Compute ObservationSnapshot
    print("\nComputing ObservationSnapshot...")
    from ags.core.observation import compute_observation_snapshot
    snap = compute_observation_snapshot(graph, total_imports_attempted=builder.total_imports_attempted)

    # 4. Classify
    print("\nClassifying regime...")
    from ags.core.observation import classify_from_snapshot
    cls = classify_from_snapshot(snap, size_mode="real")

    # 5. Report
    print("\n" + "-" * 60)
    print(f"RESULTS — {project_name}")
    print("-" * 60)
    print(f"  Nodes:            {snap.total_nodes}")
    print(f"  Edges:            {snap.total_edges}")
    print(f"  Cross-domain:     {snap.cross_domain_edges}")
    print(f"  Intra-domain:     {snap.intra_domain_edges}")
    print(f"  Unknown:              {snap.unknown_edges}")
    print(f"  Total imports tried:  {snap.total_imports_attempted}")
    print(f"  cross_domain_ratio:   {snap.cross_domain_ratio:.4f}")
    print(f"  intra_domain_ratio:   {snap.intra_domain_ratio:.4f}")
    print(f"  file_level_leakage:   {snap.file_level_leakage:.4f}")
    print(f"  cycle_density:        {snap.cycle_density:.4f}")
    print(f"  observation_quality:  {snap.observation_quality:.4f}")
    print(f"  Regime:              {cls.regime.value}")
    print(f"  Distance (total):    {cls.distance_1:.4f}")
    print(f"  Distance (struct):   {cls.structural_distance_1:.4f}")
    print(f"  2nd nearest:         {cls.second_nearest_regime.value} ({cls.distance_2:.4f})")
    print(f"  Margin:              {cls.margin:.4f}")
    print(f"  Confidence:          {cls.confidence:.4f}")

    quality_pass = snap.observation_quality >= 0.90
    margin_pass = cls.margin >= 0.10
    distance_pass = cls.structural_distance_1 <= 0.25
    print(f"\n  Gate quality >= 0.90:     {'PASS' if quality_pass else 'FAIL'} ({snap.observation_quality:.4f})")
    print(f"  Gate margin  >= 0.10:     {'PASS' if margin_pass else 'FAIL'} ({cls.margin:.4f})")
    print(f"  Gate struct-dist<= 0.25:  {'PASS' if distance_pass else 'FAIL'} ({cls.structural_distance_1:.4f})")

    print(f"\n  All regimes (total distance):")
    for name, dist in cls.all_distances:
        marker = " ← nearest" if name == cls.regime.value else ""
        print(f"    {name:20s}  {dist:.4f}{marker}")

    output = {
        "project": project_name.lower(),
        "commit": commit,
        "snapshot": snap.to_dict(),
        "classification": {
            "regime": cls.regime.value,
            "nearest_regime": cls.nearest_regime.value,
            "second_nearest_regime": cls.second_nearest_regime.value,
            "distance_1": cls.distance_1,
            "distance_2": cls.distance_2,
            "structural_distance_1": cls.structural_distance_1,
            "margin": cls.margin,
            "confidence": cls.confidence,
        },
        "gates": {
            "quality_pass": quality_pass,
            "margin_pass": margin_pass,
            "distance_pass": distance_pass,
        },
    }
    out_path = Path(f"c1_{project_name.lower()}_result.json")
    out_path.write_text(json.dumps(output, indent=2, default=str))
    print(f"\n  Exported to {out_path}")

    return output


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python tools/c1_observe.py <name> <repo_url> [workdir_name]")
        sys.exit(1)
    name = sys.argv[1]
    url = sys.argv[2]
    wd = sys.argv[3] if len(sys.argv) > 3 else None
    observe(name, url, wd)
