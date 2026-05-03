#!/usr/bin/env python3
"""
Pre-Commit Pattern Recurrence Check — Phase 6 / S187

Warns the Copilot agent before a commit if the staged diff re-introduces Python
code patterns that have historically caused CI failures, based on the accumulated
knowledge graph in the cognitive brain SQLite database.

The hook is advisory by default (exit 0 even when warnings are found).  Set
``CODEX_PATTERN_HOOK_STRICT=1`` to make it blocking (exit 1).

How it works
------------
1. Run ``git diff --cached`` to get the staged diff.
2. For each modified/added ``.py`` file in the diff, call
   ``scripts/ci/auto_fix_common_issues.py --check-only`` on the *staged* blob
   (via ``git show :file``) to detect pattern violations.
3. Cross-reference detected patterns against the ``high_recurrence`` query from
   ``pattern_recorder.py`` (patterns seen >= ``MIN_OCCURRENCES`` times in history
   with a fix-rate >= ``MIN_FIX_RATE``).
4. If any overlap, print a warning listing the high-recurrence patterns and the
   files affected.

Usage
-----
    # As a git pre-commit hook — copy or symlink to .git/hooks/pre-commit:
    ln -sf ../../scripts/hooks/pre_commit_pattern_check.py .git/hooks/pre-commit

    # Or run manually before committing:
    python scripts/hooks/pre_commit_pattern_check.py

    # Strict mode (blocks the commit):
    CODEX_PATTERN_HOOK_STRICT=1 python scripts/hooks/pre_commit_pattern_check.py

Environment
-----------
    CODEX_DB_PATH               Cognitive brain DB path (default: ~/.codex/cli_history.db)
    CODEX_PATTERN_HOOK_STRICT   Set to '1' to block commits when warnings exist
    CODEX_PATTERN_MIN_OCC       Minimum historical occurrences threshold (default: 3)
    CODEX_PATTERN_MIN_RATE      Minimum fix-rate threshold 0–1 (default: 0.5)
    CODEX_SKIP_PATTERN_WARN     Set to '1' to skip this hook entirely
"""

from __future__ import annotations

import importlib.util
import json
import logging
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
_RECORDER_PATH = _REPO_ROOT / "scripts" / "ci" / "pattern_recorder.py"

_DB_PATH = os.environ.get(
    "CODEX_DB_PATH",
    os.path.join(os.path.expanduser("~"), ".codex", "cli_history.db"),
)
_STRICT = os.environ.get("CODEX_PATTERN_HOOK_STRICT", "0") == "1"
_SKIP = os.environ.get("CODEX_SKIP_PATTERN_WARN", "0") == "1"
_MIN_OCC = int(os.environ.get("CODEX_PATTERN_MIN_OCC", "3"))
_MIN_RATE = float(os.environ.get("CODEX_PATTERN_MIN_RATE", "0.5"))


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _load_recorder():
    """Dynamically import pattern_recorder to avoid circular imports."""
    if not _RECORDER_PATH.exists():
        return None
    spec = importlib.util.spec_from_file_location("pattern_recorder", _RECORDER_PATH)
    mod = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod


def _get_staged_py_files() -> list[str]:
    """Return list of staged (added/modified) Python file paths."""
    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
            capture_output=True,
            text=True,
            cwd=_REPO_ROOT,
        )
        return [f for f in result.stdout.splitlines() if f.endswith(".py")]
    except OSError:
        return []


def _get_staged_blob(path: str) -> Optional[str]:
    """Return the staged (index) content of a file, or None on error."""
    try:
        result = subprocess.run(
            ["git", "show", f":{path}"],
            capture_output=True,
            text=True,
            cwd=_REPO_ROOT,
        )
        if result.returncode == 0:
            return result.stdout
    except OSError as exc:
        # Best-effort: if git or the index is unavailable, skip this file.
        print(f"[pattern-hook] warning: could not read staged blob for {path!r}: {exc}", file=sys.stderr)
    return None


