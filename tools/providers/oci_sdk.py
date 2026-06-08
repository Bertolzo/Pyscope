"""Lightweight OCI Python SDK helper for provisioning a minimal compute host.

This helper creates a VCN, subnet, internet gateway, route table, security
list and a public compute instance. It is intended for fallback execution
when a local host is too weak for heavy C1 jobs.
"""

from __future__ import annotations

import json
import os
import random
import shutil
import string
import subprocess
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


def _which(cmd: str) -> Optional[str]:
    return shutil.which(cmd)


def check_oci_sdk() -> bool:
    try:
        import oci  # noqa: F401
        return True
    except ImportError:
        return False


def load_oci_config(config_file: Optional[str] = None, profile: str = "DEFAULT") -> Dict[str, Any]:
    import oci

    return oci.config.from_file(config_file, profile)


def make_ssh_keypair(out_dir: Path, name: str = "oci_key") -> Tuple[Path, Path]:
    priv = out_dir / name
    pub = out_dir / f"{name}.pub"
    if priv.exists() and pub.exists():
        return priv, pub
    subprocess.run(["ssh-keygen", "-t", "rsa", "-b", "2048", "-f", str(priv), "-N", ""], check=True)
    return priv, pub


def _random_label(length: int = 6) -> str:
    return "".join(random.choice(string.ascii_lowercase + string.digits) for _ in range(length))


def get_or_create_vcn(virtual_network_client: Any, compartment_id: str, display_name: str = "c1-vcn") -> Any:
    import oci

    vcn_list = virtual_network_client.list_vcns(compartment_id=compartment_id, display_name=display_name).data
    if vcn_list:
        return vcn_list[0]
    details = oci.core.models.CreateVcnDetails(
        compartment_id=compartment_id,
        cidr_block="10.0.0.0/16",
        display_name=display_name,
        dns_label=f"{display_name.replace('-', '')}{_random_label(4)}",
    )
    resp = virtual_network_client.create_vcn(details)
    vcn = resp.data
    _wait_for_lifecycle(virtual_network_client.get_vcn, vcn.id)
    return vcn


def get_or_create_internet_gateway(virtual_network_client: Any, compartment_id: str, vcn_id: str, display_name: str = "c1-igw") -> Any:
    import oci

    gateways = virtual_network_client.list_internet_gateways(compartment_id=compartment_id, vcn_id=vcn_id, display_name=display_name).data
    if gateways:
        return gateways[0]
    details = oci.core.models.CreateInternetGatewayDetails(
        compartment_id=compartment_id,
        is_enabled=True,
        vcn_id=vcn_id,
        display_name=display_name,
    )
    resp = virtual_network_client.create_internet_gateway(details)
    gw = resp.data
    _wait_for_lifecycle(virtual_network_client.get_internet_gateway, gw.id)
    return gw


def get_or_create_route_table(virtual_network_client: Any, compartment_id: str, vcn_id: str, internet_gateway_id: str, display_name: str = "c1-rt") -> Any:
    import oci

    tables = virtual_network_client.list_route_tables(compartment_id=compartment_id, vcn_id=vcn_id, display_name=display_name).data
    if tables:
        return tables[0]
    rule = oci.core.models.RouteRule(
        cidr_block="0.0.0.0/0",
        network_entity_id=internet_gateway_id,
    )
    details = oci.core.models.CreateRouteTableDetails(
        compartment_id=compartment_id,
        display_name=display_name,
        vcn_id=vcn_id,
        route_rules=[rule],
    )
    resp = virtual_network_client.create_route_table(details)
    rt = resp.data
    _wait_for_lifecycle(virtual_network_client.get_route_table, rt.id)
    return rt


