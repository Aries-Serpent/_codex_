from __future__ import annotations

import json
import pathlib

from codex_crm.cdm.loader import FieldDef, load_cdm, load_mapping


def _assignment_fields(
    cdm_fields: list[FieldDef], mapping: dict[str, str]
) -> list[dict[str, object]]:
    fields: list[dict[str, object]] = []
    for field in cdm_fields:
        platform_key = mapping.get(field.key, field.key)
        fields.append(
            {
                "id": platform_key,
                "type": field.ftype,
                "required": field.required,
            }
        )
    return fields


def emit_zendesk_config(out_dir: str) -> None:
    """Emit JSON configuration scaffolds for Zendesk."""

    cdm = load_cdm()
    mappings = load_mapping()
    assignment_fields = _assignment_fields(
        cdm.get("assignment", []), mappings.get("assignment_zendesk", {})
    )

    output = pathlib.Path(out_dir)
    output.mkdir(parents=True, exist_ok=True)

    forms = [
        {
            "title": "Assignment",
            "fields": assignment_fields,
        }
    ]
    (output / "forms.json").write_text(json.dumps(forms, indent=2), encoding="utf-8")

    triggers = [
        {
            "title": "codex_assignment_auto_route",
            "conditions": {
                "all": [
                    {
                        "field": "ticket_form_id",
                        "operator": "is",
                        "value": "Assignment",
                    }
                ]
            },
            "actions": [
                {
                    "field": "group_id",
                    "value": "Relocation_Counselors",
                }
            ],
        }
    ]
    (output / "triggers.json").write_text(json.dumps(triggers, indent=2), encoding="utf-8")

    sla_policies = [
        {
            "title": "codex_assignment_standard",
            "policy": {
                "priority_targets": {
                    "normal": {
                        "response": 3600,
                        "resolution": 28800,
                    }
                }
            },
        }
    ]
    (output / "sla.json").write_text(json.dumps(sla_policies, indent=2), encoding="utf-8")
