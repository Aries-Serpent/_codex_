#!/usr/bin/env python3
"""Validate the actual single-job Copilot bootstrap contract, not a text snapshot."""

from __future__ import annotations

import argparse
from pathlib import Path

import yaml


def validate(path: Path) -> list[str]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    errors = []
    jobs = data.get("jobs", {})
    if set(jobs) != {"copilot-setup-steps"}:
        errors.append("exactly one copilot-setup-steps job is required")
    job = jobs.get("copilot-setup-steps", {})
    supported = {"steps", "permissions", "runs-on", "services", "snapshot", "timeout-minutes"}
    if set(job) - supported:
        errors.append("unsupported Copilot setup job keys")
    if not 1 <= job.get("timeout-minutes", 0) <= 59:
        errors.append("timeout-minutes must be between 1 and 59")
    if job.get("permissions") != {"contents": "read"}:
        errors.append("setup requires only contents: read")
    if "vars.COPILOT_RUNNER_PROFILE" not in str(job.get("runs-on", "")):
        errors.append("runner selection must be on actual job runs-on")
    steps = job.get("steps", [])
    scripts = "\n".join(str(step.get("run", "")) for step in steps)
    required = [
        "agent_resource_profile.py",
        "environment_preflight.py",
        "fetch_lfs_assets.py",
        "prepare_agent_context.py",
        "agent_setup_readiness.py",
    ]
    for script in required:
        if script not in scripts:
            errors.append(f"missing bootstrap consumer {script}")
    positions = [scripts.find(script) for script in required[:3]]
    if positions != sorted(positions):
        errors.append("resource/detection must precede required fetch")
    if "--github-env" not in scripts:
        errors.append("resource worker outputs are not exported")
    if "env |" in scripts or "printenv" in scripts:
        errors.append("broad environment dump is not allowed")
    if "Validate CCA" in scripts or "COPILOT_AGENT_CCA_VERSION_LOCK" in scripts:
        errors.append("local compatibility flags must not gate platform bootstrap")
    checkout = [s for s in steps if str(s.get("uses", "")).startswith("actions/checkout@")]
    if not checkout or any(s.get("with", {}).get("lfs") is not False for s in checkout):
        errors.append("checkout must explicitly disable automatic LFS")
    if not any(
        s.get("if") == "always()" and "agent_setup_readiness.py" in s.get("run", "") for s in steps
    ):
        errors.append("readiness report must run even after required setup failure")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("workflow", type=Path)
    args = parser.parse_args()
    errors = validate(args.workflow)
    for error in errors:
        print(f"ERROR: {error}")
    if not errors:
        print("Single-job setup contract and actual consumers verified")
    return int(bool(errors))


if __name__ == "__main__":
    raise SystemExit(main())
