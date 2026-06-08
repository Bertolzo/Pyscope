# Provisioning Playbook — Shell and Ansible

This document provides a reproducible provisioning playbook for remote C1
execution, with both a shell script pattern and an Ansible playbook example.
It is meant to complement `docs/REMOTE_PROVISIONING.md` and the provider-specific
automation scripts.

## Goal

- Provision or prepare a remote host for C1 observation.
- Upload the local repository workspace.
- Create a Python virtual environment on the remote host.
- Install minimal runtime dependencies.
- Run `tools/c1_observe.py` remotely.
- Optionally retrieve the result back to the local machine.

## Shell Playbook

This shell playbook is a minimal reproducible flow for an existing remote host.
It assumes the remote machine already exists and accepts SSH key authentication.

```bash
#!/usr/bin/env bash
set -euo pipefail

HOST=${HOST:-"<REMOTE_IP>"}
USER=${USER:-"ubuntu"}
SSH_KEY=${SSH_KEY:-"~/.ssh/id_rsa"}
REMOTE_DIR=${REMOTE_DIR:-"/tmp/c1_remote"}
PROJECT=${PROJECT:-"Django"}
REPO_URL=${REPO_URL:-"https://github.com/django/django.git"}
WORKDIR_NAME=${WORKDIR_NAME:-"c1_django_remote"}

# Create workspace tarball excluding local virtualenv and VCS metadata
TARBALL=$(mktemp --suffix=.tar.gz)

tar --exclude='.venv' --exclude='venv' --exclude='.git' --exclude='tests' --exclude='dist' --exclude='build' -czf "$TARBALL" .

echo "Uploading workspace to $USER@$HOST:$REMOTE_DIR"
scp -i "$SSH_KEY" -o StrictHostKeyChecking=no "$TARBALL" "$USER@$HOST:$REMOTE_DIR/workspace.tar.gz"

ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no "$USER@$HOST" bash -lc '
set -e
mkdir -p "$REMOTE_DIR"
cd "$REMOTE_DIR"
tar -xzf workspace.tar.gz
python3 -m venv venv
. venv/bin/activate
pip install --upgrade pip
pip install networkx typer rich pydantic
export PYTHONPATH="$(pwd)":$PYTHONPATH
venv/bin/python tools/c1_observe.py "'$PROJECT'" "'$REPO_URL'" "'$WORKDIR_NAME'"
'

rm -f "$TARBALL"

echo "Remote run finished. Retrieve result from $USER@$HOST:$REMOTE_DIR/$WORKDIR_NAME"
```

### Notes

- Adjust `USER`, `SSH_KEY`, and `REMOTE_DIR` to match your remote host.
- If the remote host uses a different Python command, replace `python3` with
  the appropriate interpreter.
- This shell playbook is an explicit, auditable way to run the remote job
  without provider-specific automation.

## Ansible Playbook

Use this Ansible playbook when you want a declarative remote runtime setup.
It assumes the remote host is reachable via SSH and `ansible-playbook` is
installed locally.

### Inventory file

Create `inventory.ini`:

```ini
[remote]
<REMOTE_IP> ansible_user=ubuntu ansible_ssh_private_key_file=~/.ssh/id_rsa
```

### Playbook file

Create `provision_c1.yml`:

```yaml
- name: Provision remote host and run C1 observation
  hosts: remote
  gather_facts: false
  vars:
    workspace_tarball: /tmp/workspace_package.tar.gz
    remote_workspace: /tmp/c1_remote
    project: Django
    repo_url: https://github.com/django/django.git
    workdir_name: c1_django_remote

  tasks:
    - name: Create remote workspace directory
      ansible.builtin.file:
        path: "{{ remote_workspace }}"
        state: directory
        mode: '0755'

    - name: Upload repository workspace tarball
      ansible.builtin.archive:
        path: .
        dest: "{{ workspace_tarball }}"
        exclude_path:
          - .venv
          - venv
          - .git
          - tests
          - dist
          - build
      delegate_to: localhost

    - name: Copy workspace tarball to remote host
      ansible.builtin.copy:
        src: "{{ workspace_tarball }}"
        dest: "{{ workspace_tarball }}"
        mode: '0644'

    - name: Extract workspace tarball on remote host
      ansible.builtin.unarchive:
        src: "{{ workspace_tarball }}"
        dest: "{{ remote_workspace }}"
        remote_src: true

    - name: Ensure Python virtualenv is present
      ansible.builtin.command:
        cmd: python3 -m venv venv
        chdir: "{{ remote_workspace }}"
      args:
        creates: "{{ remote_workspace }}/venv/bin/activate"

    - name: Install minimal runtime dependencies
      ansible.builtin.shell: |
        . venv/bin/activate
        pip install --upgrade pip
        pip install networkx typer rich pydantic
      args:
        chdir: "{{ remote_workspace }}"

    - name: Run C1 observation on remote host
      ansible.builtin.shell: |
        . venv/bin/activate
        export PYTHONPATH="{{ remote_workspace }}:$PYTHONPATH"
        venv/bin/python tools/c1_observe.py "{{ project }}" "{{ repo_url }}" "{{ workdir_name }}"
      args:
        chdir: "{{ remote_workspace }}"
```

### Execute the playbook

```bash
ansible-playbook -i inventory.ini provision_c1.yml
```

### Notes

- This Ansible playbook is intentionally user-controlled and auditable.
- It avoids provider automation and is suitable for any SSH-accessible host.
- If you already have `tools/remote_runner.py`, you can use it instead of the
  Ansible flow for a simpler upload-and-run path.

## Cross-reference

This playbook is a companion to `docs/REMOTE_PROVISIONING.md`.
Use the provider-specific automation flows there when you want AWS CLI,
OCI CLI, or OCI SDK provisioning.
