"""Config-as-data emitters for Dynamics 365 administrators."""

from __future__ import annotations

import csv
from pathlib import Path

from codex_crm.cdm.loader import FieldDef, load_cdm


def emit_d365_config(out_dir: str) -> None:
    """Emit CSV artifacts describing tables, columns, and SLA targets."""

    cdm = load_cdm()
    output = Path(out_dir)
    output.mkdir(parents=True, exist_ok=True)

    _write_tables(output)
    _write_columns(output, cdm["assignment"])
    _write_slas(output)


def _write_tables(out: Path) -> None:
    with (out / "tables.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["table", "logical_name", "display_name"])
        writer.writerow(["cdx_assignment", "cdx_assignment", "Assignment"])


def _write_columns(out: Path, fields: list[FieldDef]) -> None:
    with (out / "columns.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["table", "logical_name", "display_name", "type", "required", "optionset"])
        for field in fields:
            options = ";".join(field.choices) if field.choices else ""
            writer.writerow(
                [
                    "cdx_assignment",
                    _d365_key(field.key),
                    field.name,
                    _map_type(field.ftype),
                    "Yes" if field.required else "No",
                    options,
                ]
            )


def _write_slas(out: Path) -> None:
    with (out / "slas.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["name", "target", "pause_conditions"])
        writer.writerow(["cdx_assignment_standard", "first_response", "status:paused"])


def _d365_key(cdm_key: str) -> str:
    return cdm_key.replace("codex_", "cdx_")


def _map_type(field_type: str) -> str:
    mapping = {
        "integer": "Integer",
        "choice": "Choice",
        "lookup": "Lookup",
    }
    return mapping.get(field_type, "Text")
