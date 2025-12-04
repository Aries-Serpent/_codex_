#!/usr/bin/env python
"""Validate codex_hardship.yaml structure.

This script checks that:
- The file exists and is valid YAML.
- The top-level 'gaps' key is a mapping.
- Each entry has a 'risk_level' string (optional but recommended).
- 'risk_level' is one of: low, medium, high.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any, Dict

import yaml


VALID_RISK_LEVELS = {"low", "medium", "high"}


def load_hardship(path: Path) -> Dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(path)
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict):
        raise ValueError("hardship YAML must be a mapping at top level")
    return data


def validate_structure(data: Dict[str, Any]) -> None:
    gaps = data.get("gaps")
    if not isinstance(gaps, dict):
        raise ValueError("hardship.gaps must be a mapping of gap_id -> metadata")

    for gid, meta in gaps.items():
        if not isinstance(meta, dict):
            raise ValueError(f"hardship.gaps[{gid}] must be a mapping")
        risk = meta.get("risk_level")
        if risk is not None and risk not in VALID_RISK_LEVELS:
            raise ValueError(
                f"hardship.gaps[{gid}].risk_level must be one of {sorted(VALID_RISK_LEVELS)}, "
                f"got {risk!r}"
            )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate codex_hardship.yaml.")
    parser.add_argument(
        "--path",
        type=str,
        default="codex_hardship.yaml",
        help="Path to codex_hardship.yaml (default: codex_hardship.yaml)",
    )
    args = parser.parse_args(argv)
    path = Path(args.path).expanduser().resolve()
    data = load_hardship(path)
    validate_structure(data)
    print(f"Hardship file OK: {path}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
