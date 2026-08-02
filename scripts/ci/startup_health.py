#!/usr/bin/env python3
"""Build the deterministic startup health packet for a Copilot session."""

from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / ".codex" / "session_access_manifest.json"
CONTEXT = ROOT / ".codex" / "agent_context.json"
PACKET = ROOT / ".codex" / "session_startup_packet.json"


def _score(manifest: dict, context: dict, token_ok: bool) -> tuple[int, list[str]]:
    score = 100
    fixes: list[str] = []
    drift = manifest.get("branch_drift_severity", "UNKNOWN")
    if drift == "CRITICAL":
        score -= 30
        fixes.append("Rebase from latest main before editing")
    elif drift == "HIGH":
        score -= 15
        fixes.append("Review branch drift and enable sweep protection")
    elif drift == "UNKNOWN":
        fixes.append("Verify branch drift against origin/main")
    if not token_ok:
        score -= 5
        fixes.append("Review token-contract warnings")
    try:
        failure_rate = float(str(context.get("CODEX_CI_FAILURE_RATE", "0")).split(":")[0])
    except ValueError:
        failure_rate = 0
    try:
        threshold = float(context.get("CODEX_CI_FAILURE_THRESHOLD", 10))
    except (TypeError, ValueError):
        threshold = 10
    if failure_rate > threshold:
        score -= 10
        fixes.append("Investigate CI failure rate above threshold")
    return max(0, min(100, score)), fixes


def build_packet(
    manifest: dict | None = None, context: dict | None = None
) -> dict:
    """Build a packet with numeric CI rate; unavailable rates are ``None``."""
    manifest = manifest or (
        json.loads(MANIFEST.read_text(encoding="utf-8")) if MANIFEST.exists() else {}
    )
    context = context if context is not None else (
        json.loads(CONTEXT.read_text(encoding="utf-8")) if CONTEXT.exists() else {}
    )
    token_status = str(
        os.environ.get("TOKEN_CONTRACT_STATUS")
        or manifest.get("token_contract_status", "pass")
    )
    token_ok = token_status == "pass"
    ci_failure_rate_raw = str(context.get("CODEX_CI_FAILURE_RATE", "unknown"))
    rate_value, separator, rate_status = ci_failure_rate_raw.partition(":")
    try:
        ci_failure_rate_value = float(rate_value)
    except ValueError:
        ci_failure_rate_value = None
    ci_failure_status = (
        rate_status
        if separator and rate_value and ci_failure_rate_value is not None
        else None
    )
    score, fixes = _score(manifest, context, token_ok)
    packet = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "branch_drift_severity": manifest.get("branch_drift_severity", "UNKNOWN"),
        "main_commits_ahead": manifest.get("main_commits_ahead", 0),
        "ci_failure_rate": ci_failure_rate_value,
        "ci_failure_status": ci_failure_status,
        "ci_failure_rate_raw": ci_failure_rate_raw,
        "token_contract": token_status,
        "bootstrap_health_score": score,
        "status": "GREEN" if score >= 80 else "YELLOW" if score >= 50 else "RED",
        "must_fix_before_editing": fixes if score < 80 else [],
    }
    return packet


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=PACKET)
    args = parser.parse_args()
    packet = build_packet()
    args.output.write_text(json.dumps(packet, indent=2) + "\n", encoding="utf-8")
    gh_env = os.environ.get("GITHUB_ENV")
    if gh_env:
        with open(gh_env, "a", encoding="utf-8") as handle:
            handle.write(f"SESSION_BOOTSTRAP_HEALTH={packet['bootstrap_health_score']}\n")
            handle.write(f"BRANCH_DRIFT_SEVERITY={packet['branch_drift_severity']}\n")
    print(json.dumps(packet, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
