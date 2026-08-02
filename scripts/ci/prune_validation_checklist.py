#!/usr/bin/env python3
"""Validate the candidate/quarantine/archive pruning lifecycle."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

STAGES = ("CANDIDATE", "QUARANTINE", "CONSOLIDATED", "ARCHIVED")
REQUIRED_FIELDS = ("workflow_name", "stage", "candidate_date", "owner")


def validate(record: dict[str, object]) -> list[str]:
    errors = [f"missing {field}" for field in REQUIRED_FIELDS if not record.get(field)]
    stage = str(record.get("stage", ""))
    if stage not in STAGES:
        errors.append(f"invalid stage: {stage}")
    if stage in {"QUARANTINE", "CONSOLIDATED", "ARCHIVED"} and not record.get("dependency_map_path"):
        errors.append("dependency_map_path required after candidate stage")
    if stage in {"CONSOLIDATED", "ARCHIVED"} and not record.get("parity_report_path"):
        errors.append("parity_report_path required before archival")
    if stage == "ARCHIVED" and not record.get("rollback_sha"):
        errors.append("rollback_sha required for archived records")
    return errors


def load_records(path: Path) -> list[dict[str, object]]:
    """Load JSON registries and the Markdown registry used by this repository."""
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".json":
        data = json.loads(text)
        return data if isinstance(data, list) else data.get("candidates", [])
    if re.search(r"\|\s*_No candidates registered_\s*\|", text):
        return []
    records = []
    for line in text.splitlines():
        if not line.startswith("|") or line.startswith("|---") or "workflow_name" in line:
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) != len(REQUIRED_FIELDS) + 3:
            continue
        records.append(dict(zip(
            (*REQUIRED_FIELDS, "dependency_map_path", "parity_report_path", "rollback_sha"),
            (None if cell == "—" else cell for cell in cells),
        )))
    return records


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("registry", type=Path)
    args = parser.parse_args()
    records = load_records(args.registry)
    errors = {}
    for i, item in enumerate(records):
        item_errors = validate(item)
        if item_errors:
            errors[str(i)] = item_errors
    print(json.dumps({"records": len(records), "errors": errors}, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
