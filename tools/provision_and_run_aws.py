#!/usr/bin/env python3
"""Provision an AWS EC2 fallback host and run C1 remotely using AWS CLI."""

from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path

from tools.providers.aws_cli import (
    check_aws_cli,
    create_instance,
    create_security_group,
    discover_ami_id,
    get_default_vpc_id,
    get_instance_public_ip,
    import_ssh_public_key,
    authorize_security_group_ingress,
    make_ssh_keypair,
    terminate_instance,
)

ROOT = Path(__file__).resolve().parent.parent
REMOTE_RUNNER = ROOT / "tools" / "remote_runner.py"


def build_commands(region: str | None, key_name: str, security_group_name: str, instance_type: str, ami_id: str | None, ssh_source_cidr: str) -> list[str]:
    commands: list[str] = []
    region_args = f"--region {region}" if region else ""
    commands.append(f"aws {region_args} ec2 describe-vpcs --filters Name=isDefault,Values=true --query 'Vpcs[0].VpcId' --output text")
    commands.append(f"aws {region_args} ec2 create-security-group --group-name {security_group_name} --description 'SSH access for c1-runner' --vpc-id <default-vpc-id> --query 'GroupId' --output text")
    commands.append(f"aws {region_args} ec2 authorize-security-group-ingress --group-id <security-group-id> --protocol tcp --port 22 --cidr {ssh_source_cidr}")
    commands.append(f"aws {region_args} ec2 import-key-pair --key-name {key_name} --public-key-material file://<path-to-public-key>")
    if ami_id:
        commands.append(f"aws {region_args} ec2 run-instances --image-id {ami_id} --instance-type {instance_type} --key-name {key_name} --security-group-ids <security-group-id> --tag-specifications 'ResourceType=instance,Tags=[{{Key=Name,Value=c1-runner}}]' --query 'Instances[0].InstanceId' --output text")
    else:
        commands.append("# Use --ami-id or let the script auto-discover one in execute mode.")
    return commands


def run_remote(project: str, repo_url: str, host_ip: str, ssh_user: str, ssh_key: Path, workdir_name: str | None) -> int:
    runner_cmd = [sys.executable, str(REMOTE_RUNNER), "--host", host_ip, "--user", ssh_user, "--key", str(ssh_key), "--project", project, "--repo-url", repo_url]
    if workdir_name:
        runner_cmd.extend(["--workdir-name", workdir_name])
    return subprocess.run(runner_cmd).returncode


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--region", help="AWS region to use")
    parser.add_argument("--instance-type", default="t4g.nano", help="EC2 instance type to launch")
    parser.add_argument("--ami-id", help="AMI ID to use for the instance")
    parser.add_argument("--key-name", default="aws_c1_key", help="Name of the AWS key pair")
    parser.add_argument("--security-group-name", default="c1-runner-sg", help="Name of the security group to create")
    parser.add_argument("--ssh-user", default="ec2-user", help="SSH username for the remote AMI")
    parser.add_argument("--ssh-source-cidr", default="0.0.0.0/0", help="CIDR allowed to SSH into the instance")
    parser.add_argument("--execute", action="store_true", help="Actually run the AWS CLI commands")
    parser.add_argument("--destroy", action="store_true", help="Terminate the instance after the remote run")
    parser.add_argument("--project", required=True)
    parser.add_argument("--repo-url", required=True)
    parser.add_argument("--workdir-name")
    args = parser.parse_args()

    if not check_aws_cli():
        print("aws CLI not found; install and configure it first.", file=sys.stderr)
        return 2

    priv, pub = make_ssh_keypair(Path("."), name=args.key_name)
    print(f"SSH keypair created: {priv} {pub}")

    if not args.execute:
        print("Dry-run AWS commands:")
        for command in build_commands(args.region, args.key_name, args.security_group_name, args.instance_type, args.ami_id, args.ssh_source_cidr):
            print("  ", command)
        print("Run with --execute to apply these commands.")
        return 0

    ami_id = args.ami_id
    if not ami_id:
        ami_id = discover_ami_id(args.instance_type, region=args.region)
        if not ami_id:
            print("Unable to auto-discover an AMI for the requested instance type.", file=sys.stderr)
            return 1
        print(f"Discovered AMI: {ami_id}")

    vpc_id = get_default_vpc_id(region=args.region)
    if not vpc_id:
        print("Unable to resolve the default VPC.", file=sys.stderr)
        return 1
    print(f"Default VPC ID: {vpc_id}")

    sg_id = create_security_group(vpc_id, args.security_group_name, "SSH access for c1-runner", region=args.region)
    if not sg_id:
        print("Unable to create or find the security group.", file=sys.stderr)
        return 1
    print(f"Security group ID: {sg_id}")

    if not authorize_security_group_ingress(sg_id, cidr=args.ssh_source_cidr, region=args.region):
        print("Unable to authorize SSH ingress.", file=sys.stderr)
        return 1
    print("SSH ingress authorized.")

    if not import_ssh_public_key(args.key_name, pub, region=args.region):
        print("Unable to import the SSH public key to AWS.", file=sys.stderr)
        return 1
    print("SSH key imported into AWS.")

    instance_id = create_instance(ami_id, args.instance_type, args.key_name, sg_id, region=args.region)
    if not instance_id:
        print("Failed to create EC2 instance.", file=sys.stderr)
        return 1
    print(f"Instance created: {instance_id}")

    ip = None
    for _ in range(60):
        ip = get_instance_public_ip(instance_id, region=args.region)
        if ip:
            break
        time.sleep(5)
    if not ip:
        print("Unable to retrieve public IP for instance.", file=sys.stderr)
        return 1
    print(f"Instance public IP: {ip}")

    rc = run_remote(args.project, args.repo_url, ip, args.ssh_user, priv, args.workdir_name)

    if args.destroy:
        print("Terminating instance...")
        if not terminate_instance(instance_id, region=args.region):
            print("Failed to terminate instance.", file=sys.stderr)
            return 1

    return rc


if __name__ == "__main__":
    raise SystemExit(main())
