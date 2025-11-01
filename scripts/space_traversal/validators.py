"""Policy validation helpers for capability audit gates."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Tuple


def _load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def check_low_threshold(gaps_path: Path) -> Tuple[int, List[dict]]:
    """Return the count and list of low maturity capabilities."""
    gaps = _load_json(gaps_path)
    low_list = gaps.get("low_maturity", [])
    return len(low_list), low_list


def check_missing_detectors(
    scored_path: Path, overrides: Dict[str, Sequence[str]] | None
) -> List[str]:
    """Return canonical IDs from overrides that are missing in scored results."""
    scored = _load_json(scored_path)
    have = {cap.get("id") for cap in scored.get("capabilities", [])}
    expect = set(overrides.keys()) if overrides else set()
    return sorted(expect - have)


def _format_low_table(low_list: Iterable[dict]) -> List[str]:
    rows = ["| ID | Score | Primary Deficit |", "|----|-------|-----------------|"]
    for item in low_list:
        comps = item.get("components") or {}
        if comps:
            primary = min(comps, key=lambda key: comps[key])
        else:
            primary = "n/a"
        rows.append(f"| {item.get('id')} | {item.get('score', 0.0):.2f} | {primary} |")
    return rows


def emit_summary(
    low_list: List[dict],
    missing_detector_ids: Sequence[str],
    thresholds: Dict[str, float],
) -> str:
    """Produce deterministic markdown summary text for CI logs/step summary."""
    lines: List[str] = []
    lines.append("# Capability Audit — Gate Summary")
    lines.append("")
    lines.append(f"- Low threshold: {thresholds.get('low')}")
    lines.append(f"- Medium threshold: {thresholds.get('medium')}")
    lines.append("")
    lines.append(f"## Low Maturity ({len(low_list)})")
    if low_list:
        lines.extend(_format_low_table(low_list))
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
