"""
Validators

Purpose:
    [To be documented - Validators]

Usage:
    python scripts/space_traversal/validators.py [options]

    Examples:
    $ python scripts/space_traversal/validators.py --help

Arguments:
    [To be documented]

Environment Variables:
    [To be documented]

Dependencies:
    [To be documented]

Exit Codes:
    0: Success
    1: Error

Author: Codex Team
Last Updated: 2026-01-16
"""


from __future__ import annotations

import json


def load_json(path: str) -> dict:
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def check_low_threshold(gaps_path: str) -> tuple[int, list[dict]]:
    """
    Returns (count_low, low_list), where low_list contains entries with:
    { id, score, components, missing_patterns?, ... } as provided by S5.
    """
    gaps = load_json(gaps_path)
    low = gaps.get("low_maturity", [])
    return len(low), low


def check_missing_detectors(scored_path: str, overrides: dict[str, list[str]]) -> list[str]:
    """
    Ensures all override keys (canonical IDs) appear in scored capabilities.
    Returns the list of missing canonical IDs.
    """
    scored = load_json(scored_path)
    have = {c["id"] for c in scored.get("capabilities", [])}
    expect = set(overrides.keys()) if overrides else set()
    return sorted(expect - have)


def emit_summary(
    low_list: list[dict],
    missing_detector_ids: list[str],
    thresholds: dict[str, float],
) -> str:
    """Produce a deterministic markdown summary for job logs/step summary."""
    lines = []
    lines.append("# Capability Audit — Gate Summary")
    lines.append("")
    lines.append(f"- Low threshold: {thresholds.get('low')}")
    lines.append(f"- Medium threshold: {thresholds.get('medium')}")
    lines.append("")
    lines.append(f"## Low Maturity ({len(low_list)})")
    if low_list:
        lines.append("| ID | Score | Primary Deficit |")
        lines.append("|----|-------|-----------------|")
        for g in low_list:
            comps = g.get("components", {})
            comp = min(comps.items(), key=lambda kv: kv[1])[0] if comps else "n/a"
            lines.append(f"| {g['id']} | {g['score']:.2f} | {comp} |")
    else:
        lines.append("_None_")
    lines.append("")
    lines.append(f"## Missing Detectors (overrides) ({len(missing_detector_ids)})")
    if missing_detector_ids:
        for cid in missing_detector_ids:
            lines.append(f"- {cid}")
    else:
        lines.append("_None_")
    return "\n".join(lines)
