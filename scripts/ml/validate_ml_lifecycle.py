"""
ML Lifecycle Validator — D2 exit criteria helper.

Usage:
    python scripts/ml/validate_ml_lifecycle.py --check reproducibility
    python scripts/ml/validate_ml_lifecycle.py --check serving
    python scripts/ml/validate_ml_lifecycle.py --check registry
    python scripts/ml/validate_ml_lifecycle.py --check all
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


def _ts() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def check_reproducibility() -> dict:
    """D2 #1 — verify reproducibility checklist items and E2E readiness."""
    checklist = Path("reports/reproducibility.md")
    items_done = 0
    total_items = 6

    if checklist.exists():
        text = checklist.read_text()
        items_done = text.count("✅")

    # Also check rollback procedure documentation
    rollback_exists = Path("docs/deployment/ROLLBACK_PROCEDURES.md").exists() or \
                      Path("docs/PRODUCTION_DEPLOYMENT_GUIDE.md").exists()

    passed = items_done >= 5 and rollback_exists
    return {
        "check": "reproducibility",
        "items_done": items_done,
        "total_items": total_items,
        "rollback_documented": rollback_exists,
        "passed": passed,
        "note": "reports/reproducibility.md must have ≥5/6 items ✅; rollback docs required",
    }


def check_serving() -> dict:
    """D2 #3 — run serving smoke test."""
    smoke_paths = [
        "tests/integration/test_serving_smoke.py",
        "tests/serving_tests/test_inference_serving.py",
        "scripts/ml/serving_smoke_test.py",
        "tests/test_serving.py",
    ]
    found = next((p for p in smoke_paths if Path(p).exists()), None)

    if not found:
        return {
            "check": "serving",
            "passed": False,
            "note": f"No smoke test file found in {smoke_paths}. Create one to satisfy D2 #3.",
        }

    result = subprocess.run(
        [sys.executable, "-m", "pytest", found, "-x", "-q", "--timeout=60"],
        capture_output=True, text=True, timeout=120,
    )
    return {
        "check": "serving",
        "file": found,
        "returncode": result.returncode,
        "passed": result.returncode == 0,
        "stdout_tail": result.stdout[-500:] if result.stdout else "",
    }


def check_registry() -> dict:
    """D2 #2 — verify model registry entries exist."""
    registry_indicators = [
        ".codex/models",
        "mlruns",
        "reports/model_registry.json",
    ]
    found = [p for p in registry_indicators if Path(p).exists()]
    return {
        "check": "registry",
        "found_paths": found,
        "passed": len(found) > 0,
        "note": "At least one of: .codex/models/, mlruns/, reports/model_registry.json must exist",
    }


def check_e2e() -> dict:
    """D2 #5 — verify E2E gate (train → eval → register → serve) components exist."""
    components = {
        "reproducibility": Path("reports/reproducibility.md").exists(),
        "model_registry": any(Path(p).exists() for p in [".codex/models", "mlruns"]),
        "serving_smoke_test": Path("tests/integration/test_serving_smoke.py").exists(),
        "rollback_procedure": Path("docs/deployment/ROLLBACK_PROCEDURES.md").exists(),
        "lifecycle_gate_workflow": Path(".github/workflows/ml-lifecycle-gate.yml").exists(),
    }
    all_present = all(components.values())
    return {
        "check": "e2e",
        "components": components,
        "passed": all_present,
        "note": "All E2E pipeline components must exist for D2 score 5",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="ML Lifecycle Validator")
    parser.add_argument("--check", choices=["reproducibility", "serving", "registry", "e2e", "all"],
                        default="all")
    parser.add_argument("--output", default=None)
    args = parser.parse_args()

    checks = {
        "reproducibility": check_reproducibility,
        "serving": check_serving,
        "registry": check_registry,
        "e2e": check_e2e,
    }

    if args.check == "all":
        results = {k: fn() for k, fn in checks.items()}
    else:
        results = {args.check: checks[args.check]()}

    report = {
        "generated_at": _ts(),
        "domain": "D2_ml_lifecycle",
        "checks": results,
        "all_passed": all(v.get("passed") for v in results.values()),
    }

    print(json.dumps(report, indent=2))

    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text(json.dumps(report, indent=2))

    if not report["all_passed"]:
        failed = [k for k, v in results.items() if not v.get("passed")]
        print(f"::warning::D2 ML Lifecycle: {len(failed)} check(s) failed: {failed}",
              file=sys.stderr)
        sys.exit(1)

    print("::notice::✅ D2 ML Lifecycle validator passed")


if __name__ == "__main__":
    main()
