"""Utilities for loading the Codex CRM canonical data model and platform mappings."""

from __future__ import annotations

import csv
import json
from collections.abc import Iterable
from dataclasses import dataclass
from importlib import resources
from importlib.abc import Traversable
from pathlib import Path
from typing import Any, TextIO, cast


@dataclass(slots=True)
class FieldDef:
    """Canonical field definition entry."""

    name: str
    key: str
    ftype: str
    required: bool
    choices: list[str]
    default: str | None = None


def _iter_csv(resource: Traversable) -> Iterable[dict[str, str]]:
    with resource.open("r", encoding="utf-8") as handle:
        text_handle = cast(TextIO, handle)
        yield from csv.DictReader(text_handle)
def _iter_csv_directory(subdir: str) -> Iterable[Traversable]:
    """Yield CSV resources bundled under ``cdm/data/<subdir>``."""

    data_root = resources.files(__package__) / "data" / subdir
    if not data_root.is_dir():
        raise FileNotFoundError(f"Expected data directory not found: {data_root}")

    return (
        resource
        for resource in sorted(
            data_root.iterdir(),
            key=lambda traversable: traversable.name,
        )
        if resource.name.endswith(".csv")
    )


def load_cdm() -> dict[str, list[FieldDef]]:
    """Load canonical entities/fields from packaged ``cdm/*.csv`` resources."""

    model: dict[str, list[FieldDef]] = {}
    for csv_file in _iter_csv_directory("cdm"):
        entity = Path(csv_file.name).stem
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
    """Load Zendesk↔D365 logical name mappings from packaged ``mapping/*.csv`` resources."""

    mappings: dict[str, dict[str, str]] = {}
    for csv_file in _iter_csv_directory("mapping"):
        rows = list(_iter_csv(csv_file))
        scope = Path(csv_file.name).stem
        mappings[scope] = {row["cdm_key"]: row["platform_key"] for row in rows}
    return mappings


def load_json(fp: Path) -> Any:
    """Convenience wrapper for JSON files in config directories."""

    with fp.open(encoding="utf-8") as handle:
        return json.load(handle)
