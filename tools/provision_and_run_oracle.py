#!/usr/bin/env python3
"""Provision an Oracle Cloud Always-Free instance (via OCI CLI) and run C1 remotely.

This script is a thin orchestrator that:
- checks for `oci` CLI
- creates a temporary SSH keypair locally
- presents the `oci` CLI commands to create an instance (no automatic defaults)
- optionally runs the commands if `--execute` is passed (dangerous: requires configured OCI)
- waits for the instance to be reachable via SSH
- calls `tools/remote_runner.py` to upload and execute the observation
- optionally terminates the instance at the end

This keeps provider-specific code isolated from the general `remote_runner`.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path

from tools.providers.oracle_cli import (
    check_oci_cli,
    make_ssh_keypair,
    create_instance_cli_commands,
    get_instance_public_ip,
    run_command,
    delete_instance,
)

ROOT = Path(__file__).resolve().parent.parent
REMOTE_RUNNER = ROOT / "tools" / "remote_runner.py"


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--compartment-id", required=True)
    p.add_argument("--availability-domain", required=True)
    p.add_argument("--host-key-name", default="oci_c1_key")
    p.add_argument("--execute", action="store_true", help="Actually run the oci CLI commands (requires configured oci)")
    p.add_argument("--destroy", action="store_true", help="Terminate instance after run")
    p.add_argument("--host-user", default="opc")
    p.add_argument("--project", required=True)
    p.add_argument("--repo-url", required=True)
    p.add_argument("--workdir-name")
    args = p.parse_args()

    if not check_oci_cli():
        print("oci CLI not found; install and configure it first.", file=sys.stderr)
        return 2

    td = Path(".").resolve()
    priv, pub = make_ssh_keypair(td, name=args.host_key_name)
    print(f"SSH keypair created: {priv} {pub}")

    cmds = create_instance_cli_commands(compartment_id=args.compartment_id, availability_domain=args.availability_domain, display_name="c1-runner")
    print("Generated OCI CLI commands (review before running):")
    for c in cmds:
        print("  ", c)

    if not args.execute:
        print("Run with --execute to apply these commands using `oci` CLI (requires proper config and permissions).")
        return 0

    # Execute commands (caller must review security implications)
    for c in cmds:
        rc, out = run_command(c.replace("'ssh_authorized_keys={}'", f"'ssh_authorized_keys={pub.read_text(encoding='utf-8').strip()}'"), capture=True)
        print(out)
        if rc != 0:
            print("Command failed; aborting.", file=sys.stderr)
            return rc
        # naive parse of returned instance id from command output would go here; for now user must provide/inspect

    print("Instance creation commands executed. You must inspect the OCI console to get the instance OCID.")
    instance_id = input("Enter the instance OCID (or blank to abort): ").strip()
    if not instance_id:
        print("No instance provided; aborting.")
        return 1

    print("Waiting for public IP to be assigned...")
    ip = None
    for _ in range(60):
        ip = get_instance_public_ip(instance_id)
        if ip:
            break
        time.sleep(5)
    if not ip:
        print("Unable to retrieve public IP for instance.", file=sys.stderr)
        return 1

    print(f"Instance public IP: {ip}")
    # now run remote_runner
    runner_cmd = [sys.executable, str(REMOTE_RUNNER), "--host", ip, "--user", args.host_user, "--key", str(priv), "--project", args.project, "--repo-url", args.repo_url]
    if args.workdir_name:
        runner_cmd.extend(["--workdir-name", args.workdir_name])
    rc = subprocess.run(runner_cmd).returncode

    if args.destroy:
        print("Terminating instance...")
        delete_instance(instance_id)

    return rc


if __name__ == "__main__":
    raise SystemExit(main())
