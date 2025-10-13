from __future__ import annotations

import csv
import pathlib
from dataclasses import dataclass

BASE = pathlib.Path(__file__).resolve().parents[3]


@dataclass
class FieldDef:
    """Representation of a canonical data model field."""

    name: str
    key: str
    ftype: str
    required: bool
    choices: list[str]
    default: str | None = None


def load_csv(fp: pathlib.Path) -> list[dict[str, str]]:
    """Load a CSV file and return the rows as dictionaries."""

    with fp.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def load_cdm() -> dict[str, list[FieldDef]]:
    """Load canonical entities and fields from ``config/cdm``."""

    cdm_dir = BASE / "config" / "cdm"
    model: dict[str, list[FieldDef]] = {}
    if not cdm_dir.exists():
        return model

    for csv_file in cdm_dir.glob("*.csv"):
        entity = csv_file.stem
        rows = load_csv(csv_file)
        fields = [
            FieldDef(
                name=row["name"],
                key=row["key"],
                ftype=row["type"],
                required=row.get("required", "").strip().lower() == "true",
                choices=[
                    choice.strip()
                    for choice in (row.get("choices") or "").split("|")
                    if choice.strip()
                ],
                default=(row.get("default") or None),
            )
            for row in rows
        ]
        model[entity] = fields
    return model


def load_mapping() -> dict[str, dict[str, str]]:
    """Load Zendesk and Dynamics mapping files from ``config/mapping``."""

    mapping_dir = BASE / "config" / "mapping"
    if not mapping_dir.exists():
        return {}

    mappings: dict[str, dict[str, str]] = {}
    for csv_file in mapping_dir.glob("*.csv"):
        rows = load_csv(csv_file)
        scope = csv_file.stem
        mappings[scope] = {row["cdm_key"]: row["platform_key"] for row in rows}
    return mappings
