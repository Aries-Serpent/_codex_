from __future__ import annotations

from typing import Any

Rule = dict[str, Any]


def zd_trigger_to_d365(rule: Rule) -> Rule:
    """Convert a Zendesk trigger rule to a Dynamics 365 workflow representation."""

    return {
        "type": "realtime_workflow",
        "when": "create_or_update",
        "if": rule.get("if", []),
        "then": rule.get("then", []),
    }


def zd_automation_to_d365(rule: Rule) -> Rule:
    """Convert a Zendesk automation rule to a Dynamics 365 background workflow."""

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
    alpha: float = 0.5,
    beta: float = 0.3,
    gamma: float = 0.2,
) -> float:
    """Compute a weighted fidelity score for converted workflows."""

    return alpha * logic_equivalence + beta * data_mapping + gamma * sla_parity
