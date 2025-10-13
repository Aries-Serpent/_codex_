"""Conversion helpers between Zendesk rule specs and Dynamics 365 workflows."""

from __future__ import annotations

from typing import Any

Rule = dict[str, Any]


def zd_trigger_to_d365(rule: Rule) -> Rule:
    """Translate a Zendesk trigger rule into a realtime Dynamics 365 workflow."""

    return {
        "type": "realtime_workflow",
        "when": "create_or_update",
        "if": rule.get("if", []),
        "then": rule.get("then", []),
    }


def zd_automation_to_d365(rule: Rule) -> Rule:
    """Translate a Zendesk automation rule into a background Dynamics 365 workflow."""

    return {
        "type": "background_workflow",
        "schedule": rule.get("schedule"),
        "if": rule.get("if", []),
        "then": rule.get("then", []),
    }


def fidelity_score(
    logic_equivalence: float,
    data_mapping: float,
    sla_parity: float,
    *,
    weight_logic: float = 0.5,
    weight_data: float = 0.3,
    weight_sla: float = 0.2,
) -> float:
    """Compute a weighted fidelity score for a conversion scenario."""

    weights_total = weight_logic + weight_data + weight_sla
    if not 0 <= logic_equivalence <= 1 or not 0 <= data_mapping <= 1 or not 0 <= sla_parity <= 1:
        raise ValueError("All fidelity inputs must be within [0, 1].")

    if weights_total <= 0:
        raise ValueError("Weights must be positive and sum to a positive value.")

    normalised_logic = weight_logic / weights_total
    normalised_data = weight_data / weights_total
    normalised_sla = weight_sla / weights_total
    return (
        logic_equivalence * normalised_logic
        + data_mapping * normalised_data
        + sla_parity * normalised_sla
    )
