#!/usr/bin/env python3
"""
enforce_actions_versions.py — Expected GitHub Actions version enforcer.

Scans all workflow files under .github/workflows/ and .github/misc/ and
verifies that every action `uses:` reference matches the approved version
policy.  Can auto-fix violations when run with --fix.

Usage
-----
    # Check only — exit 1 if violations found
    python scripts/ci/enforce_actions_versions.py

    # Auto-fix violations in place
    python scripts/ci/enforce_actions_versions.py --fix

    # Check with JSON output
    python scripts/ci/enforce_actions_versions.py --json

    # Only report, never fail (for advisory runs)
    python scripts/ci/enforce_actions_versions.py --warn-only

Exit codes
----------
    0  No violations (or --warn-only).
    1  Violations found and not fixed.
    2  Error reading/writing a file.

Policy
------
The EXPECTED_VERSIONS dict below is the single source of truth for
approved action versions in this repository.  Update it when a new
major version is published and validated.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

# ── Approved version policy ───────────────────────────────────────────────────
# Maps action name (owner/repo) → expected (minimum) version tag.
#
# Versions are validated as "must be >= MINIMUM_VERSIONS[action]" to allow
# forward-compat (e.g. v5 passes when minimum is v4).
# EXACT_VERSIONS overrides: the action MUST use exactly that version.
#
# Update when a new major version is audited and approved for this repo.
EXPECTED_VERSIONS: dict[str, str] = {
    # repo convention: v5 is the current standard (254 occurrences)
    "actions/checkout": "v5",
    # repo convention: v6 is the current standard (32 occurrences)
    "actions/setup-python": "v6",
    "actions/setup-node": "v4",
    # repo convention: v5 is the current standard (79 occurrences)
    "actions/upload-artifact": "v5",
    # repo convention: v5 is the current standard (10 occurrences)
    "actions/download-artifact": "v5",
    "actions/cache": "v5",
    "actions/github-script": "v8",
    "actions/configure-pages": "v5",
    "actions/deploy-pages": "v4",
    "actions/upload-pages-artifact": "v3",
    "github/codeql-action/init": "v3",
    "github/codeql-action/autobuild": "v3",
    "github/codeql-action/analyze": "v3",
}

# MINIMUM_VERSIONS: any version >= this integer is accepted.
# Built automatically from EXPECTED_VERSIONS (strip leading 'v', parse int).
def _min_ver(tag: str) -> int:
    try:
        return int(tag.lstrip("v").split(".")[0])
    except ValueError:
        return 0

MINIMUM_VERSIONS: dict[str, int] = {
    action: _min_ver(ver) for action, ver in EXPECTED_VERSIONS.items()
}

# Patterns that are always exempt (local composite actions, reusable workflows,
# fully-pinned SHA references, etc.)
_EXEMPT_PATTERNS: tuple[str, ...] = (
    r"^\./",            # local composite actions / reusable workflows
    r"^[0-9a-f]{40}$", # full SHA pin
)

# Regex to find `uses:` lines in YAML (both step-level and job-level)
_USES_RE = re.compile(
    r"""(?x)
    (?:^\s*uses\s*:\s*|uses:\s*)  # 'uses:' key
    (?P<quote>['\"]?)              # optional surrounding quote
    (?P<action>[^\s'\"@#]+)       # action path (owner/repo or ./local)
    @(?P<version>[^\s'\"#]+)      # @version
    (?P=quote)                     # closing quote (may be empty)
    """,
    re.MULTILINE,
)

WORKFLOW_DIRS = [
    Path(".github/workflows"),
    Path(".github/misc"),
]


def _is_exempt(action: str, version: str) -> bool:
    for pat in _EXEMPT_PATTERNS:
        if re.match(pat, action) or re.match(pat, version):
            return True
    return False


def scan_file(path: Path) -> list[dict]:
    """Return list of violation dicts found in *path*."""
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"::warning::Could not read {path}: {exc}", file=sys.stderr)
        return []

    violations: list[dict] = []
    for match in _USES_RE.finditer(text):
        action = match.group("action").strip()
        version = match.group("version").strip()

        if _is_exempt(action, version):
            continue

        expected = EXPECTED_VERSIONS.get(action)
        if expected is None:
            continue  # Not in policy — skip unknown actions

        # Accept any version >= minimum (forward-compat: v5 passes when min is v4)
        min_ver = MINIMUM_VERSIONS.get(action, 0)
        try:
            found_ver = int(version.lstrip("v").split(".")[0])
        except ValueError:
            found_ver = -1

        if found_ver < min_ver:
            line_no = text[: match.start()].count("\n") + 1
            violations.append(
                {
                    "file": str(path),
                    "line": line_no,
                    "action": action,
                    "found": version,
                    "expected": expected,
                    "match_start": match.start(),
                    "match_end": match.end(),
                    "full_match": match.group(0),
                }
            )
    return violations


def fix_file(path: Path, violations: list[dict]) -> bool:
    """Rewrite *path* replacing all violations.  Returns True if changed."""
    if not violations:
        return False

    text = path.read_text(encoding="utf-8")
    # Apply fixes in reverse order so offsets stay valid
    for v in sorted(violations, key=lambda x: x["match_start"], reverse=True):
        old = v["full_match"]
        new = old.replace(f"@{v['found']}", f"@{v['expected']}", 1)
        start, end = v["match_start"], v["match_end"]
        text = text[:start] + new + text[end:]

    path.write_text(text, encoding="utf-8")
    return True


def collect_workflows() -> list[Path]:
    paths: list[Path] = []
    for d in WORKFLOW_DIRS:
        if d.is_dir():
            paths.extend(sorted(d.glob("*.yml")))
            paths.extend(sorted(d.glob("*.yaml")))
    return paths


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Enforce expected GitHub Actions versions across all workflow files."
    )
    parser.add_argument(
        "--fix", action="store_true", help="Auto-fix violations in place."
    )
    parser.add_argument(
        "--json", dest="json_out", action="store_true",
        help="Output violations as JSON to stdout.",
    )
    parser.add_argument(
        "--warn-only", action="store_true",
        help="Report but never exit with code 1.",
    )
    parser.add_argument(
        "--summary", action="store_true",
        help="Write GitHub step summary (reads GITHUB_STEP_SUMMARY env var).",
    )
    args = parser.parse_args(argv)

    all_violations: list[dict] = []
    files_by_path: dict[str, list[dict]] = {}

    for wf_path in collect_workflows():
        violations = scan_file(wf_path)
        if violations:
            all_violations.extend(violations)
            files_by_path[str(wf_path)] = violations

    # ── Output ─────────────────────────────────────────────────────────────────
    if args.json_out:
        print(json.dumps({"violations": all_violations, "total": len(all_violations)}, indent=2))

    fixed_count = 0
    if args.fix and all_violations:
        for path_str, viols in files_by_path.items():
            if fix_file(Path(path_str), viols):
                fixed_count += 1
                print(f"✅ Fixed {len(viols)} violation(s) in {path_str}")

    # ── Annotations ────────────────────────────────────────────────────────────
    for v in all_violations:
        action_str = f"actions/{v['action'].split('/')[-1]}" if "/" in v["action"] else v["action"]
        if args.fix and fixed_count:
            print(
                f"::notice file={v['file']},line={v['line']}::"
                f"Fixed {action_str}: {v['found']} → {v['expected']}"
            )
        else:
            print(
                f"::error file={v['file']},line={v['line']}::"
                f"{action_str} uses @{v['found']} but expected @{v['expected']}"
            )

    # ── Summary ────────────────────────────────────────────────────────────────
    summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
    if (args.summary or summary_path) and summary_path:
        with open(summary_path, "a") as sf:
            sf.write("## 🔖 Required Actions Version Enforcer\n\n")
            if not all_violations:
                sf.write(
                    f"✅ All {len(collect_workflows())} workflow files use "
                    "approved action versions.\n"
                )
            elif args.fix and fixed_count:
                sf.write(
                    f"🔧 Auto-fixed {len(all_violations)} violation(s) "
                    f"across {fixed_count} file(s).\n\n"
                    "| File | Line | Action | Was | Now |\n"
                    "|------|------|--------|-----|-----|\n"
                )
                for v in all_violations:
                    sf.write(
                        f"| `{v['file']}` | {v['line']} | "
                        f"`{v['action']}` | `@{v['found']}` | `@{v['expected']}` |\n"
                    )
            else:
                sf.write(
                    f"❌ {len(all_violations)} violation(s) found across "
                    f"{len(files_by_path)} file(s).\n\n"
                    "| File | Line | Action | Found | Expected |\n"
                    "|------|------|--------|-------|----------|\n"
                )
                for v in all_violations:
                    sf.write(
                        f"| `{v['file']}` | {v['line']} | "
                        f"`{v['action']}` | `@{v['found']}` | `@{v['expected']}` |\n"
                    )
            sf.write("\n")

    # ── Exit code ───────────────────────────────────────────────────────────────
    if args.fix:
        # Re-scan after fixing to see if any violations remain
        remaining = []
        for wf_path in collect_workflows():
            remaining.extend(scan_file(wf_path))
    elif all_violations and not args.warn_only:
        remaining = list(all_violations)
    else:
        remaining = []

    if remaining and not args.warn_only:
        print(
            f"\n❌ {len(remaining)} action version violation(s) — "
            "run with --fix to auto-correct.",
            file=sys.stderr,
        )
        return 1

    if not all_violations:
        total = len(collect_workflows())
        print(f"✅ {total} workflow file(s) checked — all action versions approved.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
