#!/usr/bin/env python3
"""Validate the checked-in Copilot bootstrap workflow contract."""

from __future__ import annotations

import argparse
from pathlib import Path

import yaml

_JOB_PERMISSIONS = {
    "resource-profile": {"contents": "read"},
    "copilot-setup-steps": {
        "contents": "read",
        "actions": "write",
        "issues": "write",
        "pull-requests": "write",
    },
    "rescue-comment": {"pull-requests": "write", "issues": "write"},
}

_JOB_KEYS = {
    "resource-profile": {
        "name",
        "runs-on",
        "timeout-minutes",
        "permissions",
        "outputs",
        "steps",
    },
    "copilot-setup-steps": {
        "name",
        "runs-on",
        "timeout-minutes",
        "permissions",
        "env",
        "steps",
    },
    "rescue-comment": {
        "name",
        "runs-on",
        "needs",
        "if",
        "permissions",
        "steps",
        "env",
        "timeout-minutes",
    },
}


def validate(path: Path) -> list[str]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    errors: list[str] = []
    if not isinstance(data, dict) or not isinstance(data.get("jobs"), dict):
        return ["workflow jobs must be a mapping"]
    jobs = data["jobs"]
    if set(jobs) != set(_JOB_PERMISSIONS):
        errors.append("expected resource-profile, copilot-setup-steps, and rescue-comment jobs")

    for name, supported in _JOB_KEYS.items():
        job = jobs.get(name, {})
        if not isinstance(job, dict):
            errors.append(f"{name} job must be a mapping")
            continue
        if set(job) - supported:
            errors.append(f"unsupported {name} job keys")
        timeout = job.get("timeout-minutes")
        if not isinstance(timeout, int) or not 1 <= timeout <= 59:
            errors.append(f"{name} timeout-minutes must be between 1 and 59")
        if job.get("permissions") != _JOB_PERMISSIONS[name]:
            errors.append(f"{name} permissions differ from the expected grant")

    resource_job = jobs.get("resource-profile", {})
    if not isinstance(resource_job, dict):
        resource_job = {}
    if "vars.COPILOT_RUNNER_PROFILE" not in str(resource_job.get("runs-on", "")):
        errors.append("resource-profile runner must use COPILOT_RUNNER_PROFILE")
    resource_steps = resource_job.get("steps", [])
    if not isinstance(resource_steps, list):
        resource_steps = []
    resource_scripts = "\n".join(
        str(step.get("run", "")) for step in resource_steps if isinstance(step, dict)
    )
    if (
        "agent_resource_profile.py" not in resource_scripts
        or "--github-output" not in resource_scripts
    ):
        errors.append("resource-profile must run and export agent_resource_profile.py")

    setup_job = jobs.get("copilot-setup-steps", {})
    if not isinstance(setup_job, dict):
        setup_job = {}
    setup_steps = setup_job.get("steps", [])
    if not isinstance(setup_steps, list):
        setup_steps = []
    setup_steps = [step for step in setup_steps if isinstance(step, dict)]
    checkout = [
        step for step in setup_steps if str(step.get("uses", "")).startswith("actions/checkout@")
    ]
    if not checkout or any(s.get("with", {}).get("lfs") is not False for s in checkout):
        errors.append("checkout must explicitly disable automatic LFS")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("workflow", type=Path)
    args = parser.parse_args()
    errors = validate(args.workflow)
    for error in errors:
        print(f"ERROR: {error}")
    if not errors:
        print("Copilot bootstrap workflow contract verified")
    return int(bool(errors))


if __name__ == "__main__":
    raise SystemExit(main())
