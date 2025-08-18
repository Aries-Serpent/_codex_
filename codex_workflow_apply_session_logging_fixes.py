#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Codex Workflow: Apply session logging robustness fixes with best-effort construction,
evidence-based pruning, error capture (ChatGPT-5 questions), and results summary.

Guardrail: DO NOT ACTIVATE ANY GitHub Actions files.
"""

from __future__ import annotations
import os, sys, json, shutil, subprocess, datetime, difflib, re
from pathlib import Path

# -------- Config / Flags --------
DO_NOT_ACTIVATE_GITHUB_ACTIONS = True
WRITE_CHANGES = True
SAFE_MODE = True
TARGET_FILES = [
    "scripts/apply_session_logging_workflow.py",
    "tests/test_session_logging.py",
    "tools/codex_session_logging_workflow.py",
]

# -------- Paths / Setup --------
REPO_ROOT = Path.cwd()
CODEX_DIR = REPO_ROOT / ".codex"
CHANGE_LOG = CODEX_DIR / "change_log.md"
ERRORS_LOG = CODEX_DIR / "errors.ndjson"
RESULTS_MD = CODEX_DIR / "results.md"
INVENTORY_MD = CODEX_DIR / "inventory.md"


def now_iso():
    return datetime.datetime.now().isoformat(timespec="seconds")


def ensure_dirs():
    CODEX_DIR.mkdir(exist_ok=True)


def write_change_log_header():
    if not CHANGE_LOG.exists():
        CHANGE_LOG.write_text(f"# Codex Change Log\n\nDate: {now_iso()}\n\n", encoding="utf-8")


def append_change(title: str, path: Path, before: str, after: str):
    diff = "\n".join(difflib.unified_diff(
        before.splitlines(), after.splitlines(),
        fromfile=f"a/{path}", tofile=f"b/{path}", lineterm=""
    ))
    with CHANGE_LOG.open("a", encoding="utf-8") as f:
        f.write(f"## {title}\n\n**File:** `{path.as_posix()}`\n\n```diff\n{diff}\n```\n\n")


def append_error(step: str, description: str, error: str, context: dict):
    rec = {
        "timestamp": now_iso(),
        "step": step,
        "description": description,
        "error": error,
        "context": context,
    }
    with ERRORS_LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(rec) + "\n")
    # Echo ChatGPT-5 research question
    msg = (
        "Question for ChatGPT-5:\n"
        f"While performing [{step}: {description}], encountered the following error:\n"
        f"{error}\n"
        f"Context: {json.dumps(context, ensure_ascii=False)}\n"
        "What are the possible causes, and how can this be resolved while preserving intended functionality?\n"
    )
    print(msg, file=sys.stderr)


def git_available() -> bool:
    return shutil.which("git") is not None


def in_git_repo() -> bool:
    try:
        subprocess.run(
            ["git", "rev-parse", "--is-inside-work-tree"],
            check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        return True
    except Exception:
        return False


def repo_root_from_git() -> Path | None:
    try:
        out = subprocess.check_output(["git", "rev-parse", "--show-toplevel"], text=True).strip()
        return Path(out)
    except Exception:
        return None


def verify_clean_state():
    try:
        res = subprocess.check_output(["git", "status", "--porcelain"], text=True)
        return res.strip() == ""
    except Exception:
        return None  # unknown


def write_inventory():
    rows = []
    for p in REPO_ROOT.rglob("*"):
        if p.is_file() and ".git" not in p.parts:
            kind = p.suffix or "(no-ext)"
            try:
                size = p.stat().st_size
            except Exception:
                size = -1
            rows.append((p.relative_to(REPO_ROOT).as_posix(), kind, size))
    rows.sort()
    with INVENTORY_MD.open("w", encoding="utf-8") as f:
        f.write("# Inventory\n\n| path | kind | size |\n|---|---|---:|\n")
        for path, kind, size in rows:
            f.write(f"| `{path}` | `{kind}` | {size} |\n")


def backup_file(p: Path):
    if SAFE_MODE and p.exists():
        bak = p.with_suffix(p.suffix + ".codex.bak")
        shutil.copy2(p, bak)


def read_text(p: Path) -> str:
    return p.read_text(encoding="utf-8")


def write_text(p: Path, content: str):
    if WRITE_CHANGES:
        p.write_text(content, encoding="utf-8")


def replace_exact_except_pass_in_apply_session_logging(src: str) -> str:
    """
    Replace 'except FileNotFoundError: pass' with logged graceful exit.
    Also optionally add git pre-check helpers if missing.
    """
    modified = src

    # Ensure imports/helpers exist (idempotent insertions)
    if "shutil" not in modified or "subprocess" not in modified or "logging" not in modified:
        if "import " in modified:
            modified = re.sub(r"^(import .*\n)", r"\1import shutil, subprocess, logging, sys\n", modified, count=1, flags=re.M)
        else:
            modified = "import shutil, subprocess, logging, sys\n" + modified

    if "_git_available" not in modified:
        helper = (
            "\n\ndef _git_available() -> bool:\n"
            "    return shutil.which('git') is not None\n"
        )
        modified += helper
    if "_in_git_repo" not in modified:
        helper = (
            "\n\ndef _in_git_repo() -> bool:\n"
            "    try:\n"
            "        subprocess.run(['git','rev-parse','--is-inside-work-tree'],\n"
            "                       check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)\n"
            "        return True\n"
            "    except Exception:\n"
            "        return False\n"
        )
        modified += helper

    # Pre-run guard (insert after imports/helpers): if not git or not repo → warn + exit(0)
    if "CODex_GIT_PRECHECK_MARK" not in modified:
        precheck = (
            "\n# CODex_GIT_PRECHECK_MARK\n"
            "if not _git_available() or not _in_git_repo():\n"
            "    logging.warning('Git not found or not a Git repository. The workflow requires Git.')\n"
            "    logging.warning('Suggestion: install Git or run inside a Git repo.')\n"
            "    sys.exit(0)\n"
        )
        # place after first line
        modified = re.sub(r"(\A[^\n]*\n)", r"\1" + precheck, modified, count=1, flags=re.M)

    # Replace the bare except
    pattern = r"except\s+FileNotFoundError\s*:\s*pass"
    replacement = (
        "except FileNotFoundError as e:\n"
        "    logging.warning('Git is required for the session logging workflow. %s', e)\n"
        "    logging.warning('Suggestion: install Git and/or run this script inside a Git repository.')\n"
        "    sys.exit(0)  # graceful, non-error termination when Git is absent\n"
    )
    modified = re.sub(pattern, replacement, modified)

    return modified


def harden_tests_test_session_logging(src: str) -> str:
    modified = src
    # Ensure imports
    if "import pytest" not in modified:
        modified = "import pytest\n" + modified
    if "import logging" not in modified:
        modified = "import logging\n" + modified
    if "import subprocess" not in modified:
        modified = "import subprocess\n" + modified

    # Add module-level skip if not in git repo
    if "def _in_git_repo()" not in modified:
        helper = (
            "\n\ndef _in_git_repo():\n"
            "    try:\n"
            "        subprocess.run(['git','rev-parse','--is-inside-work-tree'],\n"
            "                       check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)\n"
            "        return True\n"
            "    except Exception:\n"
            "        return False\n"
        )
        modified += helper
    if "allow_module_level=True" not in modified:
        guard = (
            "\nif not _in_git_repo():\n"
            "    pytest.skip('Git repo not available; skipping session logging tests.', allow_module_level=True)\n"
        )
        # place near top (after imports)
        modified = re.sub(r"(\A(?:from .*\n|import .*\n)+)", r"\1" + guard, modified, count=1, flags=re.M)

    # Replace any `except Exception: pass` blocks
    modified = re.sub(
        r"except\s+Exception\s*:\s*pass",
        ("except Exception as exc:\n"
         "    logging.error('Unexpected exception during session logging test: %s', exc)\n"
         "    pytest.fail(f'Unexpected exception in session logging test: {exc}')"),
        modified
    )
    return modified


def harden_tools_codex_session_logging_workflow(src: str) -> str:
    modified = src
    if "import logging" not in modified:
        if "import " in modified:
            modified = re.sub(r"^(import .*\n)", r"\1import logging\n", modified, count=1, flags=re.M)
        else:
            modified = "import logging\n" + modified

    # Replace except Exception: pass → logged + raise with hook context if available
    def repl(m):
        return (
            "except Exception as exc:\n"
            "    _ctx_hook = locals().get('hook_name', '<unknown>')\n"
            "    logging.exception(\"Error while processing session-logging hook '%s': %s\", _ctx_hook, exc)\n"
            "    raise\n"
        )
    modified = re.sub(r"except\s+Exception\s*:\s*pass", repl, modified)
    return modified


def apply_file_edit(path_rel: str, transformer, title: str):
    p = REPO_ROOT / path_rel
    if not p.exists():
        append_error("Phase 3", f"{title}", "file not found", {"path": path_rel})
        return False
    try:
        before = read_text(p)
        after = transformer(before)
        if before != after:
            backup_file(p)
            write_text(p, after)
            append_change(title, p, before, after)
        else:
            # no-op: pattern not found
            append_error("Phase 3", f"{title}", "pattern not found or no change", {"path": path_rel})
        return True
    except Exception as e:
        append_error("Phase 3", f"{title}", str(e), {"path": path_rel})
        return False

def readme_touchup():
    # Best-effort wording update (non-fatal if missing)
    candidates = [REPO_ROOT / "README.md", REPO_ROOT / "README.rst", REPO_ROOT / "README.txt"]
    for p in candidates:
        if p.exists():
            try:
                before = read_text(p)
                after = before
                after = after.replace("silently ignore", "log a warning and exit gracefully when Git is unavailable")
                if before != after:
                    backup_file(p)
                    write_text(p, after)
                    append_change("README wording update", p, before, after)
                return
            except Exception as e:
                append_error("Phase 3", "README update", str(e), {"path": p.as_posix()})
                return

def finalize_results(unresolved_errors_exist: bool):
    DO_NOTS = "\n**DO NOT ACTIVATE ANY GitHub Actions files.**\n"
    content = [
        "# Results Summary",
        f"- Timestamp: {now_iso()}",
        "- Implemented: session logging robustness edits in `scripts/`, `tests/`, and `tools/` (best-effort).",
        "- Residual gaps: see `.codex/errors.ndjson` for any unmatched patterns or missing files.",
        "- Prune index: (none unless noted in change log).",
        "- Next steps: run tests locally; review diffs; iterate on context-specific logging text.",
        DO_NOTS
    ]
    RESULTS_MD.write_text("\n".join(content) + "\n", encoding="utf-8")
    return 1 if unresolved_errors_exist else 0


def main():
    ensure_dirs()
    write_change_log_header()

    # Phase 1: preparation
    root_from_git = repo_root_from_git() if git_available() else None
    clean = verify_clean_state() if root_from_git else None
    write_inventory()

    if DO_NOT_ACTIVATE_GITHUB_ACTIONS:
        # Soft assertion / log (no action)
        pass

    unresolved = False

    # Phase 3: best-effort construction
    # A) scripts/apply_session_logging_workflow.py
    ok1 = apply_file_edit(
        "scripts/apply_session_logging_workflow.py",
        replace_exact_except_pass_in_apply_session_logging,
        "Replace bare FileNotFoundError except with warning + graceful exit"
    )
    unresolved = unresolved or not ok1

    # B) tests/test_session_logging.py
    ok2 = apply_file_edit(
        "tests/test_session_logging.py",
        harden_tests_test_session_logging,
        "Make tests fail on unexpected exceptions and skip if repo/hooks unavailable"
    )
    unresolved = unresolved or not ok2

    # C) tools/codex_session_logging_workflow.py
    ok3 = apply_file_edit(
        "tools/codex_session_logging_workflow.py",
        harden_tools_codex_session_logging_workflow,
        "Replace bare except in tools workflow with contextual logging and re-raise"
    )
    unresolved = unresolved or not ok3

    # Phase 3.3: docs touch-up
    readme_touchup()

    # Phase 6: finalize
    exit_code = finalize_results(unresolved_errors_exist=unresolved)
    print("Guardrail: DO NOT ACTIVATE ANY GitHub Actions files.", file=sys.stderr)
    sys.exit(exit_code)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        append_error("Finalization", "Unhandled exception in workflow", str(e), {"cwd": str(REPO_ROOT)})
        print("Guardrail: DO NOT ACTIVATE ANY GitHub Actions files.", file=sys.stderr)
        sys.exit(1)
