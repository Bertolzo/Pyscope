"""Lightweight AWS CLI helper for provisioning a minimal EC2 fallback host.

This module is intended to be used by a provider-specific orchestrator that
creates an EC2 instance, imports an SSH key, and retrieves the public IP.
It does not attempt to manage IAM policies or complex networking.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path
from typing import List, Optional, Tuple


def _which(cmd: str) -> Optional[str]:
    return shutil.which(cmd)


def check_aws_cli() -> bool:
    return _which("aws") is not None


def _aws_args(region: Optional[str]) -> List[str]:
    return ["--region", region] if region else []


def _run(args: List[str], capture: bool = False) -> Tuple[int, str]:
    if capture:
        proc = subprocess.run(args, capture_output=True, text=True)
        return proc.returncode, (proc.stdout or "") + (proc.stderr or "")
    proc = subprocess.run(args)
    return proc.returncode, ""


def make_ssh_keypair(out_dir: Path, name: str = "aws_c1_key") -> Tuple[Path, Path]:
    priv = out_dir / name
    pub = out_dir / f"{name}.pub"
    if priv.exists() and pub.exists():
        return priv, pub
    subprocess.run(["ssh-keygen", "-t", "rsa", "-b", "2048", "-f", str(priv), "-N", ""], check=True)
    return priv, pub


def get_default_vpc_id(region: Optional[str] = None) -> Optional[str]:
    args = ["aws", *(_aws_args(region)), "ec2", "describe-vpcs", "--filters", "Name=isDefault,Values=true", "--query", "Vpcs[0].VpcId", "--output", "text"]
    rc, out = _run(args, capture=True)
    if rc != 0:
        return None
    return out.strip() or None


def create_security_group(vpc_id: str, group_name: str, description: str, region: Optional[str] = None) -> Optional[str]:
    args = ["aws", *(_aws_args(region)), "ec2", "create-security-group", "--group-name", group_name, "--description", description, "--vpc-id", vpc_id, "--query", "GroupId", "--output", "text"]
    rc, out = _run(args, capture=True)
    if rc == 0:
        return out.strip()
    if "InvalidGroup.Duplicate" in out:
        args = ["aws", *(_aws_args(region)), "ec2", "describe-security-groups", "--filters", "Name=group-name,Values=" + group_name, "Name=vpc-id,Values=" + vpc_id, "--query", "SecurityGroups[0].GroupId", "--output", "text"]
        rc2, out2 = _run(args, capture=True)
        if rc2 == 0:
            return out2.strip()
    return None


def authorize_security_group_ingress(group_id: str, cidr: str = "0.0.0.0/0", region: Optional[str] = None) -> bool:
    args = ["aws", *(_aws_args(region)), "ec2", "authorize-security-group-ingress", "--group-id", group_id, "--protocol", "tcp", "--port", "22", "--cidr", cidr]
    rc, _ = _run(args, capture=True)
    return rc == 0


def import_ssh_public_key(key_name: str, public_key_path: Path, region: Optional[str] = None) -> bool:
    args = ["aws", *(_aws_args(region)), "ec2", "import-key-pair", "--key-name", key_name, "--public-key-material", f"file://{public_key_path}"]
    rc, _ = _run(args, capture=True)
    return rc == 0


def create_instance(ami_id: str, instance_type: str, key_name: str, security_group_id: str, region: Optional[str] = None) -> Optional[str]:
    args = [
        "aws", *(_aws_args(region)), "ec2", "run-instances",
        "--image-id", ami_id,
        "--instance-type", instance_type,
        "--key-name", key_name,
        "--security-group-ids", security_group_id,
        "--tag-specifications", "ResourceType=instance,Tags=[{Key=Name,Value=c1-runner}]",
        "--query", "Instances[0].InstanceId",
        "--output", "text",
    ]
    rc, out = _run(args, capture=True)
    if rc != 0:
        return None
    return out.strip() or None


def get_instance_public_ip(instance_id: str, region: Optional[str] = None) -> Optional[str]:
    args = ["aws", *(_aws_args(region)), "ec2", "describe-instances", "--instance-ids", instance_id, "--query", "Reservations[0].Instances[0].PublicIpAddress", "--output", "text"]
    rc, out = _run(args, capture=True)
    if rc != 0:
        return None
    public_ip = out.strip()
    return public_ip if public_ip and public_ip != "None" else None


def terminate_instance(instance_id: str, region: Optional[str] = None) -> bool:
    args = ["aws", *(_aws_args(region)), "ec2", "terminate-instances", "--instance-ids", instance_id]
    rc, _ = _run(args, capture=True)
    return rc == 0


def discover_ami_id(instance_type: str = "t4g.nano", region: Optional[str] = None) -> Optional[str]:
    if instance_type.startswith("t4g"):
        parameter = "/aws/service/ami-amazon-linux-latest/amzn2-ami-hvm-arm64-gp2"
    else:
        parameter = "/aws/service/ami-amazon-linux-latest/amzn2-ami-hvm-x86_64-gp2"
    args = ["aws", *(_aws_args(region)), "ssm", "get-parameter", "--name", parameter, "--query", "Parameter.Value", "--output", "text"]
    rc, out = _run(args, capture=True)
    if rc != 0:
        return None
    return out.strip() or None


if __name__ == "__main__":
    print("AWS CLI provisioning helper. Use programmatically from a script.")
