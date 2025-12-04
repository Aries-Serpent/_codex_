#!/usr/bin/env python
"""Validate codex_ml_test_map.yaml structure.

Checks:
- File exists and is valid YAML.
- Top-level 'categories' key is a mapping.
- Each category has:
  - 'description' (string)
  - 'tests' (list of strings; can be empty)
"""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any, Dict, List

import yaml


def load_ml_test_map(path: Path) -> Dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(path)
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict):
        raise ValueError("ML test map YAML must be a mapping at top level")
    return data


def validate_structure(data: Dict[str, Any]) -> None:
    cats = data.get("categories")
    if not isinstance(cats, dict):
        raise ValueError("ML test map must contain a 'categories' mapping")

    for cat_name, meta in cats.items():
        if not isinstance(meta, dict):
            raise ValueError(f"categories[{cat_name}] must be a mapping")
        desc = meta.get("description")
        if not isinstance(desc, str):
            raise ValueError(f"categories[{cat_name}].description must be a string")
        tests = meta.get("tests")
        if tests is None:
            raise ValueError(
                f"categories[{cat_name}].tests must be present (can be empty list)"
            )
        if not isinstance(tests, list):
            raise ValueError(f"categories[{cat_name}].tests must be a list")
        for t in tests:
            if not isinstance(t, str):
                raise ValueError(
                    f"categories[{cat_name}].tests entries must be strings"
                )


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate codex_ml_test_map.yaml.")
    parser.add_argument(
        "--path",
        type=str,
        default="codex_ml_test_map.yaml",
        help="Path to ML test map YAML (default: codex_ml_test_map.yaml)",
    )
    args = parser.parse_args(argv)
    path = Path(args.path).expanduser().resolve()
    data = load_ml_test_map(path)
    validate_structure(data)
    print(f"ML test map OK: {path}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
