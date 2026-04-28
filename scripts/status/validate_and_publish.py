#!/usr/bin/env python3
"""
Validate And Publish

Purpose:
    Validates and_publish

Usage:
    python scripts/status/validate_and_publish.py [options]

    Examples:
    $ python scripts/status/validate_and_publish.py --help

Arguments:
    [To be documented]

Environment Variables:
    [To be documented]

Dependencies:
    [To be documented]

Exit Codes:
    0: Success
    1: Error

Author: Codex Team
Last Updated: 2026-01-16
"""


from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def run(cmd: list[str]) -> tuple[int, str, str]:
    p = subprocess.run(cmd, capture_output=True, text=True)
    return p.returncode, p.stdout, p.stderr


def main() -> int:
    root = Path(__file__).resolve().parents[2]

    results = {}

    # 1) Schema validation (pytest)
    schema_test = root / "tests/status/test_example_report_schema.py"
    if schema_test.exists():
        code, out, err = run(
            [sys.executable, "-m", "pytest", "-q", "tests/status/test_example_report_schema.py"]
        )
        results["status_schema"] = {"ok": code == 0, "stdout": out, "stderr": err}
    else:
        results["status_schema"] = {
            "ok": True,
            "stdout": "skipped: schema test file not found",
            "stderr": "",
        }

    # 2) Config validation (optional)
    schema_cfg = root / "configs/schemas/training.schema.yaml"
    cfg_root = root / "configs/training"
    if schema_cfg.exists() and cfg_root.exists():
        code, out, err = run(
            [
                sys.executable,
                str(root / "tools/validate_configs.py"),
                "--root",
                str(cfg_root),
                "--schema",
                str(schema_cfg),
            ]
        )
        results["config_validation"] = {"ok": code == 0, "stdout": out, "stderr": err}
    else:
        results["config_validation"] = {"ok": True, "stdout": "skipped", "stderr": ""}

    # 3) Audit integrity chain
    code, out, err = run([sys.executable, str(root / "scripts/audit/build_integrity_chain.py")])
    results["audit_chain"] = {"ok": code == 0, "stdout": out, "stderr": err}

    print(json.dumps(results, indent=2))
    return 0 if all(step.get("ok", False) for step in results.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