def _detect_patterns_in_source(source: str, filename: str) -> set[str]:
    """Run pattern detection on *source* text and return pattern names found.

    Uses a lightweight subset of the checks from ``auto_fix_common_issues.py``
    that can operate on a string buffer without file I/O — specifically the
    patterns that are both auto-fixable and historically high-recurrence.
    """
    detected: set[str] = set()

    # Pattern 18: Duplicate Kwargs — use AST directly
    try:
        import ast as _ast
        tree = _ast.parse(source, filename=filename)
        for node in _ast.walk(tree):
            if isinstance(node, _ast.Call):
                seen: dict[str, int] = {}
                for kw in node.keywords:
                    if kw.arg is None:
                        continue
                    if kw.arg in seen:
                        detected.add("Duplicate Kwargs")
                        break
                    seen[kw.arg] = 1
    except SyntaxError:
        # Ignore files that are not syntactically valid Python — they cannot
        # be parsed for duplicate-kwargs detection and are likely intentional
        # test fixtures or work-in-progress code.
        logger.debug("Suppressed exception in handler", exc_info=True)
    # Pattern 1: Unused imports — lightweight heuristic via ruff if available
    tmp_path: Optional[str] = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False
        ) as tmp:
            tmp.write(source)
            tmp_path = tmp.name
        result = subprocess.run(
            ["ruff", "check", "--select=F401", "--output-format=json", tmp_path],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode != 0 and result.stdout.strip():
            items = json.loads(result.stdout)
            if items:
                detected.add("Unused Imports")
    except (OSError, subprocess.TimeoutExpired, json.JSONDecodeError, FileNotFoundError):
        # The ruff F401 check is optional; if ruff is unavailable or times out,
        # skip this detection step rather than failing the whole hook.
        logger.debug("Suppressed exception in handler", exc_info=True)
    finally:
        if tmp_path is not None:
            try:
                os.unlink(tmp_path)
            except OSError:
                logger.debug("Suppressed exception in handler", exc_info=True)
    return detected


# ---------------------------------------------------------------------------
# Main logic
# ---------------------------------------------------------------------------

def run_check() -> int:
    """Run the pre-commit pattern check.  Returns exit code (0 or 1)."""
    if _SKIP:
        return 0

    # Load recorder to query high-recurrence patterns
    recorder = _load_recorder()
    if recorder is None or not Path(_DB_PATH).exists():
        # No DB yet — nothing to warn about; silently pass
        return 0

    conn = recorder._open_db(_DB_PATH)
    high_rec: list[dict[str, Any]] = recorder.high_recurrence(
        conn,
        min_occurrences=_MIN_OCC,
        min_fix_rate=_MIN_RATE,
    )
    conn.close()

    if not high_rec:
        return 0  # no high-recurrence patterns in history — nothing to warn about

    high_rec_names: set[str] = {r["pattern_name"] for r in high_rec}
    staged_files = _get_staged_py_files()

    if not staged_files:
        return 0

    warnings: list[str] = []
    for fpath in staged_files:
        blob = _get_staged_blob(fpath)
        if blob is None:
            continue
        detected = _detect_patterns_in_source(blob, fpath)
        overlapping = detected & high_rec_names
        for pattern in sorted(overlapping):
            meta = next((r for r in high_rec if r["pattern_name"] == pattern), {})
            warnings.append(
                f"  ⚠  {fpath}: '{pattern}' "
                f"(seen {meta.get('total', '?')}× historically, "
                f"{meta.get('fix_rate', 0):.0%} fix-rate)"
            )

    if not warnings:
        return 0

    border = "─" * 70
    print(f"\n{border}", file=sys.stderr)
    print(
        "🧠 COGNITIVE PATTERN WARNING — high-recurrence CI patterns detected",
        file=sys.stderr,
    )
    print(border, file=sys.stderr)
    for w in warnings:
        print(w, file=sys.stderr)
    print(border, file=sys.stderr)

    if _STRICT:
        print(
            "\n❌ Commit blocked (CODEX_PATTERN_HOOK_STRICT=1).\n"
            "   Fix the patterns above or set CODEX_SKIP_PATTERN_WARN=1 to bypass.",
            file=sys.stderr,
        )
        return 1

    print(
        "\nℹ  These are warnings only (set CODEX_PATTERN_HOOK_STRICT=1 to block).\n"
        "   Run: python scripts/ci/auto_fix_common_issues.py --check-only\n"
        "   to see the full diagnostic report.",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    sys.exit(run_check())
