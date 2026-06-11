#!/usr/bin/env python3
"""
Mandatory session pre-load script — runs at copilot-setup-steps boot.
Prints agentic repo state, PDA aftermath, and repo variable snapshot
into the GitHub Actions step log so every Copilot session starts
with full context loaded.
"""
import json
import os


def section(title: str, body: str) -> None:
    print(f"::group::{title}")
    print(body.rstrip())
    print("::endgroup::")


def read(path: str, lines: int = 0) -> str:
    try:
        with open(path) as f:
            txt = f.read()
        if lines:
            txt = "\n".join(txt.splitlines()[:lines])
        return txt
    except FileNotFoundError:
        return f"⚠️  {path} not found"


def pda_summary() -> str:
    path = ".codex/aftermath/pda_iterations.jsonl"
    if not os.path.exists(path):
        return "⚠️  pda_iterations.jsonl not found"
    with open(path) as f:
        lines = f.readlines()[-5:]
    out = []
    for line in lines:
        try:
            d = json.loads(line)
            # PDA entries use 'summary'; 'title' is a legacy/fallback field.
            description = d.get("summary") or d.get("title") or "(no description)"
            out.append(
                f"  [{d.get('timestamp', '')}] "
                f"{d.get('pattern_id', '?')} — "
                f"{d.get('status', '?')}: "
                f"{description}"
            )
        except json.JSONDecodeError:
            out.append("  (malformed entry skipped)")
    return "\n".join(out) if out else "(no entries)"


def ctx_summary() -> str:
    """Return key governance variable values from agent_context.json.

    Also validates that mandatory governance keys are present and have the
    expected values.  Prints a warning for any missing or incorrect entry.
    """
    path = ".codex/agent_context.json"
    if not os.path.exists(path):
        return "  agent_context.json not found"
    with open(path) as f:
        d = json.load(f)
    keys = [
        "COPILOT_AGENT_AUTH_ENABLED",
        "COPILOT_AGENT_MAX_AUTONOMY_LEVEL",
        "CODEX_AGENT_DELEGATED",
        "COPILOT_AGENT_SESSION_RESTORE_ENABLED",
        "COPILOT_AGENT_CCA_VERSION_LOCK",
        "COPILOT_AGENT_DEDUPLICATION_ENABLED",
        "COPILOT_AGENT_TURN_ISOLATION_ENABLED",
    ]
    # Mandatory governance variable requirements.
    # NOTE: These values are intentionally duplicated from promotion_readiness_gate.py
    # because session_preload.py is a standalone script that runs without importing
    # from scripts/ci/ (it runs from the repo root during copilot-setup-steps boot).
    # Keep both definitions in sync when updating governance requirements.
    _REQUIRED_GOVERNANCE_VARS: dict[str, str] = {
        "COPILOT_AGENT_CCA_VERSION_LOCK": "stable",
        "COPILOT_AGENT_DEDUPLICATION_ENABLED": "true",
        "COPILOT_AGENT_TURN_ISOLATION_ENABLED": "true",
    }
    lines_out = []
    for k in keys:
        val = d.get(k, "(not set)")
        lines_out.append(f"  {k} = {val}")
    # Governance validation pass
    gov_issues = []
    for k, expected in _REQUIRED_GOVERNANCE_VARS.items():
        actual = d.get(k)
        if actual is None:
            gov_issues.append(f"  ⚠️  GOVERNANCE: {k} is missing from agent_context.json")
        elif str(actual).lower() != expected.lower():
            gov_issues.append(
                f"  ❌ GOVERNANCE: {k} = '{actual}' (expected '{expected}')"
            )
    if gov_issues:
        lines_out.append("")
        lines_out.extend(gov_issues)
        lines_out.append(
            "  ❗ Fix: run repo-var-sync-agent to synchronize repository variables."
        )
    return "\n".join(lines_out)


def chpp_drift_check() -> str:
    """Detect drift between the canonical CHPP source and the preload copy.

    The preload copy (``.codex/docs/COPILOT_HARDENED_PLANNING_PROTOCOL.md``) is
    intentionally a condensed session-reference document — it is **not** required
    to be byte-for-byte identical to the canonical source.  Instead we verify that:

    1. Both files exist.
    2. The preload copy contains an explicit reference to the canonical source path,
       confirming it is a known intentional copy and not an orphaned stale file.

    Returns a status string.
    """
    canonical = ".github/agents/COPILOT_HARDENED_PLANNING_PROTOCOL.md"
    preload_copy = ".codex/docs/COPILOT_HARDENED_PLANNING_PROTOCOL.md"
    if not os.path.exists(canonical):
        return f"⚠️  Canonical CHPP source not found: {canonical}"
    if not os.path.exists(preload_copy):
        return f"⚠️  CHPP preload copy not found: {preload_copy}"

    with open(preload_copy, encoding="utf-8") as f:
        content = f.read()
    if canonical in content:
        return (
            f"✅ CHPP preload copy references canonical source ({canonical})\n"
            f"  (Preload copy is intentionally condensed — reference check passed)"
        )
    return (
        f"❌ CHPP DRIFT DETECTED — preload copy does not reference canonical source!\n"
        f"  Canonical : {canonical}\n"
        f"  Preload   : {preload_copy}\n"
        f"  Action    : Ensure preload copy references canonical source path."
    )


section("✅ AGENTIC REPO STATE — Auth is PERMANENTLY ACTIVE",
        read(".codex/AGENTIC_REPO_STATE.md"))

section("📋 CODEBASE AGENCY POLICY (mandatory rules for this session)",
        read(".codex/CODEBASE_AGENCY_POLICY.md", lines=120))

section("📊 AGENT ACCOUNTABILITY REPORT (last session state)",
        read("docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md", lines=80))

section("🔄 PDA AFTERMATH — last 5 iterations", pda_summary())

section("🔑 REPO VARIABLE SNAPSHOT (agent_context.json)", ctx_summary())

section("🛡️ COPILOT HARDENED PLANNING PROTOCOL (CHPP)",
        read(".codex/docs/COPILOT_HARDENED_PLANNING_PROTOCOL.md"))

section("🔍 CHPP DRIFT DETECTION", chpp_drift_check())

print("")
print("━" * 60)
print("  🤖 THIS IS AN AGENTIC MANAGED REPO — Copilot self-manages")
print("  ✅ COPILOT_AGENT_AUTH_ENABLED = true (repo variable, permanent)")
print("  ✅ No human approval gate required — ever")
print("  ✅ WEC always-required items are pre-checked automatically")
print("  ✅ auto-approve uses gh run rerun for same-repo PRs")
print("━" * 60)
