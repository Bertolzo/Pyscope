#!/usr/bin/env python3
"""Wrapper to run C1 observation safely with resource adapter fallback."""

from __future__ import annotations

import argparse
import shlex
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RESOURCE_ADAPTER = ROOT / "tools" / "resource_adapter.py"
C1_OBSERVE = ROOT / "tools" / "c1_observe.py"


def build_c1_command(project_name: str, repo_url: str, workdir_name: str | None) -> str:
    quoted = [shlex.quote(str(C1_OBSERVE)), shlex.quote(project_name), shlex.quote(repo_url)]
    if workdir_name:
        quoted.append(shlex.quote(workdir_name))
    return f"{shlex.quote(sys.executable)} {' '.join(quoted)}"


def run_adapter(args: list[str]) -> int:
    result = subprocess.run([sys.executable, str(RESOURCE_ADAPTER)] + args)
    return result.returncode


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run a C1 observation with safe local execution and remote fallback recommendations."
    )
    parser.add_argument("project_name")
    parser.add_argument("repo_url")
    parser.add_argument("workdir_name", nargs="?", default=None)
    parser.add_argument("--prefer-low-impact", action="store_true")
    parser.add_argument("--cpu", type=int)
    parser.add_argument("--nice", type=int)
    parser.add_argument("--timeout", type=int)
    parser.add_argument(
        "--fallback-if-insufficient",
        action="store_true",
        help="Skip local execution when the host is weak and print free-tier recommendations.",
    )
    parser.add_argument(
        "--force-local",
        action="store_true",
        help="Force local execution even when remote fallback is recommended.",
    )
    args = parser.parse_args()

    if args.fallback_if_insufficient and args.force_local:
        print("Cannot use --fallback-if-insufficient together with --force-local.", file=sys.stderr)
        return 2

    c1_command = build_c1_command(args.project_name, args.repo_url, args.workdir_name)

    if args.fallback_if_insufficient:
        adapter_args = ["--run", c1_command, "--fallback-if-insufficient"]
        if args.prefer_low_impact:
            adapter_args.append("--prefer-low-impact")
        if args.cpu is not None:
            adapter_args.extend(["--cpu", str(args.cpu)])
        if args.nice is not None:
            adapter_args.extend(["--nice", str(args.nice)])
        if args.timeout is not None:
            adapter_args.extend(["--timeout", str(args.timeout)])
        return run_adapter(adapter_args)

    recommend_args = ["--recommend"]
    if args.prefer_low_impact:
        recommend_args.append("--prefer-low-impact")
    recommend_proc = subprocess.run(
        [sys.executable, str(RESOURCE_ADAPTER)] + recommend_args,
        text=True,
        capture_output=True,
    )
    if recommend_proc.returncode != 0:
        print("Resource adapter recommendation failed:", file=sys.stderr)
        print(recommend_proc.stderr, file=sys.stderr)
        return recommend_proc.returncode

    if "Remote free-tier fallback recommended:" in recommend_proc.stdout and not args.force_local:
        print(recommend_proc.stdout)
        print("Host appears weak for this job. Local execution is skipped by default.")
        print("Use --force-local to override or run the job on a remote free-tier host.")
        return 0

    adapter_args = ["--run", c1_command]
    if args.prefer_low_impact:
        adapter_args.append("--prefer-low-impact")
    if args.cpu is not None:
        adapter_args.extend(["--cpu", str(args.cpu)])
    if args.nice is not None:
        adapter_args.extend(["--nice", str(args.nice)])
    if args.timeout is not None:
        adapter_args.extend(["--timeout", str(args.timeout)])
    return run_adapter(adapter_args)


if __name__ == "__main__":
    raise SystemExit(main())
