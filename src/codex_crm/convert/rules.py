"""Conversion helpers for mapping shared rule definitions across CRM systems."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

__all__ = [
    "ConversionFidelity",
    "automation_to_d365",
    "compute_fidelity",
    "trigger_to_d365",
]


@dataclass(frozen=True)
class ConversionFidelity:
    """Summary of conversion fidelity metrics."""

    logic: float
    data: float
    sla: float
    score: float


def _normalise_logic(rule: dict[str, Any]) -> Any:
    """Return the comparable logic block from a rule."""

    return rule.get("if")


def _normalise_actions(rule: dict[str, Any]) -> Any:
    """Return the comparable action block from a rule."""

    return rule.get("then")


def trigger_to_d365(rule: dict[str, Any]) -> dict[str, Any]:
    """Convert a Zendesk trigger-style rule into a D365 workflow structure."""

    if "if" not in rule or "then" not in rule:
        raise ValueError("rule must include 'if' and 'then' keys")

    return {
        "name": rule.get("name"),
        "type": "realtime_workflow",
        "mode": rule.get("mode", "synchronous"),
        "when": rule.get("when", "create_or_update"),
        "scope": rule.get("scope", "organization"),
        "conditions": rule["if"],
        "actions": rule["then"],
        "source": rule.get("source", "zendesk_trigger"),
    }


def automation_to_d365(rule: dict[str, Any]) -> dict[str, Any]:
    """Convert a Zendesk automation-style rule into a D365 background workflow."""

    if "if" not in rule or "then" not in rule:
        raise ValueError("rule must include 'if' and 'then' keys")

    return {
        "name": rule.get("name"),
        "type": "background_workflow",
        "mode": rule.get("mode", "asynchronous"),
        "schedule": rule.get("schedule"),
        "conditions": rule["if"],
        "actions": rule["then"],
        "source": rule.get("source", "zendesk_automation"),
    }


def compute_fidelity(
    source_rule: dict[str, Any],
    converted_rule: dict[str, Any],
    *,
    alpha: float = 0.4,
    beta: float = 0.4,
    gamma: float = 0.2,
) -> ConversionFidelity:
    """Compute a simple fidelity score between the original and converted rules."""

    if not abs(alpha + beta + gamma - 1.0) < 1e-9:
        raise ValueError("alpha, beta and gamma must sum to 1.0")

    logic_match = 1.0 if _normalise_logic(source_rule) == converted_rule.get("conditions") else 0.0
    data_match = 1.0 if _normalise_actions(source_rule) == converted_rule.get("actions") else 0.0

    source_sla = source_rule.get("sla")
    converted_sla = converted_rule.get("sla")
    sla_match = (
        1.0 if source_sla == converted_sla else (0.0 if source_sla or converted_sla else 1.0)
    )

    score = alpha * logic_match + beta * data_match + gamma * sla_match

    return ConversionFidelity(
        logic=logic_match,
        data=data_match,
        sla=sla_match,
        score=score,
    )
