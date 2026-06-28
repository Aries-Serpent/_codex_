"""
Canonical diagram helpers.
Use: from codex.diagram.flows import flow_to_mermaid
"""

from __future__ import annotations

from collections.abc import Iterable

Edge = tuple[str, str, str] | dict[str, str] | str


def flow_to_mermaid(name: str, edges: Iterable[Edge]) -> str:
    """Produce a deterministic Mermaid ``flowchart TD`` diagram."""

    materialized = list(edges)
    if not materialized:
        rows = _flow_from_steps(name, [])
    elif all(isinstance(e, str) for e in materialized):
        rows = _flow_from_steps(name, [str(e) for e in materialized])
    else:
        rows: list[tuple[str, str, str]] = []  # type: ignore[no-redef]
        for e in materialized:
            if isinstance(e, dict):
                rows.append((e["src"], e.get("label", ""), e["dst"]))
            elif isinstance(e, tuple):
                rows.append((e[0], e[1], e[2]))
            else:  # pragma: no cover - defensive guard
                raise TypeError(f"Unsupported edge record: {e!r}")
        rows.sort(key=lambda t: (t[0], t[1], t[2]))
    out = [f"%% {name}", "flowchart TD"]
    nodes = sorted({r[0] for r in rows} | {r[2] for r in rows} - {"Close"})
    for n in nodes:
        out.append(f'    {sanitize_id(n)}["{n}"]')
    for src, label, dst in rows:
        label_text = f"|{label}|" if label else ""
        src_id = "Z" if src == "Close" else sanitize_id(src)
        dst_id = "Z" if dst == "Close" else sanitize_id(dst)
        out.append(f"    {src_id} -->{label_text} {dst_id}")
    # Terminal close node always last (Mermaid convention: Z[Close])
    if any(r[2] == "Close" for r in rows):
        out.append("    Z[Close]")
    return "\n".join(out) + "\n"


def intake_to_mermaid(name: str, steps: Iterable[str]) -> str:
    """Backward compatible alias that accepts sequential intake steps.

    Args:
        name: The name of the flow
        steps: Sequential intake steps (must contain at least one non-whitespace step)

    Raises:
        ValueError: If steps is empty or contains only whitespace
    """
    steps_list = [s.strip() for s in steps if s.strip()]
    if not steps_list:
        raise ValueError("steps must contain at least one non-whitespace step")

    return flow_to_mermaid(name, steps_list)


def sanitize_id(s: str) -> str:
    return "".join(ch if ch.isalnum() or ch in ("_",) else "_" for ch in s)


def _flow_from_steps(name: str, steps: list[str]) -> list[tuple[str, str, str]]:
    start = f"Start: {name}" if name else "Start"
    rows: list[tuple[str, str, str]] = []
    if not steps:
        rows.append((start, "", "Close"))
        return rows
    prev = start
    for step in steps:
        rows.append((prev, "", step))
        prev = step
    rows.append((prev, "", "Close"))
    return rows
