"""Config-as-data emitters for Zendesk administrators."""

from __future__ import annotations

import json
from pathlib import Path

from codex_crm.cdm.loader import FieldDef, load_cdm, load_mapping


def emit_zendesk_config(out_dir: str) -> None:
    """Materialise JSON config artifacts derived from the CDM."""

    cdm = load_cdm()
    mappings = load_mapping()

    output = Path(out_dir)
    output.mkdir(parents=True, exist_ok=True)

    forms = [_assignment_form(cdm["assignment"])]
    (output / "forms.json").write_text(_dump_json(forms), encoding="utf-8")

    trigger = {
        "title": "codex_assignment_auto_route",
        "conditions": {
            "all": [
                {"field": "ticket_form_id", "operator": "is", "value": "Assignment"},
            ]
        },
        "actions": [
            {"field": "group_id", "value": "Relocation_Counselors"},
        ],
    }
    (output / "triggers.json").write_text(_dump_json([trigger]), encoding="utf-8")

    sla = {
        "title": "codex_assignment_standard",
        "policy": {"priority_targets": {"normal": {"response": 3_600, "resolution": 28_800}}},
    }
    (output / "sla.json").write_text(_dump_json([sla]), encoding="utf-8")

    (output / "mappings.json").write_text(_dump_json(mappings), encoding="utf-8")


def _assignment_form(fields: list[FieldDef]) -> dict[str, object]:
    return {
        "title": "Assignment",
        "fields": [
            {
                "id": field.key,
                "type": field.ftype,
                "required": field.required,
            }
            for field in fields
        ],
    }


def _dump_json(payload: object) -> str:
    return json.dumps(payload, indent=2, sort_keys=True)
