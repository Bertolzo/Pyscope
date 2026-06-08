"""Resource adapter and runner for heavy analysis jobs.

Provides utilities to detect host memory/CPU and cgroup/container limits,
recommend conservative resource caps, and run a command under `nice`
and `cpulimit` when available.

Usage examples:
  python tools/resource_adapter.py --recommend
  python tools/resource_adapter.py --run "./.venv/bin/python tools/c1_observe.py Django https://github.com/django/django.git" --cpu 40 --nice 10

This script uses only the standard library and works in typical Linux
environments. It inspects /proc and /sys/fs/cgroup to infer container
quotas when possible.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from typing import Dict, Optional, Tuple

from tools.freetier_adapter import (
    get_cached_promotions,
    refresh_free_tier_promotions,
    recommend_remote_fallback,
)


def _read_first(path: str) -> Optional[str]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read().strip()
    except Exception:
        return None


def detect_total_memory_bytes() -> int:
    """Return total memory in bytes from /proc/meminfo or 0 on failure."""
    txt = _read_first("/proc/meminfo")
    if not txt:
        return 0
    for line in txt.splitlines():
        if line.startswith("MemTotal:"):
            parts = line.split()
            # value in kB
            try:
                kb = int(parts[1])
                return kb * 1024
            except Exception:
                return 0
    return 0


def detect_cpu_count() -> int:
    return os.cpu_count() or 1


def is_running_in_container() -> bool:
    # heuristic: /.dockerenv or 'docker'/'kubepods' in /proc/1/cgroup
    if os.path.exists("/.dockerenv"):
        return True
    cgroup = _read_first("/proc/1/cgroup")
    if cgroup and ("docker" in cgroup or "kubepods" in cgroup or "containerd" in cgroup):
        return True
    return False


def detect_cgroup_memory_limit() -> Optional[int]:
    # Try cgroup v2 then v1
    v2 = _read_first("/sys/fs/cgroup/memory.max")
    if v2 and v2 != "max":
        try:
            return int(v2)
        except Exception:
            pass
    v1 = _read_first("/sys/fs/cgroup/memory/memory.limit_in_bytes")
    if v1:
        try:
            return int(v1)
        except Exception:
            pass
    return None


def detect_cgroup_cpu_quota() -> Optional[Tuple[int, int]]:
    # returns (quota_us, period_us) or None
    q = _read_first("/sys/fs/cgroup/cpu.max")
    if q:
        parts = q.split()
        if parts[0] != "max":
            try:
                quota = int(parts[0])
                period = int(parts[1]) if len(parts) > 1 else 100000
                return quota, period
            except Exception:
                pass
    # v1
    quota = _read_first("/sys/fs/cgroup/cpu/cpu.cfs_quota_us")
    period = _read_first("/sys/fs/cgroup/cpu/cpu.cfs_period_us")
    if quota and period:
        try:
            return int(quota), int(period)
        except Exception:
            pass
    return None


def recommend_limits(reserve_system_gb: float = 1.0, prefer_low_impact: bool = True) -> Dict[str, object]:
    """Recommend resource caps.

    - `prefer_low_impact=True` recommends settings that avoid impacting
      critical services (more conservative).
    Returns a dict with `nice`, `cpu_percent_limit`, `memory_limit_bytes` and
    diagnostic fields.
    """
    total_mem = detect_total_memory_bytes()
    cpu_count = detect_cpu_count()
    in_container = is_running_in_container()
    cgroup_mem = detect_cgroup_memory_limit()
    cgroup_cpu = detect_cgroup_cpu_quota()

    # baseline: available memory for job = total - reserve_system
    reserve_bytes = int(reserve_system_gb * 1024 ** 3)
    if cgroup_mem and cgroup_mem > 0:
        host_mem = cgroup_mem
    else:
        host_mem = total_mem

    if host_mem <= 0:
        mem_limit = None
    else:
        # conservative fractions
        if prefer_low_impact:
            fraction = 0.4 if host_mem >= 8 * 1024 ** 3 else 0.5
        else:
            fraction = 0.7 if host_mem >= 8 * 1024 ** 3 else 0.6
        candidate = int(host_mem * fraction)
        mem_limit = max(0, candidate - reserve_bytes)
        if mem_limit <= 0:
            mem_limit = max(0, int(host_mem * 0.25))

    # CPU percent: how much of a single logical CPU the job may use
    # If cpus are quota-limited, compute available cores
    cores_quota = None
    if cgroup_cpu:
        quota_us, period_us = cgroup_cpu
        if quota_us > 0:
            cores_quota = quota_us / period_us

    if cores_quota and cores_quota > 0:
        available_cores = cores_quota
    else:
        available_cores = cpu_count

    # Recommended CPU percent for a single-process job (across all cores)
    if prefer_low_impact:
        cpu_percent_limit = min(50, int(100 * 0.6))  # cap to 60% overall
        nice = 10
    else:
        cpu_percent_limit = min(90, int(100 * available_cores))
        nice = 0

    # For safety, if machine has very low RAM, be more conservative
    if host_mem and host_mem < 4 * 1024 ** 3:
        cpu_percent_limit = min(cpu_percent_limit, 40)

    return {
        "total_memory_bytes": total_mem,
        "cgroup_memory_bytes": cgroup_mem,
        "cpu_count": cpu_count,
        "cgroup_cpu_quota": cgroup_cpu,
        "in_container": in_container,
        "recommended_nice": nice,
        "recommended_cpu_percent": cpu_percent_limit,
        "recommended_memory_limit_bytes": mem_limit,
        "notes": (
            "Prefer low impact: nice>=10 and cpu percent <=50 for shared hosts"
        ),
    }


def _which(cmd: str) -> Optional[str]:
    return shutil.which(cmd)


def run_command_with_limits(cmd: str, cpu_percent: int = 50, nice: int = 10, timeout: Optional[int] = None) -> int:
    """Run `cmd` (string) under `nice` and `cpulimit` (if available).

    Returns process exit code.
    """
    cpulimit_path = _which("cpulimit")
    shell_cmd = cmd
    if cpulimit_path:
        # cpulimit -l <percent> -- <command>
        shell_cmd = f"{cpulimit_path} -l {int(cpu_percent)} -- {cmd}"
    # apply nice
    shell_cmd = f"nice -n {int(nice)} sh -c '{shell_cmd}'"
    try:
        proc = subprocess.run(shell_cmd, shell=True, timeout=timeout)
        return proc.returncode
    except subprocess.TimeoutExpired:
        return 124


def human_bytes(b: Optional[int]) -> str:
    if b is None:
        return "unknown"
    for unit in ["B", "KiB", "MiB", "GiB", "TiB"]:
        if abs(b) < 1024.0:
            return f"{b:3.1f}{unit}"
        b /= 1024.0
    return f"{b:.1f}PiB"


def _print_free_tier_options(cache_path: Optional[str] = None) -> None:
    promotions = get_cached_promotions()
    print("Free-tier fallback promotions:")
    for promo in promotions:
        print(f"- {promo.provider}: {promo.name}")
        print(f"  resources: {promo.resources}")
        print(f"  validity: {promo.validity}")
        print(f"  url: {promo.url}")
        print(f"  notes: {promo.notes}")
        print()


def _print_remote_fallback_recommendation(prefer_low_impact: bool = True) -> None:
    rec = recommend_limits(prefer_low_impact=prefer_low_impact)
    promotions = recommend_remote_fallback(
        total_memory_bytes=int(rec["total_memory_bytes"]),
        cpu_count=int(rec["cpu_count"]),
    )
    if not promotions:
        print("No remote free-tier fallback needed for this host.")
        return

    print("\nRemote free-tier fallback recommended:")
    for promo in promotions:
        print(f"- {promo.provider}: {promo.name}")
        print(f"  resources: {promo.resources}")
        print(f"  validity: {promo.validity}")
        print(f"  url: {promo.url}")
        print(f"  notes: {promo.notes}")
        print()


def _print_recommendation(prefer_low_impact: bool = True):
    rec = recommend_limits(prefer_low_impact=prefer_low_impact)
    print("Host memory:", human_bytes(rec["total_memory_bytes"]))
    print("CGroup memory limit:", human_bytes(rec["cgroup_memory_bytes"]))
    print("CPU count:", rec["cpu_count"])
    print("In container:", rec["in_container"]) 
    print()
    print("Recommended settings:")
    print(f"  nice = {rec['recommended_nice']}")
    print(f"  cpulimit = {rec['recommended_cpu_percent']}%")
    print(f"  memory limit = {human_bytes(rec['recommended_memory_limit_bytes'])}")
    print()
    print("Notes:")
    print(rec["notes"])


if __name__ == "__main__":
    import argparse

    p = argparse.ArgumentParser()
    p.add_argument("--recommend", action="store_true")
    p.add_argument("--prefer-low-impact", action="store_true")
    p.add_argument("--run", type=str, help="Command to run under limits")
    p.add_argument("--cpu", type=int, help="CPU percent limit (0-100)")
    p.add_argument("--nice", type=int, help="nice value (e.g. 10)")
    p.add_argument("--timeout", type=int, help="timeout seconds for run")
    p.add_argument("--fallback-if-insufficient", action="store_true", help="Skip local run and print remote free-tier fallback if the host is weak")
    p.add_argument("--skip-if-insufficient", action="store_true", help="Alias for --fallback-if-insufficient")
    p.add_argument("--list-freetier", action="store_true", help="List cached free-tier fallback promotions")
    p.add_argument("--refresh-freetier-cache", action="store_true", help="Refresh the free-tier promotion cache")
    args = p.parse_args()

    skip_if_insufficient = args.fallback_if_insufficient or args.skip_if_insufficient

    if args.list_freetier:
        _print_free_tier_options()
        sys.exit(0)

    if args.refresh_freetier_cache:
        promotions = refresh_free_tier_promotions()
        print(f"Refreshed {len(promotions)} free-tier promotions")
        for promotion in promotions:
            print(f"- {promotion.provider}: {promotion.name} ({promotion.resources}) -> {promotion.url}")
        sys.exit(0)

    if args.recommend:
        _print_recommendation(prefer_low_impact=args.prefer_low_impact)
        _print_remote_fallback_recommendation(prefer_low_impact=args.prefer_low_impact)
        sys.exit(0)

    if args.run:
        rec = recommend_limits(prefer_low_impact=args.prefer_low_impact)
        promotions = recommend_remote_fallback(
            total_memory_bytes=int(rec["total_memory_bytes"]),
            cpu_count=int(rec["cpu_count"]),
            prefer_low_impact=args.prefer_low_impact,
        )
        if promotions:
            print("\nLocal host appears weak for heavy jobs. Remote free-tier fallback suggested:")
            for promo in promotions:
                print(f"- {promo.provider}: {promo.name}")
                print(f"  resources: {promo.resources}")
                print(f"  validity: {promo.validity}")
                print(f"  url: {promo.url}")
                print(f"  notes: {promo.notes}")
                print()
            if skip_if_insufficient:
                flag_name = "--fallback-if-insufficient" if args.fallback_if_insufficient else "--skip-if-insufficient"
                print(f"Skipping local execution because {flag_name} was set.")
                sys.exit(0)
            print("Proceeding with local execution because fallback was not forced.")

        cpu = args.cpu if args.cpu is not None else rec["recommended_cpu_percent"]
        nicev = args.nice if args.nice is not None else rec["recommended_nice"]
        print(f"Running with nice={nicev} cpulimit={cpu}%")
        rc = run_command_with_limits(args.run, cpu_percent=cpu, nice=nicev, timeout=args.timeout)
        print(f"Exit code: {rc}")
        sys.exit(rc)

    _print_recommendation()