def get_or_create_security_list(virtual_network_client: Any, compartment_id: str, vcn_id: str, display_name: str = "c1-sec-list") -> Any:
    import oci

    lists = virtual_network_client.list_security_lists(compartment_id=compartment_id, vcn_id=vcn_id, display_name=display_name).data
    if lists:
        return lists[0]
    ingress = oci.core.models.IngressSecurityRule(
        protocol="6",
        source="0.0.0.0/0",
        tcp_options=oci.core.models.TcpOptions(destination_port_range=oci.core.models.PortRange(min=22, max=22)),
    )
    details = oci.core.models.CreateSecurityListDetails(
        compartment_id=compartment_id,
        display_name=display_name,
        vcn_id=vcn_id,
        ingress_security_rules=[ingress],
    )
    resp = virtual_network_client.create_security_list(details)
    sec = resp.data
    _wait_for_lifecycle(virtual_network_client.get_security_list, sec.id)
    return sec


def get_or_create_subnet(virtual_network_client: Any, compartment_id: str, vcn_id: str, route_table_id: str, security_list_id: str, availability_domain: str, display_name: str = "c1-subnet") -> Any:
    import oci

    subnets = virtual_network_client.list_subnets(compartment_id=compartment_id, vcn_id=vcn_id, display_name=display_name).data
    if subnets:
        return subnets[0]
    details = oci.core.models.CreateSubnetDetails(
        compartment_id=compartment_id,
        availability_domain=availability_domain,
        display_name=display_name,
        vcn_id=vcn_id,
        cidr_block="10.0.1.0/24",
        route_table_id=route_table_id,
        security_list_ids=[security_list_id],
        prohibit_public_ip_on_vnic=False,
    )
    resp = virtual_network_client.create_subnet(details)
    subnet = resp.data
    _wait_for_lifecycle(virtual_network_client.get_subnet, subnet.id)
    return subnet


def discover_image_id(compute_client: Any, compartment_id: str, os_name: str = "Oracle Linux", version_keyword: str = "8") -> Optional[str]:
    images = compute_client.list_images(compartment_id, operating_system=os_name).data
    candidates = [img for img in images if version_keyword in (img.display_name or "") or version_keyword in (getattr(img, "version", "") or "")]
    if not candidates:
        return None
    candidates.sort(key=lambda img: getattr(img, "time_created", ""), reverse=True)
    return candidates[0].id


def launch_instance(
    compute_client: Any,
    compartment_id: str,
    availability_domain: str,
    shape: str,
    subnet_id: str,
    ssh_public_key: str,
    image_id: str,
    display_name: str = "c1-runner",
) -> Any:
    import oci

    create_vnic = oci.core.models.InstanceCreateVnicDetails(
        subnet_id=subnet_id,
        assign_public_ip=True,
    )
    source_details = oci.core.models.InstanceSourceViaImageDetails(image_id=image_id)
    details = oci.core.models.LaunchInstanceDetails(
        compartment_id=compartment_id,
        availability_domain=availability_domain,
        shape=shape,
        display_name=display_name,
        create_vnic_details=create_vnic,
        metadata={"ssh_authorized_keys": ssh_public_key.strip()},
        source_details=source_details,
    )
    resp = compute_client.launch_instance(details)
    instance = resp.data
    _wait_for_lifecycle(compute_client.get_instance, instance.id)
    return instance


def get_instance_public_ip(compute_client: Any, virtual_network_client: Any, compartment_id: str, instance_id: str) -> Optional[str]:
    vnic_attachments = compute_client.list_vnic_attachments(compartment_id=compartment_id, instance_id=instance_id).data
    if not vnic_attachments:
        return None
    for attachment in vnic_attachments:
        vnic = virtual_network_client.get_vnic(attachment.vnic_id).data
        if vnic.public_ip:
            return vnic.public_ip
    return None


def terminate_instance(compute_client: Any, instance_id: str) -> bool:
    compute_client.terminate_instance(instance_id)
    return True


def _wait_for_lifecycle(getter: Any, resource_id: str, timeout: int = 300) -> None:
    start = time.time()
    while True:
        resp = getter(resource_id)
        data = resp.data
        state = getattr(data, "lifecycle_state", None)
        if state == "AVAILABLE" or state == "TERMINATED" or state == "TERMINATING":
            return
        if time.time() - start > timeout:
            raise RuntimeError(f"timeout waiting for resource {resource_id}")
        time.sleep(5)


if __name__ == "__main__":
    print("OCI SDK helper module. Use from scripts, not directly.")
