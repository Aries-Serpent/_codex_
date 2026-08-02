#!/usr/bin/env python3
"""Map workflow triggers and dependants before a workflow is quarantined."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
WORKFLOW_DIR = REPO_ROOT / ".github" / "workflows"


def _workflow_name(path: Path) -> str:
    return path.name


def simulate(workflow: str, workflow_dir: Path = WORKFLOW_DIR) -> dict[str, object]:
    target = workflow_dir / workflow
    if not target.exists():
        raise FileNotFoundError(target)
    text = target.read_text(encoding="utf-8")
    trigger_lines = [
        line.strip()
        for line in text.splitlines()
        if re.match(r"^(on:|[- ]*(push|pull_request|workflow_run|schedule|workflow_dispatch):)", line)
    ]
    dependants = []
    for path in sorted(workflow_dir.glob("*.y*ml")):
        if path == target:
            continue
        content = path.read_text(encoding="utf-8", errors="replace")
        if workflow in content or target.stem in content:
            dependants.append(path.name)
    return {
        "workflow": _workflow_name(target),
        "triggers": trigger_lines,
        "workflow_run_dependants": dependants,
        "workflow_name_values": re.findall(r"^\s*name:\s*[\"']?([^\"'\n]+)", text, re.MULTILINE),
        "coverage_impact": "review-required" if dependants else "no discovered dependants",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workflow", required=True)
    parser.add_argument("--json", dest="json_path")
    args = parser.parse_args()
    report = simulate(args.workflow)
    output = json.dumps(report, indent=2)
    if args.json_path:
        Path(args.json_path).write_text(output + "\n", encoding="utf-8")
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
