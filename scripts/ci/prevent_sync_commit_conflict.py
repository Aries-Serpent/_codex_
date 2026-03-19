#!/usr/bin/env python3
"""
Prevent Sync+New-Work Rebase Conflict Anti-Pattern

Detects when a commit (or staged changes) mixes:
  1. Sync changes — content copied from remote auto-generated commits
  2. Development changes — new S-session work

This anti-pattern causes rebase conflicts because report_progress rebases
the local commit onto the remote, and both sides try to modify the same lines.

Root Cause Session: S154 — PR #3628 — 2026-03-18
Documentation: .codex/docs/SYNC_COMMIT_CONFLICT_PREVENTION.md

Usage:
    python scripts/ci/prevent_sync_commit_conflict.py          # check staged changes
    python scripts/ci/prevent_sync_commit_conflict.py --ci-mode # exit 1 on detect
    python scripts/ci/prevent_sync_commit_conflict.py --diff <file>  # check specific diff

Exit codes:
    0 = clean (no anti-pattern detected, or only warnings issued)
    1 = anti-pattern detected in --ci-mode
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path
from typing import NamedTuple

# Files that are exclusively managed by CI workflows and should NOT appear
# in development commits alongside real changes.
AUTO_GENERATED_FILES = {
    "CODEX_MANIFEST.json",
    ".codex/session_context_latest.md",
    ".codex/agent_auth_session.json",
}

# Markers that indicate auto-generated CHANGELOG content
AUTO_GENERATED_MARKERS = [
    "[auto-generated]",
    "session_wrapup_autofix.py",
    "cognitive-preflight",
    "(auto-update — PR #",
    "[CI Auto-Fix",
]

# Markers that indicate real development work in CHANGELOG
DEVELOPMENT_MARKERS = [
    r"### Fixed \(S\d{3}",       # ### Fixed (S153 — ...)
    r"### Added \(S\d{3}",        # ### Added (S154 — ...)
    r"### Changed \(S\d{3}",      # ### Changed (S150 — ...)
    r"\*\*Phase \d",              # **Phase 5...
    r"iterative-self-healing",
    r"codex-manifest-refresh",
    r"ci-failure-resolution",
]


class ConflictRisk(NamedTuple):
    file: str
    reason: str
    severity: str   # "error" | "warning"
    remediation: str


def get_staged_diff() -> str:
    """Return the full staged diff (git diff --cached).

    Uses --unified=3 (3 context lines) so that detection logic depending on
    nearby context — e.g. spotting '## [Unreleased]' above an inserted '###'
    heading — has the surrounding lines available in the hunk.
    """
    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--unified=3"],
            capture_output=True, text=True, check=False
        )
        return result.stdout
    except Exception:
        return ""


def get_staged_files() -> list[str]:
    """Return list of staged file paths."""
    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only"],
            capture_output=True, text=True, check=False
        )
        return [f.strip() for f in result.stdout.strip().splitlines() if f.strip()]
    except Exception:
        return []


def extract_file_diff(full_diff: str, filename: str) -> str:
    """Extract the diff hunk for a specific file from a full diff."""
    lines = full_diff.splitlines()
    in_file = False
    file_lines: list[str] = []
    for line in lines:
        if line.startswith("diff --git") and filename in line:
            in_file = True
        elif line.startswith("diff --git") and in_file:
            break
        if in_file:
            file_lines.append(line)
    return "\n".join(file_lines)


def check_changelog_diff(diff_text: str) -> list[ConflictRisk]:
    """
    Detect sync+new-work anti-pattern in a CHANGELOG diff.

    The anti-pattern: diff adds BOTH auto-generated markers AND development
    markers in the same diff, especially near the [Unreleased] header.
    """
    risks: list[ConflictRisk] = []
    if not diff_text:
        return risks

    added_lines = [line[1:] for line in diff_text.splitlines()
                   if line.startswith("+") and not line.startswith("+++")]
    added_text = "\n".join(added_lines)

    has_auto_gen = any(marker in added_text for marker in AUTO_GENERATED_MARKERS)
    has_dev_work = any(re.search(pattern, added_text) for pattern in DEVELOPMENT_MARKERS)

    if has_auto_gen and has_dev_work:
        risks.append(ConflictRisk(
            file="CHANGELOG.md",
            reason=(
                "Staged diff adds BOTH auto-generated content "
                "(e.g., '### Fixed (auto-update — PR #N)') AND development changes "
                "(e.g., '### Fixed (S154 — PR #N)') in the same commit. "
                "When report_progress rebases onto the remote (which already has the "
                "auto-update section from session_wrapup_autofix.py), git sees "
                "both sides modifying the same lines → CONFLICT."
            ),
            severity="error",
            remediation=(
                "Remove the auto-generated section from your staged CHANGELOG.md. "
                "The remote already has it. Keep ONLY your development (S-session) entries. "
                "Move your S-session entries to BELOW existing [Unreleased] sections "
                "(after ### Fixed (S153...) etc.) to avoid conflicting hunks. "
                "See .codex/docs/SYNC_COMMIT_CONFLICT_PREVENTION.md"
            )
        ))

    # Check: is new content being inserted immediately after ## [Unreleased]?
    # In real diffs ## [Unreleased] appears BEFORE the inserted ### blocks.
    # We look for a hunk that adds a ### section within 5 lines of the
    # ## [Unreleased] header line in the diff context (lines starting with ' ' or '+').
    unreleased_hunk_start = re.search(
        r'^[ +]## \[Unreleased\].*?\n(?:[ +][^\n]*\n){0,5}\+### (Fixed|Added|Changed)',
        diff_text,
        re.MULTILINE,
    )
    if unreleased_hunk_start and has_dev_work and not has_auto_gen:
        risks.append(ConflictRisk(
            file="CHANGELOG.md",
            reason=(
                "Staged diff inserts development entries near the [Unreleased] header — "
                "the same location where session_wrapup_autofix.py inserts auto-update entries. "
                "If an auto-update commit exists on the remote branch, this will conflict."
            ),
            severity="warning",
            remediation=(
                "Consider placing new S-session entries AFTER existing sections "
                "(e.g., after ### Fixed (S153...) instead of before it) to avoid "
                "conflicting with the remote auto-update insertion. "
                "See Rule 2 in .codex/docs/SYNC_COMMIT_CONFLICT_PREVENTION.md"
            )
        ))

    return risks


def check_auto_generated_files(staged_files: list[str], changelog_risks: list[ConflictRisk]) -> list[ConflictRisk]:
    """
    Detect when auto-generated files are staged alongside development changes.
    """
    risks: list[ConflictRisk] = []
    staged_auto = [f for f in staged_files if any(f.endswith(ag) or ag in f for ag in AUTO_GENERATED_FILES)]
    staged_dev = [f for f in staged_files if f not in staged_auto and f != "CHANGELOG.md"]

    if staged_auto and staged_dev:
        for auto_file in staged_auto:
            risks.append(ConflictRisk(
                file=auto_file,
                reason=(
                    f"Auto-generated file '{auto_file}' is staged alongside development files "
                    f"({', '.join(staged_dev[:3])}...). "
                    "CI workflows manage this file automatically. When the remote branch "
                    "has a newer auto-generated version, rebasing will conflict."
                ),
                severity="warning",
                remediation=(
                    f"Run: git restore --staged {auto_file}  # unstage it\n"
                    f"The CI workflow will update {auto_file} automatically on push. "
                    "See .codex/docs/SYNC_COMMIT_CONFLICT_PREVENTION.md"
                )
            ))

    return risks


def check_codex_manifest(diff_text: str) -> list[ConflictRisk]:
    """Detect CODEX_MANIFEST.json timestamp conflict pattern."""
    risks: list[ConflictRisk] = []
    if not diff_text:
        return risks
    if '"generated_at"' in diff_text or '"integrity_sha256"' in diff_text:
        risks.append(ConflictRisk(
            file="CODEX_MANIFEST.json",
            reason=(
                "CODEX_MANIFEST.json staged with changes to 'generated_at' and/or "
                "'integrity_sha256'. The codex-manifest-refresh workflow regenerates "
                "this file on every push. If the remote already ran a refresh (which "
                "updates 'generated_at' and 'integrity_sha256'), your different values "
                "will cause a rebase conflict."
            ),
            severity="warning",
            remediation=(
                "Consider NOT staging CODEX_MANIFEST.json in development commits. "
                "Run: git restore --staged CODEX_MANIFEST.json\n"
                "The manifest-refresh workflow will update it on push automatically. "
                "See .codex/docs/SYNC_COMMIT_CONFLICT_PREVENTION.md"
            )
        ))
    return risks


def print_risk(risk: ConflictRisk, index: int) -> None:
    """Print a single conflict risk with formatting."""
    icon = "❌" if risk.severity == "error" else "⚠️"
    print(f"\n{icon} [{risk.severity.upper()}] Risk #{index+1}: {risk.file}")
    print(f"   Reason: {risk.reason}")
    print(f"   Fix: {risk.remediation}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Detect sync+new-work commit anti-pattern before report_progress"
    )
    parser.add_argument("--ci-mode", action="store_true",
                        help="Exit 1 on error-severity findings (for CI integration)")
    parser.add_argument("--diff", metavar="FILE",
                        help="Check a specific diff file instead of staged changes")
    args = parser.parse_args()

    print("🔍 Checking for sync+new-work commit anti-pattern...")
    print("   (See .codex/docs/SYNC_COMMIT_CONFLICT_PREVENTION.md)\n")

    if args.diff:
        full_diff = Path(args.diff).read_text()
        staged_files = []
    else:
        full_diff = get_staged_diff()
        staged_files = get_staged_files()

    if not full_diff and not staged_files:
        print("✅ No staged changes found — nothing to check.")
        return 0

    all_risks: list[ConflictRisk] = []

    # Check CHANGELOG.md
    changelog_diff = extract_file_diff(full_diff, "CHANGELOG.md")
    all_risks.extend(check_changelog_diff(changelog_diff))

    # Check auto-generated files staged alongside dev files
    all_risks.extend(check_auto_generated_files(staged_files, all_risks))

    # Check CODEX_MANIFEST.json
    manifest_diff = extract_file_diff(full_diff, "CODEX_MANIFEST.json")
    all_risks.extend(check_codex_manifest(manifest_diff))

    if not all_risks:
        print("✅ No sync+new-work anti-pattern detected. Safe to commit.")
        return 0

    errors = [r for r in all_risks if r.severity == "error"]
    warnings = [r for r in all_risks if r.severity == "warning"]

    print(f"Found {len(errors)} error(s) and {len(warnings)} warning(s):\n")
    for i, risk in enumerate(all_risks):
        print_risk(risk, i)

    print("\n━━━ Summary ━━━")
    print(f"  Errors:   {len(errors)}")
    print(f"  Warnings: {len(warnings)}")
    print("\n  See .codex/docs/SYNC_COMMIT_CONFLICT_PREVENTION.md for full guidance.")

    if errors:
        print("\n  ❌ Anti-pattern detected — resolve before calling report_progress")
        if args.ci_mode:
            return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
