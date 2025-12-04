#!/usr/bin/env python
"""Validate codex_capability_map.yaml structure.

This script checks that:
- The file exists and is valid YAML.
- The top-level 'capabilities' key is a mapping.
- Each capability has 'code'/'tests'/'docs' lists where present.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any, Dict, List

import yaml


def load_capability_map(path: Path) -> Dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(path)
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict):
        raise ValueError("capability YAML must be a mapping at top level")
    return data


def _ensure_list_or_missing(cap: Dict[str, Any], key: str) -> None:
    value = cap.get(key)
    if value is None:
        return
    if not isinstance(value, list):
        raise ValueError(f"capabilities.<cap>.{key} must be a list if present")


def validate_structure(data: Dict[str, Any]) -> None:
    caps = data.get("capabilities")
    if not isinstance(caps, dict):
        raise ValueError("capabilities must be a mapping of capability -> metadata")

    for name, meta in caps.items():
        if not isinstance(meta, dict):
            raise ValueError(f"capabilities[{name}] must be a mapping")
        _ensure_list_or_missing(meta, "code")
        _ensure_list_or_missing(meta, "tests")
        _ensure_list_or_missing(meta, "docs")


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate codex_capability_map.yaml.")
    parser.add_argument(
        "--path",
        type=str,
        default="codex_capability_map.yaml",
        help="Path to codex_capability_map.yaml (default: codex_capability_map.yaml)",
    )
    args = parser.parse_args(argv)
    path = Path(args.path).expanduser().resolve()
    data = load_capability_map(path)
    validate_structure(data)
    print(f"Capability map OK: {path}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
