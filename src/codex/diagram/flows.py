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
        rows: list[tuple[str, str, str]] = []
        for e in materialized:
            if isinstance(e, dict):
                rows.append((e["src"], e.get("label", ""), e["dst"]))
            elif isinstance(e, tuple):
                rows.append((e[0], e[1], e[2]))
            else:  # pragma: no cover - defensive guard
                raise TypeError(f"Unsupported edge record: {e!r}")
        rows.sort(key=lambda t: (t[0], t[1], t[2]))
    out = [f"%% {name}", "graph TD"]
    nodes = sorted({r[0] for r in rows} | {r[2] for r in rows})
    for n in nodes:
        out.append(f'    {sanitize_id(n)}["{n}"]')
    for src, label, dst in rows:
        label_text = f"|{label}|" if label else ""
        out.append(f"    {sanitize_id(src)} -->{label_text} {sanitize_id(dst)}")
    out.append("")
    return "\n".join(out)


def intake_to_mermaid(name: str, steps: Iterable[str]) -> str:
    """Backward compatible alias that accepts sequential intake steps."""

    return flow_to_mermaid(name, list(steps))


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
