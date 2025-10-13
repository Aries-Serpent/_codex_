"""Mermaid diagram helpers for CRM process visualisations."""

from __future__ import annotations

from collections.abc import Iterable, Sequence

__all__ = ["intake_to_mermaid"]


def _sanitise_label(label: str) -> str:
    """Return a Mermaid-safe label."""

    cleaned = label.replace("[", "(").replace("]", ")")
    return cleaned.replace("\n", " ").strip()


def intake_to_mermaid(flow_name: str, steps: Sequence[str] | Iterable[str]) -> str:
    """Generate a simple top-down Mermaid flowchart for an intake process."""

    if not flow_name:
        raise ValueError("flow_name must be provided")

    steps_list = [step for step in steps if str(step).strip()]
    if not steps_list:
        raise ValueError("At least one step is required to build a diagram")

    lines = ["flowchart TD", f"  A[Start: {_sanitise_label(flow_name)}] --> B[Intake]"]
    previous_node = "B"

    for index, step in enumerate(steps_list, start=1):
        node_id = f"N{index}"
        label = _sanitise_label(str(step))
        lines.append(f"  {previous_node} --> {node_id}[{label}]")
        previous_node = node_id

    lines.append(f"  {previous_node} --> Z[Close]")
    return "\n".join(lines) + "\n"
