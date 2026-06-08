#!/usr/bin/env python3
"""Provision an OCI instance via the OCI Python SDK and run a remote C1 job."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from tools.providers.oci_sdk import (
    check_oci_sdk,
    discover_image_id,
    get_or_create_internet_gateway,
    get_or_create_route_table,
    get_or_create_security_list,
    get_or_create_subnet,
    get_or_create_vcn,
    get_instance_public_ip,
    launch_instance,
    load_oci_config,
    make_ssh_keypair,
)

ROOT = Path(__file__).resolve().parent.parent
REMOTE_RUNNER = ROOT / "tools" / "remote_runner.py"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--compartment-id", required=True)
    parser.add_argument("--availability-domain", required=True)
    parser.add_argument("--profile", default="DEFAULT")
    parser.add_argument("--config-file", help="OCI config file path")
    parser.add_argument("--shape", default="VM.Standard.E2.1.Micro")
    parser.add_argument("--image-id", help="Image OCID or omit to auto-discover Oracle Linux 8")
    parser.add_argument("--key-name", default="oci_sdk_c1_key")
    parser.add_argument("--project", required=True)
    parser.add_argument("--repo-url", required=True)
    parser.add_argument("--workdir-name")
    parser.add_argument("--destroy", action="store_true")
    args = parser.parse_args()

    if not check_oci_sdk():
        print("OCI Python SDK is not installed. Install it with `pip install oci`.", file=sys.stderr)
        return 2

    config = load_oci_config(args.config_file, args.profile)
    import oci

    vcn_client = oci.core.VirtualNetworkClient(config)
    compute_client = oci.core.ComputeClient(config)

    priv, pub = make_ssh_keypair(Path("."), name=args.key_name)
    public_key_text = pub.read_text(encoding="utf-8").strip()
    print(f"Created SSH keypair: {priv} {pub}")

    vcn = get_or_create_vcn(vcn_client, args.compartment_id)
    igw = get_or_create_internet_gateway(vcn_client, args.compartment_id, vcn.id)
    rt = get_or_create_route_table(vcn_client, args.compartment_id, vcn.id, igw.id)
    sec = get_or_create_security_list(vcn_client, args.compartment_id, vcn.id)
    subnet = get_or_create_subnet(
        vcn_client,
        args.compartment_id,
        vcn.id,
        rt.id,
        sec.id,
        args.availability_domain,
    )

    image_id = args.image_id
    if not image_id:
        image_id = discover_image_id(compute_client, args.compartment_id)
        if not image_id:
            print("Unable to discover a suitable Oracle Linux image. Provide --image-id.", file=sys.stderr)
            return 1
        print(f"Discovered image OCID: {image_id}")

    instance = launch_instance(
        compute_client,
        args.compartment_id,
        args.availability_domain,
        args.shape,
        subnet.id,
        public_key_text,
        image_id,
    )
    print(f"Instance launched: {instance.id}")

    ip = get_instance_public_ip(compute_client, vcn_client, args.compartment_id, instance.id)
    if not ip:
        print("Unable to resolve the instance public IP.", file=sys.stderr)
        return 1
    print(f"Instance public IP: {ip}")

    runner_cmd = [
        sys.executable,
        str(REMOTE_RUNNER),
        "--host",
        ip,
        "--user",
        "opc",
        "--key",
        str(priv),
        "--project",
        args.project,
        "--repo-url",
        args.repo_url,
    ]
    if args.workdir_name:
        runner_cmd.extend(["--workdir-name", args.workdir_name])

    rc = subprocess.run(runner_cmd).returncode

    if args.destroy:
        print("Terminating instance...")
        compute_client.terminate_instance(instance.id)

    return rc


if __name__ == "__main__":
    raise SystemExit(main())
