#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
codex_workflow.py — Best-effort constructor + controlled pruning for `_codex_` (branch 0B_base_)

- Builds inventory
- Applies targeted edits for supplied tasks
- Logs changes and errors
- Runs pre-commit on touched files (if configured)
- Writes results and pruning index
- Never activates GitHub Actions

Exit code:
  0 = success with no unresolved errors
  1 = unresolved errors captured in .codex/errors.ndjson
"""
from __future__ import annotations

import os
import re
import sys
import json
import shutil
import subprocess
from pathlib import Path
from datetime import datetime
from typing import List, Tuple, Dict, Optional

ROOT = Path(__file__).resolve().parents[1] if (Path(__file__).name == "codex_workflow.py") else Path.cwd()
CODEX_DIR = ROOT / ".codex"
CHANGE_LOG = CODEX_DIR / "change_log.md"
ERROR_LOG = CODEX_DIR / "errors.ndjson"
RESULTS = CODEX_DIR / "results.md"

# Safety: never enable GH Actions
GH_ACTIONS_DIR = ROOT / ".github" / "workflows"

TOUCH_TARGETS = [
    "src/codex/logging/query_logs.py",
    "src/codex/logging/session_hooks.py",
    "src/codex/db/sqlite_patch.py",
    "src/codex/logging/db_utils.py",  # may be created
    "src/codex/logging/export.py",
    "src/codex/logging/viewer.py",
    "src/codex/chat.py",
]

def ensure_dirs() -> None:
    CODEX_DIR.mkdir(parents=True, exist_ok=True)
    if not CHANGE_LOG.exists():
        CHANGE_LOG.write_text("# Codex Change Log\n\n", encoding="utf-8")
    if not ERROR_LOG.exists():
        ERROR_LOG.write_text("", encoding="utf-8")
    if not RESULTS.exists():
        RESULTS.write_text("# Codex Results\n\n", encoding="utf-8")

def clean_working_state_check() -> None:
    try:
        out = subprocess.run(["git", "status", "--porcelain"], cwd=ROOT, capture_output=True, text=True)
        if out.returncode != 0:
            raise RuntimeError(out.stderr.strip() or "git status failed")
        if out.stdout.strip():
            raise RuntimeError("Working tree not clean. Commit or stash changes before running.")
    except Exception as e:
        append_error("1.1", "Verify clean working state", str(e), "git status --porcelain")
        exit_with_errors()

def append_change(file: Path, action: str, rationale: str, before: str, after: str) -> None:
    ts = datetime.now().isoformat(timespec="seconds")
    snippet_before = "\n".join(before.splitlines()[:60])
    snippet_after = "\n".join(after.splitlines()[:60])
    entry = f"""## {ts} — {file.as_posix()}
**Action:** {action}
**Rationale:** {rationale}

<details><summary>Before (truncated)</summary>

