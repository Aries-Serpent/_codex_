#!/usr/bin/env python
"""codex_yaml_gap_check.py

Validate coverage between:
- codex_gap_registry.yaml (gaps)
- codex_task_sequence.yaml (phases/steps)

Outputs codex_yaml_gap_report.md describing:
- gaps without a mapped YAML step
- YAML steps that are not referenced by any gap (hygiene)
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

try:
    import yaml  # type: ignore
except ImportError:  # pragma: no cover
    yaml = None


@dataclass
class GapRef:
    id: str
    yaml_phase_step: Optional[str]


def _load_yaml(path: Path) -> Any:
    if not path.exists():
        raise FileNotFoundError(path)
    if yaml is None:
        raise RuntimeError("PyYAML is required. Install with `pip install pyyaml`.")
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _collect_gaps(registry_path: Path) -> list[GapRef]:
    data = _load_yaml(registry_path) or {}
    gaps_data = data.get("gaps", []) if isinstance(data, dict) else []
    gaps: list[GapRef] = []

    for item in gaps_data:
        if not isinstance(item, dict):
            continue
        gid = str(item.get("id", "")).strip()
        yps = item.get("yaml_phase_step")
        yps_str = str(yps).strip() if yps not in (None, "") else None
        if gid:
            gaps.append(GapRef(id=gid, yaml_phase_step=yps_str))

    return gaps


def _collect_yaml_steps(sequence_path: Path) -> set[str]:
    data = _load_yaml(sequence_path) or {}
    seq = data.get("codex_task_sequence") if isinstance(data, dict) else None
    if not isinstance(seq, dict):
        raise KeyError("YAML missing 'codex_task_sequence' root object")

    phases = seq.get("phases", []) or []
    steps_ids: set[str] = set()

    for phase in phases:
        if not isinstance(phase, dict):
            continue
        phase_id = str(phase.get("id", "")).strip()
        steps = phase.get("steps", []) or []
        for step in steps:
            if not isinstance(step, dict):
                continue
            step_id = str(step.get("id", "")).strip()
            if not phase_id or not step_id:
                continue
            steps_ids.add(f"{phase_id}.{step_id}")

    return steps_ids


def _write_report(
    report_path: Path,
    gaps_without_step: list[GapRef],
    yaml_steps_without_gap: list[str],
) -> None:
    report_path.parent.mkdir(parents=True, exist_ok=True)
    lines: list[str] = []
    lines.append("# codex_yaml_gap_report\n")
    lines.append("## Gaps without mapped YAML step\n")
    if not gaps_without_step:
        lines.append("All gaps have a yaml_phase_step mapped to an existing YAML step\n")
    else:
        lines.append("| gap_id | yaml_phase_step | notes |\n")
        lines.append("|--------|-----------------|-------|\n")
        for g in gaps_without_step:
            yps = g.yaml_phase_step or "-"
            lines.append(f"| {g.id} | {yps} | missing or invalid yaml_phase_step |\n")

    lines.append("\n## YAML steps without any gap reference (hygiene)\n")
    if not yaml_steps_without_gap:
        lines.append(
            "All YAML steps are referenced by at least one gap (or this check is relaxed).\n"
        )
    else:
        lines.append("| yaml_phase_step | notes |\n")
        lines.append("|-----------------|-------|\n")
        for step in sorted(yaml_steps_without_gap):
            lines.append(f"| {step} | no gap.yaml_phase_step references this step |\n")

    report_path.write_text("".join(lines), encoding="utf-8")


def parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Check coverage between gap registry and codex_task_sequence YAML."
    )
    p.add_argument("--gaps", required=True, help="Path to codex_gap_registry.yaml.")
    p.add_argument("--yaml", required=True, help="Path to codex_task_sequence.yaml.")
    p.add_argument("--out", required=True, help="Path to write codex_yaml_gap_report.md.")
    return p.parse_args(argv)


def main(argv: Optional[list[str]] = None) -> int:
    args = parse_args(argv)

    registry_path = Path(args.gaps).expanduser().resolve()
    yaml_path = Path(args.yaml).expanduser().resolve()
    report_path = Path(args.out).expanduser().resolve()

    gaps = _collect_gaps(registry_path)
    yaml_steps = _collect_yaml_steps(yaml_path)

    gaps_without_step: list[GapRef] = []
    used_steps: set[str] = set()

    for g in gaps:
        if not g.yaml_phase_step or g.yaml_phase_step not in yaml_steps:
            gaps_without_step.append(g)
        else:
            used_steps.add(g.yaml_phase_step)

    yaml_steps_without_gap = sorted(step for step in yaml_steps if step not in used_steps)
    _write_report(report_path, gaps_without_step, yaml_steps_without_gap)
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
