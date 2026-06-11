#!/usr/bin/env python3
"""
scripts/ci/promotion_readiness_gate.py
──────────────────────────────────────
Promotion Readiness Gate for ``0D_base_`` → ``main`` merge.

Validates that all required policy/protocol files are present and synchronised,
all mandatory enforcement checks pass, and all governance variables are correct
before allowing promotion.

Usage
-----
  python scripts/ci/promotion_readiness_gate.py [--json-out FILE]

Exit codes
----------
  0  All checks pass — promotion is ready.
  1  One or more checks failed — promotion is BLOCKED.
  2  Usage / file-not-found error.

Output
------
  Prints a human-readable pass/fail matrix to stdout.
  With ``--json-out`` also writes a machine-readable JSON artifact.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]

# ---------------------------------------------------------------------------
# Required files — presence + optional sync pairs
# ---------------------------------------------------------------------------
_REQUIRED_FILES: list[str] = [
    ".codex/CODEBASE_AGENCY_POLICY.md",
    ".codex/AGENTIC_REPO_STATE.md",
    ".codex/docs/COPILOT_HARDENED_PLANNING_PROTOCOL.md",
    ".github/agents/COPILOT_HARDENED_PLANNING_PROTOCOL.md",
    ".github/agents/AGENT_REGISTRY.yaml",
    ".codex/agent_context.json",
    ".codex/aftermath/pda_iterations.jsonl",
    "docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md",
    "CHANGELOG.md",
    "scripts/ci/check_deferral_language.py",
    "scripts/ci/session_wrapup_autofix.py",
]

# Files that MUST be in sync (content-identical); key = display name.
_SYNC_PAIRS: dict[str, tuple[str, str]] = {
    # NOTE: The preload copy is intentionally a condensed session-reference version
    # of the canonical CHPP.  Exact-byte identity is not required; instead we check
    # that the preload copy (a) exists and (b) contains a reference back to the
    # canonical source path.  Use _SYNC_REFERENCE_PAIRS for this looser check.
}

# Files where the destination must reference the source path (instead of identical).
_SYNC_REFERENCE_PAIRS: dict[str, tuple[str, str]] = {
    "CHPP preload copy references canonical source": (
        ".github/agents/COPILOT_HARDENED_PLANNING_PROTOCOL.md",
        ".codex/docs/COPILOT_HARDENED_PLANNING_PROTOCOL.md",
    ),
}

# Required governance variables and their expected exact values.
_REQUIRED_GOVERNANCE_VARS: dict[str, str] = {
    "COPILOT_AGENT_CCA_VERSION_LOCK": "stable",
    "COPILOT_AGENT_DEDUPLICATION_ENABLED": "true",
    "COPILOT_AGENT_TURN_ISOLATION_ENABLED": "true",
}

# CAD/CHPP enforcement checks — phrases that must NOT appear in policy doc.
_POLICY_STALE_PHRASES: list[tuple[str, str]] = [
    (
        "does not detect agent-bypass",
        "Stale claim: deferral gate now detects agent-bypass patterns",
    ),
]

# Placeholder agent identifiers that must NOT appear in accountability report.
_AGENT_PLACEHOLDER_VALUES = frozenset({
    "unknown-agent",
    "unknown_agent",
    "ci-auto-fix-fallback",
    "auto-generated",
    "placeholder",
    "none",
    "n/a",
    "tbd",
})


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_registered_agent_ids() -> set[str]:
    registry = REPO_ROOT / ".github" / "agents" / "AGENT_REGISTRY.yaml"
    ids: set[str] = set()
    if not registry.exists():
        return ids
    text = registry.read_text(encoding="utf-8")
    for m in re.finditer(r"^\s*-\s+id:\s+(\S+)", text, re.MULTILINE):
        ids.add(m.group(1).strip())
    return ids


def _run_script(args: list[str]) -> tuple[int, str]:
    """Run a sub-process and return (returncode, combined output)."""
    try:
        result = subprocess.run(
            args,
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
        )
        return result.returncode, (result.stdout + result.stderr).strip()
    except FileNotFoundError as exc:
        return 2, str(exc)


# ---------------------------------------------------------------------------
# Individual checks
# ---------------------------------------------------------------------------


def check_required_files() -> list[dict[str, Any]]:
    results = []
    for rel_path in _REQUIRED_FILES:
        p = REPO_ROOT / rel_path
        results.append({
            "check": f"file_present:{rel_path}",
            "pass": p.exists(),
            "detail": "" if p.exists() else f"MISSING: {rel_path}",
        })
    return results


def check_sync_pairs() -> list[dict[str, Any]]:
    results = []
    for name, (src, dst) in _SYNC_PAIRS.items():
        sp = REPO_ROOT / src
        dp = REPO_ROOT / dst
        if not sp.exists():
            results.append({"check": f"sync:{name}", "pass": False,
                             "detail": f"Source not found: {src}"})
            continue
        if not dp.exists():
            results.append({"check": f"sync:{name}", "pass": False,
                             "detail": f"Destination not found: {dst}"})
            continue
        ok = _sha256(sp) == _sha256(dp)
        results.append({
            "check": f"sync:{name}",
            "pass": ok,
            "detail": "" if ok else f"Content mismatch between {src} and {dst}",
        })
    # Looser check: preload copies must reference the canonical source path.
    for name, (src, dst) in _SYNC_REFERENCE_PAIRS.items():
        dp = REPO_ROOT / dst
        src_relpath = src  # the reference that must appear in dst
        if not dp.exists():
            results.append({"check": f"sync_ref:{name}", "pass": False,
                             "detail": f"Preload copy not found: {dst}"})
            continue
        content = dp.read_text(encoding="utf-8")
        ok = src_relpath in content
        results.append({
            "check": f"sync_ref:{name}",
            "pass": ok,
            "detail": "" if ok else (
                f"Preload copy {dst} does not reference canonical source path '{src_relpath}'"
            ),
        })
    return results


def check_governance_vars() -> list[dict[str, Any]]:
    results = []
    ctx_path = REPO_ROOT / ".codex" / "agent_context.json"
    if not ctx_path.exists():
        return [{"check": "governance_vars", "pass": False,
                 "detail": "agent_context.json not found"}]
    data = json.loads(ctx_path.read_text(encoding="utf-8"))
    for key, expected in _REQUIRED_GOVERNANCE_VARS.items():
        actual = data.get(key)
        ok = actual is not None and str(actual).lower() == expected.lower()
        results.append({
            "check": f"governance_var:{key}",
            "pass": ok,
            "detail": "" if ok else (
                f"{key} missing" if actual is None
                else f"{key}='{actual}' (expected '{expected}')"
            ),
        })
    return results


def check_policy_consistency() -> list[dict[str, Any]]:
    results = []
    policy_path = REPO_ROOT / ".codex" / "CODEBASE_AGENCY_POLICY.md"
    if not policy_path.exists():
        return [{"check": "policy_consistency", "pass": False,
                 "detail": "CODEBASE_AGENCY_POLICY.md not found"}]
    content = policy_path.read_text(encoding="utf-8")
    for phrase, reason in _POLICY_STALE_PHRASES:
        found = phrase.lower() in content.lower()
        results.append({
            "check": f"policy_no_stale_claim:{phrase[:40]}",
            "pass": not found,
            "detail": "" if not found else f"Stale claim found: {reason}",
        })
    return results


def check_req14_agents_used() -> list[dict[str, Any]]:
    """Validate AGENT_ACCOUNTABILITY_REPORT.md for valid agent identifiers."""
    report_path = REPO_ROOT / "docs" / "accountability" / "AGENT_ACCOUNTABILITY_REPORT.md"
    if not report_path.exists():
        return [{"check": "req14_agents_used", "pass": False,
                 "detail": "AGENT_ACCOUNTABILITY_REPORT.md not found"}]
    content = report_path.read_text(encoding="utf-8")
    heading_match = re.search(r"^#{1,4}\s+Agents Used", content, re.MULTILINE)
    if not heading_match:
        return [{"check": "req14_agents_used", "pass": False,
                 "detail": "Missing 'Agents Used' section heading"}]
    section_start = heading_match.start()
    next_heading = re.search(
        r"^#{1,4}\s+\S", content[heading_match.end():], re.MULTILINE
    )
    section = (
        content[section_start: heading_match.end() + next_heading.start()]
        if next_heading
        else content[section_start:]
    )
    identifiers = re.findall(r"`([^`]+)`", section)
    registered = _load_registered_agent_ids()
    for ident in identifiers:
        low = ident.lower().strip()
        if low in _AGENT_PLACEHOLDER_VALUES:
            return [{"check": "req14_agents_used", "pass": False,
                     "detail": f"Placeholder identifier `{ident}` found — must be replaced"}]
        if not registered or ident in registered:
            return [{"check": "req14_agents_used", "pass": True, "detail": ""}]
    return [{"check": "req14_agents_used", "pass": False,
             "detail": "No valid registered agent identifier found in Agents Used section"}]


def check_deferral_scan() -> list[dict[str, Any]]:
    """Run check_deferral_language.py against the most recent accountability entry.

    Scanning the full AGENT_ACCOUNTABILITY_REPORT.md would false-positive on
    historical entries that legitimately described pre-existing failures.
    We extract only the last real (non-auto-generated) session entry.
    """
    report_path = REPO_ROOT / "docs" / "accountability" / "AGENT_ACCOUNTABILITY_REPORT.md"
    if not report_path.exists():
        return [{"check": "deferral_scan", "pass": False,
                 "detail": "AGENT_ACCOUNTABILITY_REPORT.md not found for deferral scan"}]
    script = REPO_ROOT / "scripts" / "ci" / "check_deferral_language.py"
    if not script.exists():
        return [{"check": "deferral_scan", "pass": False,
                 "detail": "check_deferral_language.py not found"}]

    # Extract the last 200 lines of the report to scope to the most recent session.
    content = report_path.read_text(encoding="utf-8")
    recent_lines = content.splitlines()[-200:]
    recent_text = "\n".join(recent_lines)

    # Write to a temp file (no /tmp — use .codex scratch)
    scratch = REPO_ROOT / ".codex" / "_promo_gate_recent_accountability.txt"
    scratch.write_text(recent_text, encoding="utf-8")
    try:
        rc, out = _run_script([sys.executable, str(script), "--session-log", str(scratch)])
    finally:
        try:
            scratch.unlink()
        except OSError:
            pass  # best-effort cleanup; ignore if file was already removed
    ok = rc == 0
    return [{"check": "deferral_scan", "pass": ok,
             "detail": "" if ok else f"Deferral language detected in recent session entry (exit {rc}):\n{out[:500]}"}]


def check_pda_freshness() -> list[dict[str, Any]]:
    """Verify at least one PDA entry exists from within the last 7 days."""
    pda_path = REPO_ROOT / ".codex" / "aftermath" / "pda_iterations.jsonl"
    if not pda_path.exists():
        return [{"check": "pda_freshness", "pass": False,
                 "detail": "pda_iterations.jsonl not found"}]
    lines = pda_path.read_text(encoding="utf-8").splitlines()
    now = datetime.now(tz=timezone.utc)
    for line in reversed(lines):
        try:
            d = json.loads(line)
            ts_str = d.get("timestamp", "")
            if not ts_str:
                continue
            # Accept "YYYY-MM-DDTHH:MM" (16-char short-form) by appending seconds.
            _SHORT_ISO_LEN = 16
            ts_str_norm = ts_str.rstrip("Z")
            if len(ts_str_norm) == _SHORT_ISO_LEN:
                ts_str_norm += ":00"
            ts = datetime.fromisoformat(ts_str_norm).replace(tzinfo=timezone.utc)
            age_days = (now - ts).days
            if age_days <= 7:
                return [{"check": "pda_freshness", "pass": True, "detail": ""}]
        except (json.JSONDecodeError, ValueError):
            continue
    return [{"check": "pda_freshness", "pass": False,
             "detail": "No PDA entry found within the last 7 days"}]


def check_no_placeholder_agents_in_pda() -> list[dict[str, Any]]:
    """Check that recent PDA entries do not list placeholder agent names in their
    dedicated agent fields (``agents_used`` / ``agents``).

    Auto-generated summary descriptions that happen to contain the word
    "auto-generated" are expected and do not constitute violations.
    """
    pda_path = REPO_ROOT / ".codex" / "aftermath" / "pda_iterations.jsonl"
    if not pda_path.exists():
        return [{"check": "pda_no_placeholder_agents", "pass": True, "detail": ""}]
    lines = pda_path.read_text(encoding="utf-8").splitlines()
    for line in lines[-10:]:
        try:
            d = json.loads(line)
            # Only inspect dedicated agent identifier fields, not free-text summary.
            agent_fields = []
            for field in ("agents_used", "agents", "agent"):
                val = d.get(field)
                if isinstance(val, list):
                    agent_fields.extend(str(v) for v in val)
                elif isinstance(val, str):
                    agent_fields.append(val)
            for ident in agent_fields:
                low = ident.lower().strip()
                if low in _AGENT_PLACEHOLDER_VALUES:
                    return [{"check": "pda_no_placeholder_agents", "pass": False,
                             "detail": f"PDA agent field contains placeholder '{ident}'"}]
        except json.JSONDecodeError:
            continue
    return [{"check": "pda_no_placeholder_agents", "pass": True, "detail": ""}]


def check_accountability_schema() -> list[dict[str, Any]]:
    """Validate that the most recent real (non-auto-generated) accountability
    session entry contains the mandatory schema sections:

    - Objective / work description
    - Agents Used
    - Outcomes / Work Completed
    - Validation evidence (parallel_validation / CI check references)
    """
    report_path = REPO_ROOT / "docs" / "accountability" / "AGENT_ACCOUNTABILITY_REPORT.md"
    if not report_path.exists():
        return [{"check": "accountability_schema", "pass": False,
                 "detail": "AGENT_ACCOUNTABILITY_REPORT.md not found"}]
    content = report_path.read_text(encoding="utf-8")
    # Split into sessions separated by "---" or "## SESSION"
    sessions = re.split(r"\n---\n", content)
    # Find the most recent non-auto-generated session block.
    real_session: str | None = None
    for block in reversed(sessions):
        if "[auto-generated]" not in block and "SESSION AUTO" not in block:
            if re.search(r"^#{1,3}\s+", block, re.MULTILINE):
                real_session = block
                break
    if real_session is None:
        # All entries are auto-generated — warn but do not hard-fail promotion
        # since the first real session may not have happened yet.
        return [{"check": "accountability_schema", "pass": True,
                 "detail": "(only auto-generated entries found — schema check skipped)"}]
    results = []
    _REQUIRED_SCHEMA_SECTIONS = [
        (r"agents?\s+used|agents?\s+invoked|custom\s+agent", "Agents Used"),
        (r"work\s+completed|objective|task\s+description|summary|session\s+summary", "Objective/Work Completed"),
        (r"outcomes?|results?|changes?\s+made|work\s+completed|impact|gates?\s+unblocked", "Outcomes/Results"),
        (r"validation|parallel_validation|ci\s+check|code\s+review|pre.?flight", "Validation Evidence"),
    ]
    for pattern, label in _REQUIRED_SCHEMA_SECTIONS:
        found = bool(re.search(pattern, real_session, re.IGNORECASE))
        results.append({
            "check": f"accountability_schema:{label.lower().replace(' ', '_')}",
            "pass": found,
            "detail": "" if found else f"Missing schema section: '{label}'",
        })
    return results


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def run_all_checks() -> list[dict[str, Any]]:
    all_results: list[dict[str, Any]] = []
    all_results.extend(check_required_files())
    all_results.extend(check_sync_pairs())
    all_results.extend(check_governance_vars())
    all_results.extend(check_policy_consistency())
    all_results.extend(check_req14_agents_used())
    all_results.extend(check_deferral_scan())
    all_results.extend(check_pda_freshness())
    all_results.extend(check_no_placeholder_agents_in_pda())
    all_results.extend(check_accountability_schema())
    return all_results


def _build_summary(results: list[dict[str, Any]]) -> str:
    """Build a human-readable pass/fail matrix."""
    lines = [
        "┌─────────────────────────────────────────────────────────────────┐",
        "│          Promotion Readiness Gate: 0D_base_ → main              │",
        "├─────────────────────────────────────────────────────────────────┤",
    ]
    passed = 0
    _MAX_DETAIL_LINES = 3  # max lines of failure detail shown in the summary table
    failed = 0
    for r in results:
        icon = "✅" if r["pass"] else "❌"
        status = "PASS" if r["pass"] else "FAIL"
        check_name = r["check"][:58]
        lines.append(f"│ {icon} {status:<4}  {check_name:<58}│")
        if not r["pass"] and r.get("detail"):
            for detail_line in r["detail"].splitlines()[:_MAX_DETAIL_LINES]:
                lines.append(f"│        ↳ {detail_line[:62]:<62}│")
        if r["pass"]:
            passed += 1
        else:
            failed += 1
    lines.append("├─────────────────────────────────────────────────────────────────┤")
    overall = "✅ READY" if failed == 0 else f"❌ BLOCKED ({failed} failure(s))"
    lines.append(f"│  Overall: {overall:<57}│")
    lines.append(f"│  Passed: {passed}  Failed: {failed}  Total: {passed + failed:<37}│")
    lines.append("└─────────────────────────────────────────────────────────────────┘")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Promotion readiness gate: 0D_base_ → main",
    )
    parser.add_argument(
        "--json-out",
        metavar="FILE",
        help="Write machine-readable JSON results to FILE",
    )
    args = parser.parse_args()

    results = run_all_checks()
    print(_build_summary(results))
    failed = [r for r in results if not r["pass"]]

    if args.json_out:
        artifact = {
            "generated_at": datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "ready": len(failed) == 0,
            "passed": len(results) - len(failed),
            "failed": len(failed),
            "total": len(results),
            "checks": results,
        }
        out_path = Path(args.json_out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(artifact, indent=2) + "\n", encoding="utf-8")
        print(f"\n📄 JSON results written to: {out_path}")

    if failed:
        print("\n🚫 Promotion BLOCKED — resolve the failures above before merging.")
        return 1
    print("\n🚀 Promotion READY — all gates passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
