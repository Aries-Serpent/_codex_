#!/usr/bin/env python3
"""
scan_all.py — Unified codebase-wide error discovery tool.

Runs EVERY static analysis check used in CI (ruff, mypy, isort, pre-commit
dry-run, duplicate-def scanner, SHA-drift check) in a single pass and
produces a ranked, colour-coded report so a Copilot coding agent (or
developer) can find ALL errors at once rather than one tool at a time.

Exit codes
----------
  0 — no errors discovered
  1 — one or more fixable errors discovered
  2 — tool execution error

Usage
-----
  python scripts/ci/scan_all.py              # full scan, coloured output
  python scripts/ci/scan_all.py --json       # machine-readable JSON
  python scripts/ci/scan_all.py --fix        # auto-fix everything possible
  python scripts/ci/scan_all.py --category ruff   # single category
  python scripts/ci/scan_all.py --summary    # one-line-per-check summary only
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import subprocess
import sys
import textwrap
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parents[2]

# ── ANSI colours (disabled when not a TTY) ────────────────────────────────
_COLOUR = sys.stdout.isatty()
RED    = "\033[31m" if _COLOUR else ""
YELLOW = "\033[33m" if _COLOUR else ""
GREEN  = "\033[32m" if _COLOUR else ""
CYAN   = "\033[36m" if _COLOUR else ""
BOLD   = "\033[1m"  if _COLOUR else ""
RESET  = "\033[0m"  if _COLOUR else ""

# ── Result dataclass ──────────────────────────────────────────────────────
@dataclass
class CheckResult:
    name: str
    category: str
    passed: bool
    fixable: bool          # True = can be auto-fixed
    error_count: int
    lines: list[str] = field(default_factory=list)
    fix_cmd: str = ""


# ── Individual check functions ─────────────────────────────────────────────

def _run(cmd: list[str], **kw) -> subprocess.CompletedProcess:
    return subprocess.run(
        cmd, capture_output=True, text=True, cwd=REPO_ROOT, **kw
    )


def check_ruff_all() -> CheckResult:
    """ruff — all selected rules (E, F, I) across the whole repo."""
    r = _run(["python", "-m", "ruff", "check", ".", "--output-format=json"])
    lines: list[str] = []
    try:
        items = json.loads(r.stdout) if r.stdout.strip() else []
        for it in items:
            fname = it["filename"].replace(str(REPO_ROOT) + "/", "")
            row   = it["location"]["row"]
            code  = it["code"]
            msg   = it["message"]
            lines.append(f"  {fname}:{row}  [{code}] {msg}")
    except (json.JSONDecodeError, KeyError):
        lines = [r.stdout.strip()] if r.stdout.strip() else []
    return CheckResult(
        name="ruff (E/F/I)",
        category="ruff",
        passed=len(lines) == 0,
        fixable=True,
        error_count=len(lines),
        lines=lines,
        fix_cmd="python -m ruff check . --fix",
    )


def check_ruff_stubs() -> CheckResult:
    """ruff F811 — duplicate definitions inside stub packages."""
    stub_dirs = [
        d for d in [
            REPO_ROOT / "torch",
            REPO_ROOT / "transformers",
            REPO_ROOT / "sentencepiece",
            REPO_ROOT / "omegaconf",
            REPO_ROOT / "numpy",
            REPO_ROOT / "tests" / "stub_packages",
        ] if d.exists()
    ]
    if not stub_dirs:
        return CheckResult("ruff F811 (stubs)", "ruff", True, True, 0)

    r = _run(
        ["python", "-m", "ruff", "check", "--select", "F811",
         "--output-format=json"] + [str(d) for d in stub_dirs]
    )
    lines: list[str] = []
    try:
        items = json.loads(r.stdout) if r.stdout.strip() else []
        for it in items:
            fname = it["filename"].replace(str(REPO_ROOT) + "/", "")
            row   = it["location"]["row"]
            msg   = it["message"]
            lines.append(f"  {fname}:{row}  [F811] {msg}")
    except (json.JSONDecodeError, KeyError):
        logger.debug("Suppressed exception in handler", exc_info=True)
    return CheckResult(
        name="ruff F811 (stub duplicates)",
        category="ruff",
        passed=len(lines) == 0,
        fixable=True,
        error_count=len(lines),
        lines=lines,
        fix_cmd="python -m ruff check --select F811 --fix torch/ transformers/ sentencepiece/ omegaconf/ numpy/",
    )


def check_mypy() -> CheckResult:
    """mypy — run against src/ in isolated minimal environment."""
    baseline_path = REPO_ROOT / ".mypy_baseline"
    baseline = int(baseline_path.read_text().strip()) if baseline_path.exists() else 0

    r = _run([
        sys.executable, "-m", "mypy", "src/",
        "--ignore-missing-imports",
        "--no-error-summary",
        "--no-pretty",
    ])
    error_lines = [ln for ln in r.stdout.splitlines() if ": error:" in ln]
    count = len(error_lines)
    exceeded = count > baseline
    lines = error_lines[:40]  # cap display to 40
    if count > 40:
        lines.append(f"  … {count - 40} more errors (run mypy src/ directly for full list)")
    return CheckResult(
        name=f"mypy (src/) [{count} errors vs baseline {baseline}]",
        category="mypy",
        passed=not exceeded,
        fixable=False,  # mypy errors require manual type annotation work
        error_count=count if exceeded else 0,
        lines=lines if exceeded else [],
        fix_cmd="python scripts/ci/mypy_baseline.py --update  # after fixing type errors",
    )


def check_isort() -> CheckResult:
    """isort — import sorting across entire repo."""
    r = _run([
        "python", "-m", "isort", ".", "--check-only", "--diff", "--quiet"
    ])
    lines = [ln for ln in r.stdout.splitlines() if ln.strip()][:30]
    return CheckResult(
        name="isort (import order)",
        category="isort",
        passed=r.returncode == 0,
        fixable=True,
        error_count=len(lines),
        lines=lines,
        fix_cmd="python -m isort .",
    )


def check_ruff_e402_tests() -> CheckResult:
    """ruff E402 — module-level imports not at top (test files, informational)."""
    r = _run([
        "python", "-m", "ruff", "check", "--select", "E402",
        "tests/", "--output-format=json",
    ])
    lines: list[str] = []
    try:
        items = json.loads(r.stdout) if r.stdout.strip() else []
        for it in items:
            fname = it["filename"].replace(str(REPO_ROOT) + "/", "")
            row   = it["location"]["row"]
            msg   = it["message"]
            lines.append(f"  {fname}:{row}  [E402] {msg}")
    except (json.JSONDecodeError, KeyError):
        logger.debug("Suppressed exception in handler", exc_info=True)
    # E402 in tests/ is suppressed by per-file-ignores — report is informational only
    return CheckResult(
        name="ruff E402 (tests/importorskip — informational)",
        category="ruff",
        passed=True,  # per-file-ignores suppresses these; this is FYI only
        fixable=False,
        error_count=len(lines),
        lines=lines,
        fix_cmd="# Suppressed via [tool.ruff.per-file-ignores] — no action needed",
    )


def check_pre_commit_fast() -> CheckResult:
    """pre-commit — run trailing-whitespace + end-of-file-fixer only (fast)."""
    r = _run([
        "pre-commit", "run", "trailing-whitespace", "end-of-file-fixer",
        "--all-files", "--show-diff-on-failure",
    ])
    passed = r.returncode == 0
    lines  = [ln for ln in (r.stdout + r.stderr).splitlines() if ln.strip()][:20]
    return CheckResult(
        name="pre-commit (whitespace/EOF)",
        category="pre-commit",
        passed=passed,
        fixable=True,
        error_count=0 if passed else len(lines),
        lines=[] if passed else lines,
        fix_cmd="pre-commit run trailing-whitespace end-of-file-fixer --all-files",
    )


def check_sha_drift() -> CheckResult:
    """CI SHA drift — warn when GITHUB_SHA != local git HEAD."""
    github_sha = os.environ.get("GITHUB_SHA", "")
    if not github_sha:
        # Not in CI — nothing to report
        return CheckResult("CI SHA drift (n/a outside CI)", "ci", True, False, 0)

    r = _run(["git", "log", "-1", "--format=%H"])
    local_sha = r.stdout.strip()
    if local_sha == github_sha:
        return CheckResult("CI SHA drift", "ci", True, False, 0)

    msg = (
        f"GITHUB_SHA={github_sha[:12]} ≠ git HEAD={local_sha[:12]}. "
        "CI is running on a GitHub merge-preview commit, not the PR branch HEAD. "
        "mypy/ruff counts may differ from local runs. "
        "Check .github/workflows/mypy-baseline.yml SHA-drift diagnostic step."
    )
    return CheckResult(
        name="CI SHA drift",
        category="ci",
        passed=False,
        fixable=False,
        error_count=1,
        lines=[f"  ⚠ {msg}"],
        fix_cmd=(
            "# SHA drift is informational — re-run CI after latest push resolves "
            "the merge-preview commit."
        ),
    )


def check_duplicate_baseline() -> CheckResult:
    """mypy baseline file — confirm .mypy_baseline is an integer ≥ 0."""
    path = REPO_ROOT / ".mypy_baseline"
    if not path.exists():
        return CheckResult(
            ".mypy_baseline file",
            "mypy",
            False, True, 1,
            ["  .mypy_baseline missing — create with: echo 0 > .mypy_baseline"],
            "echo 0 > .mypy_baseline",
        )
    try:
        val = int(path.read_text().strip())
        if val < 0:
            raise ValueError
    except ValueError:
        return CheckResult(
            ".mypy_baseline value",
            "mypy",
            False, True, 1,
            [f"  .mypy_baseline contains invalid value: {path.read_text().strip()!r}"],
            "echo 0 > .mypy_baseline",
        )
    return CheckResult(".mypy_baseline file", "mypy", True, False, 0)


# ── Registry ───────────────────────────────────────────────────────────────

ALL_CHECKS: list[tuple[str, Callable[[], CheckResult]]] = [
    ("ruff",        check_ruff_all),
    ("ruff",        check_ruff_stubs),
    ("mypy",        check_mypy),
    ("isort",       check_isort),
    ("ruff",        check_ruff_e402_tests),
    ("pre-commit",  check_pre_commit_fast),
    ("ci",          check_sha_drift),
    ("mypy",        check_duplicate_baseline),
]


# ── Reporting ──────────────────────────────────────────────────────────────

def _icon(r: CheckResult) -> str:
    if r.passed and r.error_count == 0:
        return f"{GREEN}✅{RESET}"
    if not r.passed:
        return f"{RED}❌{RESET}"
    return f"{YELLOW}⚠️{RESET}"   # informational


def print_summary(results: list[CheckResult]) -> None:
    print(f"\n{BOLD}{'=' * 60}{RESET}")
    print(f"{BOLD}  CODEBASE-WIDE SCAN SUMMARY{RESET}")
    print(f"{BOLD}{'=' * 60}{RESET}")
    for r in results:
        icon = _icon(r)
        count_str = f"({r.error_count} issues)" if r.error_count else ""
        fix_tag = f" {CYAN}[auto-fixable]{RESET}" if (not r.passed and r.fixable) else ""
        print(f"  {icon}  {r.name}  {YELLOW}{count_str}{RESET}{fix_tag}")
    print()


def print_details(results: list[CheckResult]) -> None:
    for r in results:
        if r.passed and r.error_count == 0:
            continue
        print(f"\n{BOLD}{_icon(r)}  {r.name}{RESET}")
        for ln in r.lines[:25]:
            print(f"  {YELLOW}{ln}{RESET}" if not r.passed else f"  {ln}")
        if len(r.lines) > 25:
            print(f"  … {len(r.lines) - 25} more lines")
        if r.fix_cmd:
            print(f"  {CYAN}Fix: {r.fix_cmd}{RESET}")


def to_json(results: list[CheckResult]) -> str:
    return json.dumps(
        [
            {
                "name": r.name,
                "category": r.category,
                "passed": r.passed,
                "fixable": r.fixable,
                "error_count": r.error_count,
                "lines": r.lines,
                "fix_cmd": r.fix_cmd,
            }
            for r in results
        ],
        indent=2,
    )


# ── Main ───────────────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(
        description=textwrap.dedent(__doc__),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--json",     action="store_true", help="Output JSON")
    parser.add_argument("--summary",  action="store_true", help="Summary table only")
    parser.add_argument("--fix",      action="store_true", help="Auto-fix where possible")
    parser.add_argument(
        "--category",
        choices=["ruff", "mypy", "isort", "pre-commit", "ci"],
        help="Run only checks in this category",
    )
    args = parser.parse_args()

    checks = (
        [(cat, fn) for cat, fn in ALL_CHECKS if cat == args.category]
        if args.category
        else ALL_CHECKS
    )

    results: list[CheckResult] = []
    for _cat, fn in checks:
        print(f"{CYAN}▶ {fn.__doc__ or fn.__name__}{RESET}", end="  ", flush=True)
        try:
            result = fn()
        except Exception as exc:  # pragma: no cover
            result = CheckResult(fn.__name__, _cat, False, False, 1,
                                 [f"  Tool error: {exc}"])
        icon = _icon(result)
        count = f"({result.error_count})" if result.error_count else ""
        print(f"{icon} {count}")
        results.append(result)

    if args.json:
        print(to_json(results))
        return 0

    print_summary(results)
    if not args.summary:
        print_details(results)

    # Auto-fix pass
    if args.fix:
        fixable = [r for r in results if not r.passed and r.fixable and r.fix_cmd]
        if fixable:
            print(f"\n{BOLD}🔧 Auto-fixing {len(fixable)} check(s)…{RESET}")
            for r in fixable:
                print(f"  Running: {r.fix_cmd}")
                subprocess.run(  # nosec B603 — fix_cmd is a hardcoded literal from CheckResult
                    r.fix_cmd.split(), cwd=REPO_ROOT, check=False,  # noqa: S603
                )
        else:
            print(f"{GREEN}Nothing to auto-fix.{RESET}")

    # Print Copilot-ready summary for issue reporting
    failing = [r for r in results if not r.passed]
    if failing:
        print(f"\n{BOLD}{RED}── COPILOT ACTION NEEDED ──────────────────────{RESET}")
        print("The following checks failed.  Fix in this order:\n")
        for i, r in enumerate(failing, 1):
            fix = f" → `{r.fix_cmd}`" if r.fixable and r.fix_cmd else " (manual fix required)"
            print(f"  {i}. {r.name} [{r.error_count} issues]{fix}")
        print()
        return 1

    print(f"{BOLD}{GREEN}✅ All checks passed!{RESET}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
