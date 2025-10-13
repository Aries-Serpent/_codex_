"""Utilities for loading the Codex CRM canonical data model and platform mappings."""

from __future__ import annotations

import csv
import json
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

BASE = Path(__file__).resolve().parents[3]


@dataclass(slots=True)
class FieldDef:
    """Canonical field definition entry."""

    name: str
    key: str
    ftype: str
    required: bool
    choices: list[str]
    default: str | None = None


def _iter_csv(fp: Path) -> Iterable[dict[str, str]]:
    with fp.open(newline="", encoding="utf-8") as handle:
        yield from csv.DictReader(handle)


def load_cdm() -> dict[str, list[FieldDef]]:
    """Load canonical entities/fields from ``config/cdm/*.csv``."""

    cdm_dir = BASE / "config" / "cdm"
    if not cdm_dir.exists():
        raise FileNotFoundError(f"CDM directory not found: {cdm_dir}")

    model: dict[str, list[FieldDef]] = {}
    for csv_file in sorted(cdm_dir.glob("*.csv")):
        entity = csv_file.stem
        rows = list(_iter_csv(csv_file))
        model[entity] = [
            FieldDef(
                name=row["name"],
                key=row["key"],
                ftype=row["type"],
                required=row.get("required", "").strip().lower() == "true",
                choices=[c.strip() for c in (row.get("choices") or "").split("|") if c.strip()],
                default=(row.get("default") or None),
            )
            for row in rows
        ]
    return model


def load_mapping() -> dict[str, dict[str, str]]:
    """Load Zendesk↔D365 logical name mappings from ``config/mapping/*.csv``."""

    mapping_dir = BASE / "config" / "mapping"
    if not mapping_dir.exists():
        raise FileNotFoundError(f"Mapping directory not found: {mapping_dir}")

    mappings: dict[str, dict[str, str]] = {}
    for csv_file in sorted(mapping_dir.glob("*.csv")):
        rows = list(_iter_csv(csv_file))
        scope = csv_file.stem
        mappings[scope] = {row["cdm_key"]: row["platform_key"] for row in rows}
    return mappings


def load_json(fp: Path) -> Any:
    """Convenience wrapper for JSON files in config directories."""

    with fp.open(encoding="utf-8") as handle:
        return json.load(handle)
