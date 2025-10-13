"""Mermaid diagram utilities."""

from __future__ import annotations


def flow_to_mermaid(flow_name: str, steps: list[str]) -> str:
    """Generate a Mermaid ``flowchart TD`` diagram string."""

    if not steps:
        return "flowchart TD\n  A[Start]-->Z[Close]\n"
    lines = ["flowchart TD", f"  A[Start: {flow_name}]-->B[{_esc(steps[0])}]"]
    prev = "B"
    for i, step in enumerate(steps[1:], start=1):
        node_id = f"N{i}"
        lines.append(f"  {prev}-->{node_id}[{_esc(step)}]")
        prev = node_id
    lines.append(f"  {prev}-->Z[Close]")
    return "\n".join(lines) + "\n"


def intake_to_mermaid(flow_name: str, steps: list[str]) -> str:
    """Backward compatible alias for :func:`flow_to_mermaid`."""

    return flow_to_mermaid(flow_name, steps)


def _esc(value: str) -> str:
    return value.replace("[", "(").replace("]", ")")