```diff
{_diff_like(snippet_before)}
````

</details>

<details><summary>After (truncated)</summary>

```diff
{_diff_like(snippet_after)}
```

</details>

---

"""
    with CHANGE_LOG.open("a", encoding="utf-8") as fh:
        fh.write(entry)

def append_error(step: str, description: str, error: str, context: str) -> None:
    # Echo research-question format to console
    block = (
        "Question for ChatGPT-5:\n"
        f"While performing [{step}: {description}], encountered the following error:\n"
        f"{error}\n"
        f"Context: {context}\n"
        "What are the possible causes, and how can this be resolved while preserving intended functionality?\n"
    )
    sys.stderr.write(block + "\n")
    # Structured NDJSON
    rec = {
        "step": step,
        "description": description,
        "error": error,
        "context": context,
        "timestamp": datetime.now().isoformat(timespec="seconds"),
    }
    with ERROR_LOG.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec) + "\n")

def note_results(section: str, body: str) -> None:
    with RESULTS.open("a", encoding="utf-8") as fh:
        fh.write(f"## {section}\n\n{body.strip()}\n\n")

def _diff_like(text: str) -> str:
    return "\n".join(f" {line}" for line in text.splitlines())

def read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""
    except Exception as e:
        append_error("R.read", f"Read {path}", str(e), "read_text")
        return ""

def write_if_changed(path: Path, new: str, rationale: str) -> bool:
    old = read(path)
    if old == new:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    backup = path.with_suffix(path.suffix + ".bak")
    try:
        if old:
            shutil.copy2(path, backup)
        path.write_text(new, encoding="utf-8")
        append_change(path, "edit" if old else "create", rationale, old, new)
        return True
    except Exception as e:
        append_error("W.write", f"Write {path}", str(e), rationale)
        return False

def inventory() -> None:
    paths = []
    for p in ROOT.rglob("src/codex/**/*.py"):
        rel = p.relative_to(ROOT).as_posix()
        if any(seg.startswith(".") for seg in p.parts):
            continue
        paths.append(rel)
    note_results("Inventory", "- " + "\n- ".join(sorted(paths)) if paths else "No Python assets found.")

def guard_disable_gh_actions() -> None:
    if GH_ACTIONS_DIR.exists():
        note_results("Safety", "GitHub Actions present; will not activate or modify them.")
    else:
        note_results("Safety", "No GitHub Actions directory found.")

# --- Targeted Edits ---------------------------------------------------------

def edit_query_logs_build_query() -> Optional[Path]:
    """
    Task A: In src/codex/logging/query_logs.py:
    - Replace mapcol["content"] -> mapcol["message"] within build_query()
    - Adjust subsequent references accordingly (conservative: replace within function block)
    """
    rel = Path("src/codex/logging/query_logs.py")
    path = ROOT / rel
    src = read(path)
    if not src:
        append_error("3.1", "Locate query_logs.py", "file not found", str(rel))
        return None

    # Find def build_query(...): block (naive but scoped)
    m = re.search(r"(?ms)^(def\s+build_query\s*\(.*?\):\s*)(?P<body>.*?)(?=^\S)", src + "\nX")  # sentinel
    if not m:
        append_error("3.1", "Find build_query()", "not found", str(rel))
        return None
    head, body = m.group(1), m.group("body")

    # Replace content->message only in this function body
    new_body = body.replace('mapcol["content"]', 'mapcol["message"]')

    # Heuristic: if code accesses variable named content specifically tied to mapcol, adjust simple follow-ups:
    new_body = re.sub(r'mapcol\.get\("content"\)', 'mapcol.get("message")', new_body)

    if new_body == body:
        # No change needed; perhaps already updated—log and continue
        note_results("Task A", "No replacements performed; `build_query` likely already uses `message`.")
        return path

    new_src = src[:m.start("body")] + new_body + src[m.end("body") :]

    changed = write_if_changed(path, new_src, 'Switch build_query() to mapcol["message"] (scoped)')
    if changed:
        return path
    return None

def edit_logging_helpers() -> List[Path]:
    """
    Task B: Narrow exception handling
    - session_hooks._safe_write_text: (OSError, IOError)
    - session_hooks._safe_append_json_line: (OSError, IOError, json.JSONDecodeError)
    - sqlite_patch._apply_pragmas: sqlite3.Error
    """
    touched: List[Path] = []

    # session_hooks.py
    sh_rel = Path("src/codex/logging/session_hooks.py")
    sh_path = ROOT / sh_rel
    sh_src = read(sh_path)
    if sh_src:
        # Ensure json import if needed by append_json_line
        if "json.JSONDecodeError" in sh_src and "import json" not in sh_src:
            sh_src = "import json\n" + sh_src

        def narrow(func: str, exc_list: str) -> str:
            pattern = rf"(?ms)(def\s+{func}\s*\(.*?\):\s*)(?P<body>.*?)(?=^\S)"
            m = re.search(pattern, sh_src + "\nX")
            if not m:
                append_error("3.2", f"Find {func}", "not found", str(sh_rel))
                return sh_src
            body = m.group("body")
            # Replace broad excepts
            body2 = re.sub(r"\n\s*except\s*:\s*\n", f"\n    except {exc_list} as e:\n        import logging\n        logging.exception('Failure in {func}: %s', e)\n", body)
            body2 = re.sub(
                r"\n\s*except\s+Exception\s+as\s+(\w+)\s*:\s*\n",
                f"\n    except {exc_list} as e:\n        import logging\n        logging.exception('Failure in {func}: %s', e)\n",
                body2,
            )
            if body2 == body:
                # maybe already specific; add logging.exception if bare logging present
                if "logging.exception" not in body:
                    body2 = body.replace("logging.error(", "logging.exception(")
            return sh_src[: m.start("body")] + body2 + sh_src[m.end("body") :]

        sh_new = narrow("_safe_write_text", "(OSError, IOError)")
        sh_new = re.sub(r"(?s)^", "", sh_new)
        sh_new = sh_new if sh_new else sh_src
        sh_new = re.sub(
            r"(?s).*", lambda m: narrow("_safe_append_json_line", "(OSError, IOError, json.JSONDecodeError)"), sh_new, count=1
        ) if "_safe_append_json_line" in sh_new else sh_new

        if sh_new != sh_src:
            if write_if_changed(sh_path, sh_new, "Narrow exception handling; use logging.exception"):
                touched.append(sh_path)

    # sqlite_patch.py
    sp_rel = Path("src/codex/db/sqlite_patch.py")
    sp_path = ROOT / sp_rel
    sp_src = read(sp_path)
    if sp_src:
        if "sqlite3.Error" in sp_src and "import sqlite3" not in sp_src:
            sp_src = "import sqlite3\n" + sp_src

        m = re.search(r"(?ms)(def\s+_apply_pragmas\s*\(.*?\):\s*)(?P<body>.*?)(?=^\S)", sp_src + "\nX")
        if not m:
            append_error("3.2", "Find _apply_pragmas", "not found", str(sp_rel))
        else:
            body = m.group("body")
            body2 = re.sub(
                r"\n\s*except\s*:\s*\n",
                "\n    except sqlite3.Error as e:\n        import logging\n        logging.exception('sqlite PRAGMA failure: %s', e)\n",
                body,
            )
            body2 = re.sub(
                r"\n\s*except\s+Exception\s+as\s+(\w+)\s*:\s*\n",
                "\n    except sqlite3.Error as e:\n        import logging\n        logging.exception('sqlite PRAGMA failure: %s', e)\n",
                body2,
            )
            sp_new = sp_src[: m.start("body")] + body2 + sp_src[m.end("body") :]
            if sp_new != sp_src and write_if_changed(sp_path, sp_new, "Narrow _apply_pragmas exceptions; use logging.exception"):
                touched.append(sp_path)

    return touched

def remove_inner_imports_in_key() -> Optional[Path]:
    """
    Task C: Remove inner imports inside sqlite_patch._key; rely on module-level imports.
    """
    rel = Path("src/codex/db/sqlite_patch.py")
    path = ROOT / rel
    src = read(path)
    if not src:
        append_error("3.3", "Locate sqlite_patch.py", "file not found", str(rel))
        return None
    m = re.search(r"(?ms)(def\s+_key\s*\(.*?\):\s*)(?P<body>.*?)(?=^\S)", src + "\nX")
    if not m:
        append_error("3.3", "Find _key", "not found", str(rel))
        return None
    body = m.group("body")
    body2 = re.sub(r"^\s*import\s+os\s*$", "", body, flags=re.MULTILINE)
    body2 = re.sub(r"^\s*import\s+threading\s*$", "", body2, flags=re.MULTILINE)

    if body2 == body:
        note_results("Task C", "No inner imports found in _key; likely already clean.")
        return path

    new_src = src[: m.start("body")] + body2 + src[m.end("body") :]
    if write_if_changed(path, new_src, "Remove inner imports in _key (use module-level)"):
        return path
    return None

def add_db_utils_and_refactor() -> List[Path]:
    """
    Task D: Create resolve_db_path() and refactor callers when patterns are confidently detected.
    Conservative approach: add helper; attempt pattern replacements; else log research question.
    """
    touched: List[Path] = []
    du_rel = Path("src/codex/logging/db_utils.py")
    du_path = ROOT / du_rel
    helper = '''"""
Shared DB path utilities for codex logging.
"""
from __future__ import annotations
from pathlib import Path
from typing import Optional, Union

def resolve_db_path(base: Union[str, Path], name: Optional[str] = None) -> Path:
    """
    Resolve an absolute, normalized DB path under `base`.
    - Ensures parent directory exists (mkdir parents=True, exist_ok=True)
    - Does NOT create the DB file.
    """
    b = Path(base).expanduser().resolve()
    if name:
        p = b / name
    else:
        p = b
    p.parent.mkdir(parents=True, exist_ok=True)
    return p
'''
    if write_if_changed(du_path, helper, "Create shared DB helper resolve_db_path"):
        touched.append(du_path)

    candidates = [
        Path("src/codex/logging/export.py"),
        Path("src/codex/logging/viewer.py"),
        Path("src/codex/logging/query_logs.py"),
    ]
    import_line = "from .db_utils import resolve_db_path"
    for rel in candidates:
        path = ROOT / rel
        src = read(path)
        if not src:
            continue
        new_src = src
        if import_line not in new_src:
            # place after first import block
            m = re.search(r"(?m)^from\s+.*|^import\s+.*", new_src)
            if m:
                # insert import line after the last contiguous import group
                imports = list(
                    re.finditer(r"(?m)^(?:from\s+\S+\s+import\s+.*|import\s+.*)$", new_src)
                )
                if imports:
                    last = imports[-1]
                    new_src = new_src[: last.end()] + f"\n{import_line}\n" + new_src[last.end() :]
                else:
                    new_src = import_line + "\n" + new_src
            else:
                new_src = import_line + "\n" + new_src

        # Attempt a minimal, safe replacement of common patterns:
        # Pattern 1: Path(base) / name -> resolve_db_path(base, name)
        new_src2 = re.sub(
            r"Path\(\s*([^\)]+)\s*\)\s*/\s*([A-Za-z0-9_\'\"\.\-]+)",
            r"resolve_db_path(\1, \2)",
            new_src,
        )
        # Pattern 2: os.path.join(base, name) -> resolve_db_path(base, name)
        new_src2 = re.sub(
            r"os\.path\.join\(\s*([^,]+)\s*,\s*([^)]+)\)",
            r"resolve_db_path(\1, \2)",
            new_src2,
        )

        if new_src2 == src:
            append_error(
                "3.4",
                f"Refactor to resolve_db_path in {rel.as_posix()}",
                "No confident DB-path patterns found",
                "Left code unchanged; helper available for future refactor",
            )
        if new_src2 != src and write_if_changed(path, new_src2, "Refactor DB path to resolve_db_path (best-effort)"):
            touched.append(path)

    return touched

def document_chat_session_exit() -> Optional[Path]:
    rel = Path("src/codex/chat.py")
    path = ROOT / rel
    src = read(path)
    if not src:
        append_error("3.5", "Locate chat.py", "file not found", str(rel))
        return None
    m = re.search(r"(?ms)(def\s+__exit__\s*\(.*?\):\s*)(?P<body>.*?)(?=^\S)", src + "\nX")
    if not m:
        append_error("3.5", "Find ChatSession.__exit__", "not found", str(rel))
        return None
    head, body = m.group(1), m.group("body")
    if '"""' in body.splitlines()[0]:
        note_results("Task E", "`__exit__` already has a docstring.")
        return path
    doc = (
        '    """Context manager exit protocol.\n'
        "    Args:\n"
        "        exc_type: Exception type if an exception occurred, else None.\n"
        "        exc: Exception instance if an exception occurred, else None.\n"
        "        tb: Traceback object if an exception occurred, else None.\n\n"
        "    Returns:\n"
        "        None. (The method does not suppress exceptions.)\n"
        '    """\n'
    )
    # Insert docstring as the first statement in the function body
    body2 = doc + body
    new_src = src[: m.start("body")] + body2 + src[m.end("body") :]
    if write_if_changed(path, new_src, "Add __exit__ docstring (protocol & return type)"):
        return path
    return None

# --- pre-commit -------------------------------------------------------------

def run_pre_commit(files: List[Path]) -> None:
    if not files:
        return
    cfg = ROOT / ".pre-commit-config.yaml"
    if not cfg.exists():
        note_results("pre-commit", "No .pre-commit-config.yaml; skipping hooks.")
        return
    str_files = [str(f.relative_to(ROOT)) for f in files if f.exists()]
    if not str_files:
        return
    try:
        out = subprocess.run(["pre-commit", "run", "--files", *str_files], cwd=ROOT, capture_output=True, text=True)
        note_results("pre-commit output", f"`\n{out.stdout}\n{out.stderr}\n`")
        if out.returncode != 0:
            append_error("3.6", "pre-commit run failed", f"rc={out.returncode}", "\n".join(str_files))
    except FileNotFoundError:
        note_results("pre-commit", "pre-commit not installed; skipping.")
    except Exception as e:
        append_error("3.6", "pre-commit execution error", str(e), "subprocess")

# --- Finalization -----------------------------------------------------------

def finalize() -> None:
    # Results summary header
    addendum = (
        "**Important:** DO NOT ACTIVATE ANY GitHub Actions files.\n\n"
        "If unresolved errors are present in `.codex/errors.ndjson`, exit code is 1."
    )
    note_results("Finalization", addendum)

def exit_with_errors() -> None:
    sys.exit(1)

def has_unresolved_errors() -> bool:
    try:
        return ERROR_LOG.exists() and ERROR_LOG.read_text(encoding="utf-8").strip() != ""
    except Exception:
        return True

# --- Main ------------------------------------------------------------------

def main() -> int:
    clean_working_state_check()
    ensure_dirs()
    guard_disable_gh_actions()
    inventory()

    touched: List[Path] = []

    # Task A
    p = edit_query_logs_build_query()
    if p:
        touched.append(p)

    # Task B
    touched += edit_logging_helpers()

    # Task C
    p = remove_inner_imports_in_key()
    if p and p not in touched:
        touched.append(p)

    # Task D
    touched += add_db_utils_and_refactor()

    # Task E
    p = document_chat_session_exit()
    if p and p not in touched:
        touched.append(p)

    # Run pre-commit on touched files
    run_pre_commit(touched)

    finalize()
    return 1 if has_unresolved_errors() else 0

if __name__ == "__main__":
    rc = main()
    sys.exit(rc)
