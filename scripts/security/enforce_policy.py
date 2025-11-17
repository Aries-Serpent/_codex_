#!/usr/bin/env python3
"""
Enforce security policy gates:
- Validate secrets baseline presence when required
- Run bandit and enforce severity threshold
- Run pip-audit JSON and enforce vulnerability caps

Exit code: 0 pass, 1 fail
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Tuple


def run(cmd: list[str]) -> Tuple[int, str, str]:
    p = subprocess.run(cmd, capture_output=True, text=True)
    return p.returncode, p.stdout, p.stderr


def bandit_check(threshold: str) -> Tuple[bool, str]:
    # Run bandit with JSON output
    code, out, err = run(["bandit", "-q", "-r", "src", "-f", "json"])
    if code not in (0, 1):  # bandit returns 1 on findings
        return False, f"Bandit failed: {err}"
    try:
        data = json.loads(out or "{}")
    except Exception:
        return False, "Bandit JSON parse error"
    severity_rank = {"none": 0, "low": 1, "medium": 2, "high": 3}
    max_allowed = severity_rank.get(threshold.lower(), 3)
    worst = 0
    for r in data.get("results", []):
        sev = r.get("issue_severity", "LOW").lower()
        worst = max(worst, severity_rank.get(sev, 1))
    ok = worst <= max_allowed
    return ok, f"bandit_worst={worst} allowed<={max_allowed}"


def pip_audit_check(max_critical: int, max_high: int) -> Tuple[bool, str]:
    code, out, err = run(["pip-audit", "-f", "json"])
    if code not in (0, 1):  # 1 means vulns found
        return False, f"pip-audit failed: {err}"
    try:
        data = json.loads(out or "[]")
    except Exception:
        return False, "pip-audit JSON parse error"
    crit = sum(
        1 for v in data for a in v.get("vulns", []) if a.get("severity", "").lower() == "critical"
    )
    high = sum(
        1 for v in data for a in v.get("vulns", []) if a.get("severity", "").lower() == "high"
    )
    ok = (crit <= max_critical) and (high <= max_high)
    return ok, f"pip_audit_critical={crit}/{max_critical} high={high}/{max_high}"


def main(argv=None) -> int:
    policy_path = Path("configs/security_policy.policy.json")
    if not policy_path.exists():
        print("[WARN] Policy not found; skipping enforcement")
        return 0

    # Validate policy file against schema (best-effort)
    if (
        Path("tools/schema_validate.py").exists()
        and Path("configs/schemas/security_policy.schema.json").exists()
    ):
        subprocess.call(
            [
                sys.executable,
                "tools/schema_validate.py",
                "--data",
                str(policy_path),
                "--schema",
                "configs/schemas/security_policy.schema.json",
            ]
        )

    policy = json.loads(policy_path.read_text(encoding="utf-8"))
    sast_fail_on = policy.get("sast", {}).get("bandit_fail_on", "high")
    baseline_required = bool(policy.get("secrets", {}).get("baseline_required", False))
    dep_caps = policy.get("dependencies", {})
    max_critical = int(dep_caps.get("max_critical", 0))
    max_high = int(dep_caps.get("max_high", 0))

    # Secrets baseline
    if baseline_required and not Path(".secrets.baseline").exists():
        print("[FAIL] .secrets.baseline required by policy but not found")
        return 1

    ok_b, msg_b = bandit_check(sast_fail_on)
    print(f"[bandit] {msg_b}")
    if not ok_b:
        return 1

    ok_p, msg_p = pip_audit_check(max_critical, max_high)
    print(f"[pip-audit] {msg_p}")
    if not ok_p:
        return 1

    print("[OK] Security policy enforcement passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
