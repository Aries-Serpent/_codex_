#!/usr/bin/env python3
"""
Canonicalize Artifacts

Purpose:
    Command-line utility (see argument parser for details)

Usage:
    python scripts/canonicalize_artifacts.py [options]
    
    Examples:
    $ python scripts/canonicalize_artifacts.py --help

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


import argparse
import logging
logger = logging.getLogger(__name__)
import hashlib
import json
import sys
from pathlib import Path

CANON_KEYS_DROP = {"generated", "timestamp"}


def sha256_b(s: bytes) -> str:
    return hashlib.sha256(s).hexdigest()


def canonicalize_json(p: Path) -> dict:
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(f"[ERR] Failed to parse {p}: {e}", file=sys.stderr)
        raise

    def scrub(obj):
        if isinstance(obj, dict):
            return {k: scrub(v) for k, v in sorted(obj.items()) if k not in CANON_KEYS_DROP}
        if isinstance(obj, list):
            return [scrub(v) for v in obj]
        return obj

    clean = scrub(data)
    blob = json.dumps(clean, sort_keys=True, separators=(",", ":")).encode()
    return {"name": p.name, "sha": sha256_b(blob)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--artifacts_dir", default="audit_artifacts", help="Directory with JSON artifacts"
    )
    ap.add_argument("--out", default="audit_artifacts/canonical_manifest.json")
    args = ap.parse_args()

    adir = Path(args.artifacts_dir)
    items = []
    if not adir.exists():
        print(f"[ERR] {adir} not found", file=sys.stderr)
        sys.exit(2)

    for p in sorted(adir.glob("*.json")):
        if p.name.startswith("_"):
            continue
        items.append(canonicalize_json(p))

    out = {"artifacts": items}
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
