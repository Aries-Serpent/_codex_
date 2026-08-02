#!/usr/bin/env python3
"""Validate the candidate/quarantine/archive pruning lifecycle."""

from __future__ import annotations

import argparse
import json
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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("registry", type=Path)
    args = parser.parse_args()
    data = json.loads(args.registry.read_text(encoding="utf-8"))
    records = data if isinstance(data, list) else data.get("candidates", [])
    errors = {str(i): validate(item) for i, item in enumerate(records) if validate(item)}
    print(json.dumps({"records": len(records), "errors": errors}, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
