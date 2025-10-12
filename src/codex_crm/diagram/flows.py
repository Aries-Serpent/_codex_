"""Helpers for rendering workflow steps as Mermaid diagrams."""

from __future__ import annotations

from collections.abc import Iterable


def flow_to_mermaid(flow_name: str, steps: Iterable[str]) -> str:
    """Return a Mermaid flowchart definition for the given steps."""

    steps_list: list[str] = [step for step in steps if step]
    lines = ["flowchart TD"]
    if not steps_list:
        lines.append("  A[Start]-->B[Close]")
        return "\n".join(lines)

    lines.append(f"  A[Start: {flow_name}]-->N0[{steps_list[0]}]")
    previous = "N0"
    for index, step in enumerate(steps_list[1:], start=1):
        node_id = f"N{index}"
        lines.append(f"  {previous}-->{node_id}[{step}]")
        previous = node_id
    lines.append(f"  {previous}-->Z[Close]")
    return "\n".join(lines)
