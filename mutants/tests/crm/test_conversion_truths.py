"""Truth-table style regression tests for conversion fidelity."""

from codex_crm.convert.rules import (
    fidelity_score,
    zd_automation_to_d365,
    zd_trigger_to_d365,
)


def test_trigger_to_d365_minimal() -> None:
    zd_payload = {
        "if": [{"field": "ticket_form_id", "operator": "is", "value": "Assignment"}],
        "then": [{"field": "group_id", "value": "Relocation_Counselors"}],
    }
    converted = zd_trigger_to_d365(zd_payload)
    assert converted["type"] == "realtime_workflow", "Condition must be true"
    assert converted["if"], "Condition must be true"
    assert converted["then"], "Condition must be true"


def test_automation_to_d365_minimal() -> None:
    zd_payload = {
        "schedule": {"every": "hour"},
        "if": [{"field": "status", "operator": "is", "value": "open"}],
        "then": [],
    }
    converted = zd_automation_to_d365(zd_payload)
    assert converted["type"] == "background_workflow", "Condition must be true"
    assert "schedule" in converted, "Condition must be true"


def test_fidelity_score_bounds() -> None:
    assert 0.0 <= fidelity_score(0, 0, 0) <= 1.0
    assert 0.99 <= fidelity_score(1, 1, 1) <= 1.0
