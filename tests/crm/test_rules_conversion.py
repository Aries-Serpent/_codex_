from __future__ import annotations

from codex_crm.convert import automation_to_d365, compute_fidelity, trigger_to_d365


def _sample_rule() -> dict[str, object]:
    return {
        "name": "Notify assignee",
        "if": {"status": "open"},
        "then": ["notify_assignee"],
        "sla": None,
    }


def test_trigger_to_d365_structure() -> None:
    rule = _sample_rule()
    converted = trigger_to_d365(rule)

    assert converted["type"] == "realtime_workflow"
    assert converted["conditions"] == rule["if"]
    assert converted["actions"] == rule["then"]


def test_automation_to_d365_structure() -> None:
    rule = _sample_rule()
    converted = automation_to_d365(rule)

    assert converted["type"] == "background_workflow"
    assert converted["actions"] == rule["then"]


def test_compute_fidelity_default_weights() -> None:
    rule = _sample_rule()
    converted = trigger_to_d365(rule)
    fidelity = compute_fidelity(rule, converted)

    assert fidelity.logic == 1.0
    assert fidelity.data == 1.0
    assert fidelity.sla == 1.0
    assert fidelity.score == 1.0
