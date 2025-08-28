#!/usr/bin/env python3
"""Validate that workflow files use allowed self-hosted runner labels."""
from __future__ import annotations

import json
import pathlib
import sys
from typing import List

try:
    import yaml
except Exception:  # pragma: no cover - dependency check
    print("Install pyyaml to run label policy lint.", file=sys.stderr)
    sys.exit(2)

POLICY_PATH = pathlib.Path("tools/label_policy.json")
WF_DIR = pathlib.Path(".github/workflows")


def as_list(value: object) -> List[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [str(v) for v in value]
    return []


def load_policy() -> tuple[set[str], set[str], set[str]]:
    policy = json.loads(POLICY_PATH.read_text(encoding="utf-8"))
    allowed = set(policy["allowed_labels"])
    required = set(policy.get("required_base", []))
    defaults = set(policy.get("defaults_for_string_runs_on", []))
    return allowed, required, defaults


def lint_file(
    path: pathlib.Path, allowed: set[str], required: set[str], defaults: set[str]
) -> List[str]:
    errors: List[str] = []
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    jobs = (data or {}).get("jobs", {})
    for job_name, job in (jobs or {}).items():
        runs_on = job.get("runs-on")
        if runs_on is None:
            continue
        labels = as_list(runs_on)
        if "self-hosted" in labels:
            if labels == ["self-hosted"]:
                labels = ["self-hosted", *defaults]
            extra_labels = [label for label in labels if label not in allowed]
            missing_base = [label for label in required if label not in labels]
            if extra_labels:
                errors.append(f"{path}:{job_name}: disallowed labels: {extra_labels}")
            if missing_base:
                errors.append(f"{path}:{job_name}: missing required base labels: {missing_base}")
    return errors


def main() -> int:
    if not WF_DIR.exists():
        print("No .github/workflows directory; nothing to lint.")
        return 0
    allowed, required, defaults = load_policy()
    problems: List[str] = []
    for file in sorted(WF_DIR.glob("*.y*ml")):
        problems.extend(lint_file(file, allowed, required, defaults))
    if problems:
        print("Label policy violations:\n- " + "\n- ".join(problems), file=sys.stderr)
        return 1
    print("Label policy: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
