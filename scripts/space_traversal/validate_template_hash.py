#!/usr/bin/env python
"""
Validate Template Hash

Purpose:
    Validates template_hash

Usage:
    python scripts/space_traversal/validate_template_hash.py [options]

    Examples:
    $ python scripts/space_traversal/validate_template_hash.py --help

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


import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def compute_template_hash(tpl_dir: Path) -> str:
    concat = b""
    for t in sorted(tpl_dir.glob("*.j2")):
        concat += t.read_bytes()
    return hashlib.sha256(concat).hexdigest()


def main():
    manifest_path = ROOT / "audit_run_manifest.json"
    if not manifest_path.exists():
        print("[WARN] Manifest not found. Run the audit pipeline first.")
        return
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    tpl_dir = ROOT / "templates" / "audit"
    live_hash = compute_template_hash(tpl_dir)
    manifest_hash = manifest.get("template_hash")
    if live_hash != manifest_hash:
        print(f"[WARN] Template hash mismatch!\n  live={live_hash}\n  manifest={manifest_hash}")
    else:
        print("[PASS] Template hash matches manifest.")


if __name__ == "__main__":
    main()
