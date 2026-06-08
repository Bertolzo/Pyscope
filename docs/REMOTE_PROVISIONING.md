# Remote Provisioning Playbook (stratified)

This document is intentionally stratified: provider-specific automation is
separate from a general manual playbook. Follow the section that applies to
your chosen path.

## A. Provider-specific automation — Oracle Cloud (OCI CLI)

> Consulte também `docs/FALLBACK_PROTOCOL.md` para o protocolo de ativação
> de fallback remoto e para o comportamento esperado de `--fallback-if-insufficient`.


When you want a one-command provisioning flow and you're using Oracle Cloud
Always-Free, use the `oci` CLI and the provided orchestrator.

Prerequisites
- An Oracle Cloud account with Always-Free enabled.
- `oci` CLI installed and configured (`oci setup config`) with a profile that
  has permission to create VCNs, subnets and instances.
- SSH keypair available or allow the orchestrator to create one locally.

Steps
1. Create an OCI config and verify access:

```bash
oci os ns get
```

2. Identify a compartment OCID and an availability domain for your tenancy.
3. Run the orchestrator to generate commands (dry-run):

```bash
./.venv/bin/python tools/provision_and_run_oracle.py --compartment-id <COMPARTMENT_OCID> --availability-domain <AD> --project Django --repo-url https://github.com/django/django.git
```

4. Review the printed `oci` commands. If acceptable, re-run with `--execute`:

```bash
./.venv/bin/python tools/provision_and_run_oracle.py --compartment-id <COMPARTMENT_OCID> --availability-domain <AD> --project Django --repo-url https://github.com/django/django.git --execute
```

5. The script will prompt for the created instance OCID. Once provided it waits
   for a public IP, then uploads the workspace and runs the observation using
   the existing `tools/remote_runner.py` script.

6. Optionally, pass `--destroy` to terminate the instance after the run.

Security notes
- The orchestrator executes `oci` commands and will require credentials with
  significant privileges; run only on trusted workstations.

## B. Provider-specific automation — AWS EC2 (CLI)

> A alternativa AWS fornece uma rota free-tier/low-cost para fallback remoto
> usando `aws` CLI e `tools/provision_and_run_aws.py`.

When you want an EC2-based fallback host, use the `aws` CLI and the new AWS
orchestrator.

Prerequisites
- An AWS account with a region that supports the selected instance type.
- `aws` CLI installed and configured with credentials and a default region.
- `ssh-keygen` available locally.

Steps
1. Run the AWS orchestrator in dry-run mode first:

```bash
./.venv/bin/python tools/provision_and_run_aws.py --project Django --repo-url https://github.com/django/django.git
```

2. If you need a specific region, instance type, or AMI, pass:

```bash
./.venv/bin/python tools/provision_and_run_aws.py --region us-east-1 --instance-type t4g.nano --project Django --repo-url https://github.com/django/django.git
```

3. When ready, re-run with `--execute`:

```bash
./.venv/bin/python tools/provision_and_run_aws.py --execute --project Django --repo-url https://github.com/django/django.git
```

4. The script will:
   - create or reuse a security group with SSH access,
   - import the generated SSH public key into AWS,
   - launch the EC2 instance,
   - wait for its public IP,
   - upload the workspace and execute the C1 observation remotely.

5. Optionally pass `--destroy` to terminate the instance after the run.

Security notes
- The AWS flow opens SSH access to the selected CIDR range.
- Use `--ssh-source-cidr` to restrict access to a safer IP range.

## D. Provider-specific automation — OCI SDK

> Use this flow when you want pure Python SDK provisioning instead of
> executing `oci` CLI commands.

Prerequisites
- `pip install oci`
- OCI config file in `~/.oci/config` and a profile with permissions to create
  network and compute resources.
- A compartment OCID and availability domain.

Steps
1. Run the SDK-based orchestrator in dry-run mode first:

```bash
./.venv/bin/python tools/provision_and_run_oci_sdk.py --help
```

2. Execute provisioning with your compartment and availability domain:

```bash
./.venv/bin/python tools/provision_and_run_oci_sdk.py --compartment-id <COMPARTMENT_OCID> --availability-domain <AD> --project Django --repo-url https://github.com/django/django.git
```

3. The script will create the minimal VCN, subnet, internet gateway, route
   table, security list, and instance, then upload the workspace and run the
   observation.

4. Provide `--image-id` if the auto-discovery cannot resolve a suitable image.

5. Optionally pass `--destroy` to terminate the instance after the run.

Security notes
- The OCI SDK flow creates network resources automatically; inspect your OCI
  console to reclaim or audit them later.

## C. Manual provisioning playbook (generic)

If you prefer not to use provider APIs, follow this reproducible manual flow.

1. Choose a provider and create a free-tier VM (example providers: Oracle,
   AWS Free Tier EC2 t4g.nano, Google Cloud f1-micro (always-free in some
   regions), Fly.io, Railway).
2. Create an SSH keypair locally and add the public key to the VM user.
3. On the remote VM:
   - install Python 3.10+ and `gcc` toolchain if needed
   - clone the repository (or upload the tarball created by `tools/remote_runner`)
   - create a virtualenv and install minimal dependencies:

```bash
python3 -m venv venv
. venv/bin/activate
pip install --upgrade pip
pip install networkx typer rich pydantic
```

4. Run the C1 observation inside the remote VM (use streaming mode):

```bash
# from repository root on remote
. venv/bin/activate
python tools/c1_observe.py Django https://github.com/django/django.git c1_django_remote
```

5. After completion, copy the produced `c1_django_remote_result.json` back to
   your workstation for analysis.

See `docs/PROVISIONING_PLAYBOOK.md` for an explicit shell and Ansible
playbook that implement the remote upload and execution flow.

## Quick commands using `tools/remote_runner.py`

Upload and run remote (ssh key-based):

```bash
./.venv/bin/python tools/remote_runner.py --host <IP> --user ubuntu --key /path/to/key --project Django --repo-url https://github.com/django/django.git --workdir-name c1_django_remote
```

Or use the Oracle-specific orchestrator (see A) to provision + run in one flow.

---

Keep stratified: provider-specific automation (A) is for users with configured
cloud CLI and comfortable granting programmatic permissions. Manual playbook
(B) is for users who want full manual control and auditability.
