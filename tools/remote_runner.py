#!/usr/bin/env python3
"""Remote runner: copy workspace to a remote host and run C1 observation safely.

Usage examples:
  python tools/remote_runner.py --host 1.2.3.4 --user ubuntu --key /path/to/key \
    --project Django --repo-url https://github.com/django/django.git --workdir c1_django_remote

Notes:
- Requires `ssh` and `scp` available locally.
- Remote host must accept key-based auth or passwordless ssh.
- The script uploads a tarball of the current workspace (excluding .venv).
- On the remote it will create a venv, install minimal runtime deps, and run
  `tools/c1_observe.py` with `PYTHONPATH` set to the project tree.
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

EXCLUDES = [".venv", "venv", "dist", "build", ".git", "tests"]


def make_workspace_tar(out_path: Path) -> Path:
    base = ROOT
    tar_path = out_path / "workspace_package.tar.gz"
    with tarfile.open(tar_path, "w:gz") as tar:
        for p in base.rglob("*"):
            rel = p.relative_to(base)
            if any(part in EXCLUDES for part in rel.parts):
                continue
            tar.add(p, arcname=str(rel))
    return tar_path


def _scp_put(tar_path: Path, user: str, host: str, key: str | None, remote_tmp: str = "/tmp") -> int:
    target = f"{user}@{host}:{remote_tmp}/"
    cmd = ["scp", "-o", "StrictHostKeyChecking=no"]
    if key:
        cmd.extend(["-i", str(key)])
    cmd.append(str(tar_path))
    cmd.append(target)
    return subprocess.run(cmd).returncode


def _ssh_run(user: str, host: str, key: str | None, cmd: str) -> int:
    ssh_cmd = ["ssh", "-o", "StrictHostKeyChecking=no"]
    if key:
        ssh_cmd.extend(["-i", str(key)])
    ssh_cmd.append(f"{user}@{host}")
    ssh_cmd.append(cmd)
    return subprocess.run(ssh_cmd).returncode


def build_remote_commands(remote_dir: str, repo_base: str, project: str, repo_url: str, workdir_name: str | None, python_cmd: str = "python3") -> str:
    # remote_dir: path where tar was extracted (parent of repo_base)
    repo_path = f"{remote_dir}/{repo_base}"
    workdir_arg = workdir_name or f"c1_{project.lower()}"
    cmds = [
        f"set -e",
        f"mkdir -p {remote_dir}",
        f"tar -xzf /tmp/workspace_package.tar.gz -C {remote_dir}",
        f"cd {repo_path}",
        f"{python_cmd} -m venv venv || {python_cmd} -m venv venv",
        f". venv/bin/activate",
        f"pip install --upgrade pip",
        # install minimal deps from pyproject to run the observer
        f"pip install networkx typer rich pydantic || true",
        # ensure PYTHONPATH points to the checked-out tree so `import ags` works
        f"export PYTHONPATH={repo_path}:$PYTHONPATH",
        f"venv/bin/python tools/c1_observe.py {project} {repo_url} {workdir_arg}",
    ]
    return " && ".join(cmds)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--host", required=True)
    p.add_argument("--user", default=os.getlogin())
    p.add_argument("--key", help="Path to private SSH key file", type=Path)
    p.add_argument("--remote-dir", default="/tmp/opencode_remote")
    p.add_argument("--project", required=True)
    p.add_argument("--repo-url", required=True)
    p.add_argument("--workdir-name", help="Optional remote workdir name")
    p.add_argument("--python", default="python3", help="Python command on remote")
    args = p.parse_args()

    key = args.key if args.key else None

    # create tarball
    with tempfile.TemporaryDirectory() as td:
        tdpath = Path(td)
        tar_path = make_workspace_tar(tdpath)
        print(f"Created workspace tar: {tar_path}")

        print(f"Uploading to {args.user}@{args.host}:/tmp/")
        rc = _scp_put(tar_path, args.user, args.host, key)
        if rc != 0:
            print("scp failed", file=sys.stderr)
            return rc

        print("Extracting and running on remote host...")
        repo_base = ROOT.name
        remote_cmd = build_remote_commands(args.remote_dir, repo_base, args.project, args.repo_url, args.workdir_name, python_cmd=args.python)
        rc = _ssh_run(args.user, args.host, key, remote_cmd)
        if rc != 0:
            print(f"Remote execution failed with exit code {rc}", file=sys.stderr)
        return rc


if __name__ == "__main__":
    raise SystemExit(main())
