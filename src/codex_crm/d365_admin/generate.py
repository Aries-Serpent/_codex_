from __future__ import annotations

import csv
import pathlib

from codex_crm.cdm.loader import FieldDef, load_cdm, load_mapping

_TABLE_NAME = "cdx_assignment"


def _map_type(field_type: str) -> str:
    return {"integer": "Integer", "choice": "Choice", "lookup": "Lookup"}.get(field_type, "Text")


def _assignment_columns(
    cdm_fields: list[FieldDef], mapping: dict[str, str]
) -> list[tuple[str, str, str, str, str, str]]:
    rows: list[tuple[str, str, str, str, str, str]] = []
    for field in cdm_fields:
        logical_name = mapping.get(field.key, field.key.replace("codex_", "cdx_"))
        rows.append(
            (
                _TABLE_NAME,
                logical_name,
                field.name,
                _map_type(field.ftype),
                "Yes" if field.required else "No",
                ";".join(field.choices),
            )
        )
    return rows


def emit_d365_config(out_dir: str) -> None:
    """Emit CSV configuration scaffolds for Dynamics 365."""

    cdm = load_cdm()
    mappings = load_mapping()
    assignment_fields = cdm.get("assignment", [])
    assignment_map = mappings.get("assignment_d365", {})

    output = pathlib.Path(out_dir)
    output.mkdir(parents=True, exist_ok=True)

    with (output / "tables.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["table", "logical_name", "display_name"])
        writer.writerow([_TABLE_NAME, _TABLE_NAME, "Assignment"])

    with (output / "columns.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(
            [
                "table",
                "logical_name",
                "display_name",
                "type",
                "required",
                "optionset",
            ]
        )
        for row in _assignment_columns(assignment_fields, assignment_map):
            writer.writerow(list(row))

    with (output / "slas.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["name", "target", "pause_conditions"])
        writer.writerow(["cdx_assignment_standard", "first_response", "status:paused"])
