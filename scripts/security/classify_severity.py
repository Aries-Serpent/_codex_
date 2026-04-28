#!/usr/bin/env python
"""
Classify Severity

Purpose:
    Main execution script

Usage:
    python scripts/security/classify_severity.py [options]

    Examples:
    $ python scripts/security/classify_severity.py --help

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

import logging

logger = logging.getLogger(__name__)

import json
import os
import sys
from pathlib import Path
from typing import Any

ART_DIR = Path("audit_artifacts")
IN_REPORT = ART_DIR / "secret_entropy_report.json"
OUT_REPORT = ART_DIR / "security_severity.json"


def classify(entropy: float, length: int) -> str | None:
    if entropy >= 4.0 and 20 <= length <= 48:
        return "high"
    if entropy >= 3.8 and 16 <= length <= 48:
        return "medium"
    if entropy >= 3.5 and 16 <= length <= 48:
        return "low"
    return None


def main():
    enable = os.getenv("SECURITY_SEVERITY_ENABLE", "0") in {"1", "true", "TRUE", "on", "yes", "YES"}
    if not enable:
        print("[INFO] Security severity classification disabled.")
        return 0
    if not IN_REPORT.exists():
        print("[WARN] secret_entropy_report.json missing; run entropy scan first.", file=sys.stderr)
        return 2

    try:
        data = json.loads(IN_REPORT.read_text())
    except Exception as e:
        logger.debug(f"Exception: {e}")
        print(f"[ERR] Failed to parse entropy report: {e}", file=sys.stderr)
        return 2

    findings = data.get("findings", [])
    classified = []
    counts = {"high": 0, "medium": 0, "low": 0}
    for f in findings:
        token = f.get("span", "")
        entropy = float(f.get("entropy", 0.0))
        sev = classify(entropy, len(token))
        if sev:
            counts[sev] += 1
            classified.append(
                {
                    "file": f.get("file"),
                    "span": token[:80],
                    "entropy": entropy,
                    "length": len(token),
                    "severity": sev,
                }
            )

    total = sum(counts.values())
    weights = {
        "high": float(os.getenv("SEVERITY_HIGH_WEIGHT", "0.05")),
        "medium": float(os.getenv("SEVERITY_MEDIUM_WEIGHT", "0.02")),
        "low": float(os.getenv("SEVERITY_LOW_WEIGHT", "0.01")),
    }
    payload: dict[str, Any] = {
        "counts": counts | {"total": total},
        "weights": weights,
        "findings": classified,
    }
    ART_DIR.mkdir(parents=True, exist_ok=True)
    OUT_REPORT.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"[INFO] Security severity report written: {OUT_REPORT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
