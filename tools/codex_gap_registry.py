#!/usr/bin/env python
"""codex_gap_registry.py

Build a machine-readable *Gap Registry* for the _codex_ project.

Inputs (best-effort, any may be missing):
- --audit       : path to latest status audit markdown
- --change-log  : path to codex_change_log.md
- --errors      : path to codex_error_questions.md
- --hardship    : optional path to hardship metadata (YAML)
- --cap-map     : optional path to capability map (YAML)
- --out         : path to write codex_gap_registry.yaml

The script is intentionally heuristic: it looks for a "High-Signal Findings"
section and extracts bullet points as gap descriptions, then augments them with
any available metadata (change log, hardship, capability map).
"""
from __future__ import annotations

import argparse
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml


@dataclass
class Gap:
    id: str
    capability: str
    location: List[str]
    description: str
    status: str  # missing|stubbed|partial|implemented
    risk_level: Optional[str] = None
    yaml_phase_step: Optional[str] = None
    ml_test_categories: Optional[List[str]] = None
    last_seen_in_audit: Optional[str] = None
    notes: Optional[str] = None


_HIGH_SIGNAL_HEADING_RE = re.compile(r"^##?\s+High-Signal Findings", re.IGNORECASE)
_BULLET_RE = re.compile(r"^\s*[-*]\s+(.*)")
_DATE_RE = re.compile(r"(20\d{2}-\d{2}-\d{2})")


def _slugify(text: str) -> str:
    text = text.strip().lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = re.sub(r"-+", "-", text).strip("-")
    return text or f"gap-{hash(text)}"


def _infer_capability_from_text(text: str) -> str:
    t = text.lower()
    if "token" in t:
        return "tokenization"
    if "model" in t or "lora" in t or "peft" in t:
        return "modeling"
    if "train" in t or "trainer" in t:
        return "training"
    if "config" in t or "hydra" in t:
        return "configuration"
    if "metric" in t or "eval" in t:
        return "evaluation"
    if "log" in t or "monitor" in t:
        return "logging"
    if "checkpoint" in t or "resume" in t:
        return "checkpointing"
    if "dataset" in t or "data" in t:
        return "data_handling"
    if "deploy" in t or "docker" in t:
        return "deployment"
    if "experiment" in t or "mlflow" in t or "tracking" in t:
        return "experiment_tracking"
    if "extensibility" in t or "registry" in t:
        return "extensibility"
    return "general"


def _parse_audit(audit_path: Path) -> List[Gap]:
    if not audit_path.exists():
        return []

    lines = audit_path.read_text(encoding="utf-8", errors="ignore").splitlines()
    gaps: List[Gap] = []

    in_high_signal = False
    last_date: Optional[str] = None

    m = _DATE_RE.search(audit_path.name)
    if m:
        last_date = m.group(1)
    else:
        for line in lines:
            m = _DATE_RE.search(line)
            if m:
                last_date = m.group(1)
                break

    for line in lines:
        if _HIGH_SIGNAL_HEADING_RE.match(line):
            in_high_signal = True
            continue
        if in_high_signal:
            if line.startswith("#") and not _BULLET_RE.match(line):
                break
            m = _BULLET_RE.match(line)
            if not m:
                continue
            desc = m.group(1).strip()
            capability = _infer_capability_from_text(desc)
            gid = _slugify(f"{capability}.{desc[:80]}")
            gaps.append(
                Gap(
                    id=gid,
                    capability=capability,
                    location=[],
                    description=desc,
                    status="missing",
                    last_seen_in_audit=last_date,
                    notes="Extracted from High-Signal Findings in audit.",
                )
            )
    return gaps


def _parse_change_log(change_log_path: Path) -> Dict[str, Dict[str, Any]]:
    if not change_log_path or not change_log_path.exists():
        return {}
    rows: Dict[str, Dict[str, Any]] = {}
    lines = change_log_path.read_text(encoding="utf-8", errors="ignore").splitlines()
    for line in lines:
        if not line.startswith("|"):
            continue
        parts = [p.strip() for p in line.strip("|").split("|")]
        if len(parts) != 5:
            continue
        ts, phase_id, step_id, status, details = parts
        if ts == "timestamp":
            continue
        key = f"{phase_id}:{step_id}"
        rows.setdefault(key, {"events": []})["events"].append(
            {"timestamp": ts, "status": status, "details": details}
        )
    return rows


