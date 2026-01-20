#!/usr/bin/env python
"""
Synonym Loader

Purpose:
    Main execution script

Usage:
    python scripts/space_traversal/synonym_loader.py [options]
    
    Examples:
    $ python scripts/space_traversal/synonym_loader.py --help

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

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

# Capability Synonym Loader (P6)
#
# Expands found_patterns in capabilities_raw.json using a synonym map.
# Records map_hash for reproducibility.
#
# Synonym Map Format (JSON):
# {
#   "train": ["training", "epoch", "fit"],
#   "checkpoint": ["save_checkpoint", "restore", "load_checkpoint"],
#   "tokenizer": ["tokenize", "encode", "decode"]
# }
#
# Environment Knobs:
#   SYNONYM_MAP_PATH=configs/synonyms/synonyms.json  (default)
#
# Behavior:
# - Load capabilities_raw.json
# - For each capability, expand found_patterns via synonym map
# - Output capabilities_raw_expanded.json with synonym_count and map_hash
#
# Integration:
# - S3 can optionally use expanded version for richer pattern matching

import hashlib
import json
import os
import sys
from pathlib import Path

ART_DIR = Path("audit_artifacts")
RAW = ART_DIR / "capabilities_raw.json"
OUT = ART_DIR / "capabilities_raw_expanded.json"

DEFAULT_MAP_PATH = "configs/synonyms/synonyms.json"


def load_synonym_map(path: Path) -> dict[str, list[str]]:
    """Load synonym map JSON."""
    if not path.exists():
        return {}

    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        logger.debug(f"Exception: {e}")
        print(f"[WARN] Failed to load synonym map: {e}", file=sys.stderr)
        return {}


def expand_patterns(found: list[str], synonym_map: dict[str, list[str]]) -> set[str]:
    """Expand found patterns using synonym map."""
    expanded = set(found)

    for pattern in found:
        # Direct match
        if pattern in synonym_map:
            expanded.update(synonym_map[pattern])

        # Partial match (substring)
        for key, values in synonym_map.items():
            if key in pattern or pattern in key:
                expanded.update(values)

    return expanded


def compute_map_hash(synonym_map: dict) -> str:
    """Compute stable hash of synonym map."""
    canonical = json.dumps(synonym_map, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode()).hexdigest()[:16]


def main():
    map_path_str = os.getenv("SYNONYM_MAP_PATH", DEFAULT_MAP_PATH)
    map_path = Path(map_path_str)

    if not RAW.exists():
        print("[WARN] capabilities_raw.json missing; run S3 first.", file=sys.stderr)
        return 2

    synonym_map = load_synonym_map(map_path)
    if not synonym_map:
        print("[INFO] No synonym map loaded; passthrough mode.")
        # Passthrough: copy raw to expanded
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(RAW.read_text())
        return 0

    map_hash = compute_map_hash(synonym_map)
    data = json.loads(RAW.read_text())

    for cap in data.get("capabilities", []):
        found = cap.get("found_patterns", [])
        expanded = expand_patterns(found, synonym_map)

        cap["found_patterns_original"] = found
        cap["found_patterns"] = sorted(expanded)
        cap["synonym_expansion_count"] = len(expanded) - len(found)

    data["synonym_map_hash"] = map_hash
    data["synonym_count"] = sum(len(v) for v in synonym_map.values())

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(data, indent=2), encoding="utf-8")
    print(f"[INFO] Synonym expansion written: {OUT}")
    print(f"[INFO] Map hash: {map_hash}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
