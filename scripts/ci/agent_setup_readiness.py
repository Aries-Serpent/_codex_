#!/usr/bin/env python3
"""Report observed bootstrap readiness without claiming hosted permissions."""

from __future__ import annotations

import importlib.metadata
import json
import os
import sys
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def read_json(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
        return value if isinstance(value, dict) else {}
    except (OSError, ValueError):
        return {}


def report(root: Path, outcomes: dict[str, str]) -> dict:
    assets = read_json(root / ".codex/lfs_assets_status.json")
    context = read_json(root / ".codex/runtime/context/status.json")
    required_ok = all(
        outcomes.get(key) == "success"
        for key in ("ASSET_OUTCOME", "PYTHON_OUTCOME", "INTENT_OUTCOME")
    ) and assets.get("status") in {"ready", "not-requested"}
    # Only allowlisted, non-secret observations are included.
    result = {
        "generated_at": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "status": "ready" if required_ok else "not-ready",
        "scope": "bootstrap only; task-specific tests and platform access remain unverified",
        "environment_type": outcomes.get("ENVIRONMENT_TYPE", "unknown"),
        "python": sys.version.split()[0],
        "assets": assets.get("status", "unknown"),
        "optional_context": context.get("status", "unavailable"),
        "optional_rag": context.get("rag", "unavailable"),
        "platform_access": "unverified",
        "missing_task_dependencies": [],
        "dependency_check": "installed distribution versions only; task imports/tests remain required",
    }
    if result["environment_type"] == "ml-heavy":
        try:
            sys.path.insert(0, str(root))
            from scripts.ci.environment_preflight import _load_runtime_dependencies
            from packaging.requirements import Requirement

            missing = []
            for dependency in _load_runtime_dependencies(root):
                requirement = Requirement(dependency)
                if requirement.marker and not requirement.marker.evaluate():
                    continue
                try:
                    version = importlib.metadata.version(requirement.name)
                    if not requirement.specifier.contains(version, prereleases=True):
                        missing.append(requirement.name)
                except importlib.metadata.PackageNotFoundError:
                    missing.append(requirement.name)
            result["missing_task_dependencies"] = missing
        except (ImportError, OSError, ValueError):
            result["missing_task_dependencies"] = ["dependency verification unavailable"]
    if required_ok and (
        context.get("status") != "available" or result["missing_task_dependencies"]
    ):
        result["status"] = "partial"
    return result


def main() -> int:
    result = report(ROOT, dict(os.environ))
    path = ROOT / ".codex/agent_setup_status.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    if summary := os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(summary, "a", encoding="utf-8") as handle:
            handle.write("## Observed setup readiness\n\n```json\n")
            handle.write(json.dumps(result, indent=2) + "\n```\n")
    print(json.dumps(result))
    return 1 if result["status"] == "not-ready" else 0


if __name__ == "__main__":
    raise SystemExit(main())
