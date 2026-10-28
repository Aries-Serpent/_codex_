#!/usr/bin/env python3
"""Check the retained ordinary Actions workflow, not hosted Copilot setup support."""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
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

_LEGACY_FILTERED_ENV_COMMAND = (
    'env | grep -E "^(CODEX|PYTHON|RAG|CI|GITHUB|COPILOT)" | sort || true'
)
_ENV_DUMP_COMMAND = re.compile(r"\bprintenv\b|\benv\s*(?:\||>|$)")
_DEFERRED_CLOUD_SETUP_CHECKS = (
    "agent context preparation and delivery",
    "requested LFS fetch integration",
    "always-run setup readiness reporting",
)


@dataclass(frozen=True)
class WorkflowValidation:
    errors: tuple[str, ...]
    legacy_findings: tuple[str, ...]
    deferred_cloud_setup_checks: tuple[str, ...] = _DEFERRED_CLOUD_SETUP_CHECKS


def _environment_dump_findings(jobs: dict) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    legacy: list[str] = []
    for job_name, job in jobs.items():
        if not isinstance(job, dict) or not isinstance(job.get("steps", []), list):
            continue
        for step in job.get("steps", []):
            if not isinstance(step, dict):
                continue
            step_name = str(step.get("name", "unnamed step"))
            for line in str(step.get("run", "")).splitlines():
                command = line.strip()
                if not command or command.startswith("#"):
                    continue
                if command == _LEGACY_FILTERED_ENV_COMMAND:
                    if (
                        job_name == "copilot-setup-steps"
                        and step_name == "✅ Validate Environment Setup"
                    ):
                        legacy.append(
                            f"{job_name}/{step_name} retains filtered environment output: {command}"
                        )
                    else:
                        errors.append(f"unreviewed environment output in {job_name}/{step_name}")
                    continue
                if _ENV_DUMP_COMMAND.search(command):
                    errors.append(f"unreviewed environment output in {job_name}/{step_name}")
    return errors, legacy


def validate_retained_workflow(path: Path) -> WorkflowValidation:
    """Validate retained baseline compatibility and report deferred hardening separately."""
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        return WorkflowValidation((f"unable to read valid workflow YAML: {exc}",), ())

    if not isinstance(data, dict) or not isinstance(data.get("jobs"), dict):
        return WorkflowValidation(("workflow jobs must be a mapping",), ())
    jobs = data["jobs"]
    errors: list[str] = []
    if set(jobs) != set(_JOB_PERMISSIONS):
        errors.append(
            "expected retained resource-profile, copilot-setup-steps, and rescue-comment jobs"
        )

    for name, supported in _JOB_KEYS.items():
        job = jobs.get(name, {})
        if not isinstance(job, dict):
            errors.append(f"{name} job must be a mapping")
            continue
        if set(job) - supported:
            errors.append(f"unsupported {name} job keys")
        timeout = job.get("timeout-minutes")
        if type(timeout) is not int or not 1 <= timeout <= 59:
            errors.append(f"{name} timeout-minutes must be between 1 and 59")
        if job.get("permissions") != _JOB_PERMISSIONS[name]:
            errors.append(f"{name} permissions differ from the retained baseline")
        if not isinstance(job.get("steps"), list):
            errors.append(f"{name} steps must be a list")

    resource_job = jobs.get("resource-profile", {})
    if not isinstance(resource_job, dict):
        resource_job = {}
    if "vars.COPILOT_RUNNER_PROFILE" not in str(resource_job.get("runs-on", "")):
        errors.append("resource-profile must use the configured runner label")
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
        errors.append("resource-profile command or output contract is missing")

    setup_job = jobs.get("copilot-setup-steps", {})
    if not isinstance(setup_job, dict):
        setup_job = {}
    setup_steps = setup_job.get("steps", [])
    if not isinstance(setup_steps, list):
        setup_steps = []
    setup_steps = [step for step in setup_steps if isinstance(step, dict)]
    setup_scripts = "\n".join(str(step.get("run", "")) for step in setup_steps)
    if "environment_preflight.py" not in setup_scripts:
        errors.append("retained setup environment preflight is missing")
    checkout = [
        step for step in setup_steps if str(step.get("uses", "")).startswith("actions/checkout@")
    ]
    if not checkout:
        errors.append("checkout must explicitly disable automatic LFS")
    else:
        for step in checkout:
            options = step.get("with", {})
            if not isinstance(options, dict):
                errors.append("checkout options must be a mapping")
            elif options.get("lfs") is not False:
                errors.append("checkout must explicitly disable automatic LFS")

    dump_errors, legacy_findings = _environment_dump_findings(jobs)
    errors.extend(dump_errors)
    return WorkflowValidation(tuple(errors), tuple(legacy_findings))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("workflow", type=Path)
    args = parser.parse_args()
    report = validate_retained_workflow(args.workflow)
    for error in report.errors:
        print(f"ERROR: {error}")
    for finding in report.legacy_findings:
        print(f"LEGACY BASELINE FINDING: {finding}")
    print("Deferred cloud-setup checks: " + ", ".join(report.deferred_cloud_setup_checks))
    if not report.errors:
        print(
            "Retained ordinary workflow compatibility validated; "
            "hosted Copilot setup support is not validated."
        )
    return int(bool(report.errors))


if __name__ == "__main__":
    raise SystemExit(main())
