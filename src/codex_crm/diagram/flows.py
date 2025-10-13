from __future__ import annotations

from collections.abc import Iterable


def flow_to_mermaid(flow_name: str, steps: Iterable[str]) -> str:
    """Render a simple Mermaid flowchart from linear workflow steps."""

    steps = [step for step in steps if step]
    lines = ["flowchart TD"]
    if steps:
        lines.append(f"  A[Start: {flow_name}]-->N0[{steps[0]}]")
        previous = "N0"
        for index, step in enumerate(steps[1:], start=1):
            node = f"N{index}"
            lines.append(f"  {previous}-->{node}[{step}]")
            previous = node
        lines.append(f"  {previous}-->Z[Close]")
    else:
        lines.append(f"  A[Start: {flow_name}]-->Z[Close]")
    return "\n".join(lines)
