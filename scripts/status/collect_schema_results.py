#!/usr/bin/env python3
"""
Collect Schema Results

Purpose:
    Main execution script

Usage:
    python scripts/status/collect_schema_results.py [options]

    Examples:
    $ python scripts/status/collect_schema_results.py --help

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


def validate_pair(data: str, schema: str, tool: str) -> dict:
    cmd = [sys.executable, "tools/schema_validate.py", "--data", data, "--schema", schema]
    code = subprocess.call(cmd)
    return {
        "target": data,
        "schema": schema,
        "tool": tool,
        "status": "PASS" if code == 0 else "FAIL",
        "findings": "" if code == 0 else "See workflow logs",
        "severity": 3 if code == 0 else 4,
        "remediation": "" if code == 0 else "Align fields/types with schema",
    }


def main(argv=None) -> int:
    results: list[dict] = []
    pairs = [
        (
            "configs/training/base.yaml",
            "configs/schemas/training.schema.yaml",
            "tools/schema_validate.py",
        ),
        (
            "configs/training/profiles/default.yaml",
            "configs/schemas/training_profile.schema.json",
            "tools/schema_validate.py",
        ),
        (
            "runs/examples/evaluation.json",
            "configs/schemas/evaluation.schema.json",
            "tools/schema_validate.py",
        ),
        (
            "runs/examples/checkpoint_manifest.json",
            "configs/schemas/checkpoint_manifest.schema.json",
            "tools/schema_validate.py",
        ),
    ]
    for data, schema, tool in pairs:
        if Path(data).exists() and Path(schema).exists():
            results.append(validate_pair(data, schema, tool))

    out = {"schema_validation_results": results}
    Path("schema_validation_results.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    print("[OK] Wrote schema_validation_results.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
