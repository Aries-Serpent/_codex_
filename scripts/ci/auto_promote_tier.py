"""
scripts/ci/auto_promote_tier.py
Phase 5 — Dry-run REQ-N stub generator for automatic tier promotion.

Scans AGENT_REGISTRY.yaml for agents with enforcement_tier=SOFT that have
zero violations in the last 30 days (from SQLite agent_sessions). Generates
YAML stubs for new REQ-N gates — DRY-RUN ONLY, never modifies live files.

Usage:
  python scripts/ci/auto_promote_tier.py               # dry-run (default)
  python scripts/ci/auto_promote_tier.py --check-only  # exit 1 if any promotable
  python scripts/ci/auto_promote_tier.py --output /tmp/stubs/  # write stubs to dir

Output (dry-run):
  Prints REQ-N YAML stubs to stdout for human review.
  Does NOT modify any file in the repository.

Security note (Domain 8):
  This script MUST remain dry-run-only.  Auto-applying tier promotions without
  human review violates the security posture established in soft_to_GROUNDED.md.
"""

from __future__ import annotations

import argparse
import pathlib
import re
import sqlite3
import sys
import textwrap
import time
from typing import Any

import yaml

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
REGISTRY_PATH = REPO_ROOT / ".github" / "agents" / "AGENT_REGISTRY.yaml"
DB_PATH = REPO_ROOT / ".codex" / "codex_corpus.db"

# Minimum quiet period before suggesting promotion (30 days)
PROMOTION_QUIET_DAYS = 30


def _load_soft_agents() -> list[dict[str, Any]]:
    """Return agents with enforcement_tier=SOFT from the registry."""
    if not REGISTRY_PATH.exists():
        return []
    data = yaml.safe_load(REGISTRY_PATH.read_text(encoding="utf-8"))
    return [
        a
        for a in data.get("agents", [])
        if a.get("enforcement_tier") == "SOFT" and a.get("status") == "active"
    ]


def _get_violation_count(agent_id: str) -> int:
    """Query SQLite for violation count in last 30 days; returns 0 if DB absent."""
    if not DB_PATH.exists():
        return 0
    try:
        conn = sqlite3.connect(DB_PATH)
        rows = conn.execute(
            "SELECT COALESCE(SUM(violation_count), 0) FROM agent_sessions "
            "WHERE agent_id = ? AND start_time > datetime('now', '-30 days')",
            (agent_id,),
        ).fetchone()
        conn.close()
        return int(rows[0]) if rows else 0
    except Exception:  # noqa: BLE001
        return 0


def _next_req_number() -> int:
    """Find the next unused REQ-N number by scanning workflow files."""
    req_nums: list[int] = []
    for wf in sorted(REPO_ROOT.glob(".github/workflows/*.yml")):
        text = wf.read_text(encoding="utf-8", errors="ignore")
        for m in re.finditer(r"REQ-(\d+)", text):
            req_nums.append(int(m.group(1)))
    return max(req_nums, default=0) + 1


def generate_req_stub(agent_id: str, req_num: int) -> str:
    """Generate a YAML step stub for a new REQ-N gate (DRY-RUN output only)."""
    return textwrap.dedent(
        f"""\
        # REQ-{req_num}: Auto-generated tier promotion stub (DRY-RUN)
        # Agent: {agent_id}  |  Proposed: SOFT → PARTIAL
        # Generated: {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}
        # Action required: review + merge this step into cognitive-preflight job
        - name: "REQ-{req_num}: {agent_id} enforcement check (Canary Tier-2)"
          id: req{req_num}
          run: |
            # Verify {agent_id} emits ::warning:: on policy violations
            # (Tier-2 canary — promote to exit 1 after 2-sprint observation)
            python3 - << 'PYEOF'
        import pathlib, yaml, sys
        registry = yaml.safe_load(
            pathlib.Path('.github/agents/AGENT_REGISTRY.yaml').read_text())
        agent = next((a for a in registry['agents'] if a['id'] == '{agent_id}'), None)
        if not agent:
            print('::warning::REQ-{req_num}: {agent_id} not found in registry')
            sys.exit(0)
        tier = agent.get('enforcement_tier', 'SOFT')
        if tier == 'SOFT':
            print('::warning::REQ-{req_num}: {agent_id} still at SOFT tier — promote to PARTIAL')
        else:
            print(f'REQ-{req_num}: {{agent_id}} tier={{tier}} OK')
        PYEOF
        """
    )


def run(check_only: bool = False, output_dir: pathlib.Path | None = None) -> int:
    """
    Main dry-run logic.

    Args:
        check_only: If True, exit 1 when promotable agents are found.
        output_dir: If set, write stub files to this directory.

    Returns:
        Number of promotable agents found.
    """
    soft_agents = _load_soft_agents()
    if not soft_agents:
        print("✅ No SOFT-tier active agents found — nothing to promote.")
        return 0

    promotable: list[dict[str, Any]] = []
    for agent in soft_agents:
        agent_id = agent["id"]
        violations = _get_violation_count(agent_id)
        if violations == 0:
            promotable.append(agent)

    if not promotable:
        print(
            f"ℹ️  {len(soft_agents)} SOFT agents found, "
            f"but all have violations in last {PROMOTION_QUIET_DAYS} days — no stubs generated."
        )
        return 0

    print(
        f"⬆️  {len(promotable)} agent(s) qualify for SOFT→PARTIAL promotion "
        f"(0 violations in last {PROMOTION_QUIET_DAYS} days):\n"
    )

    next_req = _next_req_number()
    stubs: list[str] = []
    for i, agent in enumerate(promotable):
        req_num = next_req + i
        stub = generate_req_stub(agent["id"], req_num)
        stubs.append(stub)
        print(f"  [{i + 1}] {agent['id']}  →  REQ-{req_num}")
        if output_dir:
            output_dir.mkdir(parents=True, exist_ok=True)
            out_path = output_dir / f"REQ-{req_num}_{agent['id']}.yaml"
            out_path.write_text(stub, encoding="utf-8")
            print(f"       Written: {out_path}")

    print("\n── DRY-RUN STUBS ──────────────────────────────────────\n")
    for stub in stubs:
        print(stub)

    print(
        "── END DRY-RUN ───────────────────────────────────────\n"
        "⚠️  These stubs are for HUMAN REVIEW only.\n"
        "   Copy relevant steps into the cognitive-preflight job manually.\n"
        "   DO NOT auto-apply. (Domain 8 security posture)\n"
    )

    if check_only:
        print(
            f"::warning::auto_promote_tier: {len(promotable)} agent(s) "
            f"qualify for SOFT→PARTIAL promotion — review stubs above"
        )
        sys.exit(1)

    return len(promotable)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Dry-run tier promotion stub generator (SOFT→PARTIAL)")
    ap.add_argument(
        "--check-only",
        action="store_true",
        help="Exit 1 if any agents qualify for promotion (CI gate mode)",
    )
    ap.add_argument(
        "--output",
        type=pathlib.Path,
        default=None,
        help="Directory to write YAML stub files to",
    )
    args = ap.parse_args()
    run(check_only=args.check_only, output_dir=args.output)
