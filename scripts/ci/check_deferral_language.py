#!/usr/bin/env python3
"""
scripts/ci/check_deferral_language.py
──────────────────────────────────────
Deferral-Language Enforcement Gate
Enforces the AI Codebase Agency Policy (`.codex/CODEBASE_AGENCY_POLICY.md`).

TRIGGER RULE (mandatory for ALL agents):
  Any phrase in DEFERRAL_TRIGGERS found in a PR body, commit message, or
  agent session log is a policy violation.  The gate FAILS and the agent
  MUST:
    1. Load `.codex/CODEBASE_AGENCY_POLICY.md`
    2. Load the latest `docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md`
    3. Fix the issue immediately — no exceptions for branch/PR/agent origin

Usage:
  python scripts/ci/check_deferral_language.py --pr-body FILE
  python scripts/ci/check_deferral_language.py --commit-msg FILE
  python scripts/ci/check_deferral_language.py --session-log FILE
  python scripts/ci/check_deferral_language.py --text "raw text to scan"

Exit codes:
  0  — no deferral language found
  1  — deferral language detected (policy violation)
  2  — usage / file-not-found error
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# ── Canonical deferral trigger phrases ────────────────────────────────────────
# These are the exact patterns that constitute policy violations.
# Edit only via PR with AGENT_ACCOUNTABILITY_REPORT update.
DEFERRAL_TRIGGERS: list[tuple[str, str]] = [
    # Attribution-based deferrals
    (r"this was from (?:a )?different (?:branch|agent|pr|pull request|task|session)",
     "Attribution deferral: blaming origin instead of fixing"),
    (r"not (?:from|in) (?:our|the) current (?:pr|branch|feature|task)",
     "Attribution deferral: scoping out current responsibility"),
    (r"(?:pre-?existing|pre-existing) (?:issue|code|problem|bug|error|concern)",
     "Pre-existing deferral: refusing pre-existing issues"),
    (r"(?:introduced|added|created) by (?:a )?(?:different|another|previous|other) (?:agent|pr|session|task|commit)",
     "Origin deferral: deflecting to another agent/session"),
    (r"not introduced by (?:this|my|our)",
     "Origin deferral: deflecting to another source"),
    # Scope-based deferrals
    (r"(?:not|out of|outside)(?: the)? scope(?: of this| of my)?",
     "Scope deferral: scoping out responsibility"),
    (r"not related to (?:this|my|our|the current) (?:pr|task|branch|change)",
     "Scope deferral: claiming issue is unrelated"),
    (r"not (?:directly )?related to (?:my|our|this) (?:change|work|fix|commit)",
     "Scope deferral: claiming issue is unrelated"),
    (r"(?:is|are|was|were) not (?:my|our) (?:problem|responsibility|concern|task)",
     "Responsibility deferral: refusing ownership"),
    # Future-based deferrals
    (r"(?:will|can|could|should|may)(?: be)? (?:address|fix|resolve|handle)(?:ed|d)? in (?:a )?future",
     "Future deferral: punting to future work without documented justification"),
    (r"future (?:pr\b|task\b|session\b|iteration\b|sprint\b|phase\b|work\b|fix\b|improvement\b)",
     "Future deferral: punting to future work"),
    (r"address(?:ed)? (?:incrementally|later|separately|in a follow[-\s]?up)",
     "Incremental deferral: incrementalism as avoidance"),
    (r"follow[-\s]?up (?:pr\b|task\b|issue\b|ticket\b)",
     "Follow-up deferral: creating follow-up instead of fixing"),
    (r"(?:can|will) be (?:addressed|fixed|resolved) (?:separately|later|next)",
     "Deferred fix: explicit future-assignment"),
    # "Residual" deferral without documented mitigation
    (r"residual (?:risk|issue|concern|problem)(?! — | - |\. Mitigation)",
     "Residual risk: documented without mitigation"),
    # Deprecation without tombstone
    (r"not actionable in this (?:pr|task|session|iteration)",
     "Non-actionable claim: must provide documented mitigation"),
    (r"(?:too|very) broad (?:for|to|in) (?:this|the current)",
     "Broad-scope deferral: claiming scope is too broad to fix"),
    (r"pre-?existing and safe",
     "Safety assumption without verification"),
    (r"(?:another|a different|the previous) (?:session|agent|team|pr) (?:should|will|can|must)",
     "Responsibility delegation to another agent/session"),
]

# ── Allowed exemptions (phrases that appear in policy/accountability docs themselves) ──
EXEMPTION_PATTERNS: list[str] = [
    r"DEFERRAL_TRIGGERS",           # this script's own source
    r"check_deferral_language",     # this script name
    r"deferral.language.gate",      # workflow name
    r"Prohibited Statements",       # policy itself listing what's prohibited
    r"#\s*noqa:\s*deferral",        # explicit per-line suppression
    r"noqa.*deferral",
]


def _load_text(source: str | Path) -> str:
    """Load text from a file path or return the string directly."""
    path = Path(source)
    if path.exists():
        return path.read_text(encoding="utf-8", errors="replace")
    return str(source)


def _line_is_exempt(line: str) -> bool:
    """Return True if the line is covered by an exemption pattern."""
    return any(re.search(p, line, re.IGNORECASE) for p in EXEMPTION_PATTERNS)


def scan(text: str, source_label: str = "<input>") -> list[dict]:
    """
    Scan *text* for deferral language.

    Returns a list of violation dicts with keys: line_no, line, pattern, reason.
    """
    violations: list[dict] = []
    for line_no, line in enumerate(text.splitlines(), start=1):
        if _line_is_exempt(line):
            continue
        for pattern, reason in DEFERRAL_TRIGGERS:
            if re.search(pattern, line, re.IGNORECASE):
                violations.append(
                    {
                        "source": source_label,
                        "line_no": line_no,
                        "line": line.strip(),
                        "pattern": pattern,
                        "reason": reason,
                    }
                )
                break  # one violation per line is enough
    return violations


def _format_violation(v: dict) -> str:
    return (
        f"  {v['source']}:{v['line_no']}: {v['reason']}\n"
        f"    TEXT: {v['line'][:120]}\n"
    )


def _print_policy_reminder() -> None:
    print(
        "\n"
        "═══════════════════════════════════════════════════════════════════\n"
        "  🚨 CODEBASE AGENCY POLICY VIOLATION — DEFERRAL LANGUAGE DETECTED\n"
        "═══════════════════════════════════════════════════════════════════\n"
        "\n"
        "  MANDATORY IMMEDIATE ACTIONS (no exceptions):\n"
        "\n"
        "  1. 🔃 LOAD: .codex/CODEBASE_AGENCY_POLICY.md\n"
        "  2. 🔃 LOAD: docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md\n"
        "  3. 🔃 LOAD: All stored memories from previous sessions\n"
        "  4. FIX the deferred issue NOW — branch/PR/agent origin is irrelevant\n"
        "\n"
        "  PROHIBITED (per policy §2 'Comprehensive Issue Resolution'):\n"
        "    ❌ 'This was from a different branch'\n"
        "    ❌ 'This is a pre-existing issue'\n"
        "    ❌ 'Not related to my PR'\n"
        "    ❌ 'Will address in a future PR/session'\n"
        "    ❌ 'Out of scope'\n"
        "\n"
        "  Full policy: .codex/CODEBASE_AGENCY_POLICY.md\n"
        "═══════════════════════════════════════════════════════════════════\n",
        file=sys.stderr,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Scan text for deferral language (Codebase Agency Policy enforcement)"
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--pr-body", metavar="FILE", help="Path to PR body text file")
    group.add_argument("--commit-msg", metavar="FILE", help="Path to commit message file")
    group.add_argument("--session-log", metavar="FILE", help="Path to agent session log")
    group.add_argument("--text", metavar="TEXT", help="Raw text string to scan")
    group.add_argument(
        "--git-log",
        action="store_true",
        help="Scan last 10 commit messages via git log",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        default=True,
        help="Exit 1 on any violation (default: True)",
    )
    parser.add_argument(
        "--warn-only",
        action="store_true",
        help="Print violations but exit 0 (informational mode)",
    )
    args = parser.parse_args(argv)

    all_violations: list[dict] = []

    if args.pr_body:
        path = Path(args.pr_body)
        if not path.exists():
            print(f"ERROR: File not found: {path}", file=sys.stderr)
            return 2
        all_violations += scan(path.read_text(encoding="utf-8"), f"PR body ({path.name})")

    elif args.commit_msg:
        path = Path(args.commit_msg)
        if not path.exists():
            print(f"ERROR: File not found: {path}", file=sys.stderr)
            return 2
        all_violations += scan(path.read_text(encoding="utf-8"), f"commit msg ({path.name})")

    elif args.session_log:
        path = Path(args.session_log)
        if not path.exists():
            print(f"ERROR: File not found: {path}", file=sys.stderr)
            return 2
        all_violations += scan(path.read_text(encoding="utf-8"), f"session log ({path.name})")

    elif args.text:
        all_violations += scan(args.text, "<inline>")

    elif args.git_log:
        import subprocess  # noqa: PLC0415
        try:
            result = subprocess.run(  # noqa: S603
                ["git", "log", "--format=%B", "-n", "10"],  # noqa: S607
                capture_output=True, text=True, check=True,
            )
            all_violations += scan(result.stdout, "git log (last 10 commits)")
        except subprocess.CalledProcessError as exc:
            print(f"ERROR: git log failed: {exc}", file=sys.stderr)
            return 2

    if all_violations:
        _print_policy_reminder()
        print(f"Found {len(all_violations)} deferral language violation(s):\n")
        for v in all_violations:
            print(_format_violation(v))
        if args.warn_only:
            print("⚠️  warn-only mode: exiting 0 despite violations", file=sys.stderr)
            return 0
        return 1

    print("✅ No deferral language detected.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
