#!/usr/bin/env python3
"""Interactive MCP provider registry tool.

Usage:
  python tools/mcp_register.py --list
  python tools/mcp_register.py --interactive
  python tools/mcp_register.py --register <name>

This tool reads `tools/mcp_providers.json` for known providers and can
register them locally by writing to `~/.config/ags/mcp_registry.json`.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

REGISTRY_PATH = Path.home() / ".config" / "ags" / "mcp_registry.json"
PROVIDERS_FILE = Path(__file__).resolve().parent / "mcp_providers.json"


def load_providers() -> List[Dict[str, Any]]:
    try:
        with open(PROVIDERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def ensure_registry_dir() -> None:
    REGISTRY_PATH.parent.mkdir(parents=True, exist_ok=True)


def save_registry(entry: Dict[str, Any]) -> None:
    ensure_registry_dir()
    data = []
    if REGISTRY_PATH.exists():
        try:
            data = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
        except Exception:
            data = []
    data.append(entry)
    REGISTRY_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")


def list_providers() -> None:
    provs = load_providers()
    if not provs:
        print("No MCP providers configured in tools/mcp_providers.json")
        return
    print("Known MCP providers:")
    for p in provs:
        print(f"- {p.get('name')} ({p.get('provider')}) -> {p.get('url')}")


def interactive() -> None:
    provs = load_providers()
    if not provs:
        print("No providers to show.")
        return
    print("Interactive MCP registration")
    for i, p in enumerate(provs, start=1):
        print(f"[{i}] {p.get('name')} - {p.get('description')}")
    sel = input("Choose provider number to register (or 'q' to quit): ").strip()
    if sel.lower() == "q":
        print("Aborted")
        return
    try:
        idx = int(sel) - 1
        if idx < 0 or idx >= len(provs):
            print("Invalid selection")
            return
    except Exception:
        print("Invalid input")
        return
    p = provs[idx]
    print(f"Selected: {p.get('name')} -> {p.get('url')}")
    token = None
    if p.get('notes') and 'token' in p.get('notes').lower():
        token = input("Enter bearer token (or leave blank): ").strip() or None
    # Simulate registration
    entry = {
        "name": p.get('name'),
        "provider": p.get('provider'),
        "url": p.get('url'),
        "registered_at": __import__('datetime').datetime.utcnow().isoformat(),
        "auth": {"bearer": token} if token else None,
    }
    save_registry(entry)
    print(f"Provider {p.get('name')} registered locally in {REGISTRY_PATH}")


def register_by_name(name: str) -> None:
    provs = load_providers()
    for p in provs:
        if p.get('name') == name:
            entry = {
                "name": p.get('name'),
                "provider": p.get('provider'),
                "url": p.get('url'),
                "registered_at": __import__('datetime').datetime.utcnow().isoformat(),
                "auth": None,
            }
            save_registry(entry)
            print(f"Registered {name} -> {p.get('url')} in {REGISTRY_PATH}")
            return
    print(f"Provider named {name} not found in providers file.")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--list", action="store_true")
    parser.add_argument("--interactive", action="store_true")
    parser.add_argument("--register", help="Register provider by exact name")
    args = parser.parse_args()

    if args.list:
        list_providers()
        return 0
    if args.interactive:
        interactive()
        return 0
    if args.register:
        register_by_name(args.register)
        return 0

    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
