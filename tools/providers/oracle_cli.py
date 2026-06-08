"""Lightweight Oracle Cloud (OCI) CLI helper for provisioning a free-tier VM.

This module offers helper functions that build and optionally run `oci` CLI
commands to create a VM, wait for its public IP, and delete it. It is
intentionally conservative: it requires `oci` CLI configured with a profile
that has permission to create instances.

It does NOT attempt to manage keys automatically beyond creating a temporary
SSH keypair in the current working directory if requested. Use with care.
"""

from __future__ import annotations

import json
import os
import shlex
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Optional, Tuple


def _which(cmd: str) -> Optional[str]:
    return shutil.which(cmd)


def check_oci_cli() -> bool:
    return _which("oci") is not None


def make_ssh_keypair(out_dir: Path, name: str = "oci_key") -> Tuple[Path, Path]:
    priv = out_dir / f"{name}"
    pub = out_dir / f"{name}.pub"
    if priv.exists() and pub.exists():
        return priv, pub
    subprocess.run(["ssh-keygen", "-t", "rsa", "-b", "2048", "-f", str(priv), "-N", ""], check=True)
    return priv, pub


def create_instance_cli_commands(compartment_id: str, availability_domain: str, shape: str = "VM.Standard.E2.1", image_id: Optional[str] = None, ssh_pub_key_path: Optional[Path] = None, display_name: str = "c1-runner") -> list[str]:
    """Return a list of `oci` CLI commands to create a minimal instance.

    This does NOT run the commands; the caller can run them after review.
    """
    cmds = []
    # ensure network resources exist (VCN, subnet) — user may provide existing IDs.
    # For simplicity, use a quickcreate which requires a shape and image here.
    qc = [
        "oci", "compute", "instance", "launch", 
        "--compartment-id", compartment_id,
        "--shape", shape,
        "--display-name", display_name,
        "--assign-public-ip", "true",
        "--metadata", "'ssh_authorized_keys={}'"
    ]
    # placeholder; actual invocation should fill ssh key and image
    if image_id:
        qc.extend(["--image-id", image_id])
    # The metadata must include the public key; caller should format the command
    # properly with the public key contents.
    cmds.append(" ".join(shlex.quote(p) for p in qc))
    return cmds


def run_command(cmd: str, capture: bool = False) -> Tuple[int, str]:
    if capture:
        proc = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        out = (proc.stdout or "") + (proc.stderr or "")
        return proc.returncode, out
    else:
        proc = subprocess.run(cmd, shell=True)
        return proc.returncode, ""


def get_instance_public_ip(instance_id: str, profile: Optional[str] = None) -> Optional[str]:
    """Query OCI for the instance public IP. Returns string or None.

    Requires `oci` CLI configured with a default profile or provided profile
    via environment/arguments.
    """
    if not check_oci_cli():
        return None
    cmd = f"oci compute instance list-vnics --instance-id {shlex.quote(instance_id)} --raw-output"
    rc, out = run_command(cmd, capture=True)
    if rc != 0:
        return None
    try:
        data = json.loads(out)
        # data expected to be a list of vnics
        for v in data:
            if v and isinstance(v, dict):
                ip = v.get("public-ip") or v.get("publicIps") or None
                if ip:
                    return ip
    except Exception:
        return None
    return None


def delete_instance(instance_id: str) -> int:
    if not check_oci_cli():
        return 1
    cmd = f"oci compute instance terminate --instance-id {shlex.quote(instance_id)} --force"
    rc, _ = run_command(cmd, capture=False)
    return rc


if __name__ == "__main__":
    print("This module provides helpers for OCI CLI; use programmatically.")
