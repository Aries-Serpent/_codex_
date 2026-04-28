#!/usr/bin/env python3
"""
Validate Inventory Paths

Purpose:
    Validates inventory_paths

Usage:
    python scripts/remediation/validate_inventory_paths.py [options]

    Examples:
    $ python scripts/remediation/validate_inventory_paths.py --help

Arguments:
    [To be documented]

Environment Variables:
    [To be documented]

Dependencies:
    [To be documented]

Exit Codes:
    0: Success
    1: Error

Author: Codex Team
Last Updated: 2026-01-16
"""


import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
INVENTORY = ROOT / ".github" / "SHIM_INVENTORY.yaml"


def main():
    if not INVENTORY.exists():
        print(f"[ERROR] Inventory file not found: {INVENTORY}")
        sys.exit(1)

    doc = yaml.safe_load(INVENTORY.read_text(encoding="utf-8"))
    missing = []

    for item in doc.get("inventory", []):
        module = item.get("module", "unknown")
        for path_field in ("legacy_path", "canonical_path"):
            path_str = item.get(path_field)
            if path_str and path_str.strip():  # Non-empty path
                full_path = ROOT / path_str
                if not full_path.exists():
                    missing.append((module, path_field, path_str))

    if missing:
        print("[ERROR] Missing inventory paths:")
        for module, field, path in missing:
            print(f"  - {module}.{field}: {path}")
        sys.exit(1)

    print(f"[OK] Inventory path validation PASS ({len(doc.get('inventory', []))} modules checked)")
    sys.exit(0)


if __name__ == "__main__":
    main()