def _merge_status_from_change_log(gaps: List[Gap], change_log: Dict[str, Dict[str, Any]]) -> None:
    index_by_phase: Dict[str, Gap] = {}
    for gap in gaps:
        if gap.yaml_phase_step:
            index_by_phase[gap.yaml_phase_step] = gap
    for key, entry in change_log.items():
        events = entry.get("events", [])
        for ev in events:
            status = ev.get("status")
            if status != "ok":
                continue
            phase_step = key
            gap = index_by_phase.get(phase_step)
            if not gap:
                continue
            if gap.status == "missing":
                gap.status = "partial"


def _load_hardship(hardship_path: Optional[Path]) -> Dict[str, Dict[str, Any]]:
    if not hardship_path or not hardship_path.exists():
        return {}
    data = yaml.safe_load(hardship_path.read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict):
        return {}
    gaps = data.get("gaps")
    return gaps if isinstance(gaps, dict) else {}


def _apply_hardship(gaps: List[Gap], hardship: Dict[str, Dict[str, Any]]) -> None:
    for gap in gaps:
        meta = hardship.get(gap.id)
        if not meta:
            continue
        risk = meta.get("risk_level")
        if isinstance(risk, str):
            gap.risk_level = risk
        extra = meta.get("notes")
        if extra:
            gap.notes = (gap.notes or "") + f" | Hardship: {extra}"


def _load_capability_map(cap_map_path: Optional[Path]) -> Dict[str, Any]:
    if not cap_map_path or not cap_map_path.exists():
        return {}
    data = yaml.safe_load(cap_map_path.read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict):
        return {}
    caps = data.get("capabilities")
    return caps if isinstance(caps, dict) else {}


def _apply_capability_locations(gaps: List[Gap], cap_map: Dict[str, Any]) -> None:
    for gap in gaps:
        meta = cap_map.get(gap.capability)
        if not isinstance(meta, dict):
            continue
        locations: List[str] = []
        for key in ("code", "tests", "docs"):
            paths = meta.get(key)
            if isinstance(paths, list):
                locations.extend(str(p) for p in paths)
        if locations:
            gap.location = locations


def build_registry(
    audit: Optional[Path],
    change_log: Optional[Path],
    errors: Optional[Path],
    hardship: Optional[Path],
    cap_map: Optional[Path] = None,
) -> Dict[str, Any]:
    gaps = _parse_audit(audit) if audit else []
    change_rows = _parse_change_log(change_log) if change_log else {}
    _merge_status_from_change_log(gaps, change_rows)
    hardship_meta = _load_hardship(hardship)
    _apply_hardship(gaps, hardship_meta)
    cap_map_meta = _load_capability_map(cap_map)
    _apply_capability_locations(gaps, cap_map_meta)
    return {"gaps": [asdict(g) for g in gaps]}


def parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Build codex gap registry YAML.")
    p.add_argument("--audit", type=str, default=None, help="Path to audit markdown file.")
    p.add_argument("--change-log", type=str, default=None, help="Path to codex_change_log.md.")
    p.add_argument("--errors", type=str, default=None, help="Path to codex_error_questions.md.")
    p.add_argument("--hardship", type=str, default=None, help="Optional hardship metadata YAML.")
    p.add_argument("--cap-map", type=str, default=None, help="Optional capability map YAML.")
    p.add_argument("--out", type=str, required=True, help="Output path for codex_gap_registry.yaml.")
    return p.parse_args(argv)


def main(argv: Optional[list[str]] = None) -> int:
    args = parse_args(argv)
    audit = Path(args.audit).expanduser().resolve() if args.audit else None
    change_log = Path(args.change_log).expanduser().resolve() if args.change_log else None
    errors = Path(args.errors).expanduser().resolve() if args.errors else None
    hardship = Path(args.hardship).expanduser().resolve() if args.hardship else None
    cap_map = Path(args.cap_map).expanduser().resolve() if args.cap_map else None
    out_path = Path(args.out).expanduser().resolve()
    registry = build_registry(audit, change_log, errors, hardship, cap_map)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(yaml.safe_dump(registry), encoding="utf-8")
    print(f"Wrote gap registry to {out_path}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
