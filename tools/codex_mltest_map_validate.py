"""Validation helper for codex_ml_test_map.yaml."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


def load_ml_test_map(path: Path) -> dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def validate_structure(data: dict[str, Any]) -> None:
    if not isinstance(data, dict):
        raise ValueError("ML test map must be a mapping")
    categories = data.get("categories")
    if not isinstance(categories, dict):
        raise ValueError("`categories` must be a mapping")
    for name, entry in categories.items():
        if not isinstance(entry, dict):
            raise ValueError(f"Category {name} must be a mapping")
        tests = entry.get("tests")
        if not isinstance(tests, list):
            raise ValueError(f"Category {name} must contain a list of tests")
