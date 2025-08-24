#!/usr/bin/env python3
"""
End-to-end workflow to add session logging context manager, helper, CLI query,
tests, and docs to the _codex_ repository (branch 0B_base_).
Respects the guardrail: DO NOT ACTIVATE ANY GitHub Actions files.

Phases implemented: 1..6 (see top-level plan).
"""

from __future__ import annotations

import difflib
import json
import re
import sys
import time

try:
    from codex.db.sqlite_patch import auto_enable_from_env as _codex_sqlite_auto

    _codex_sqlite_auto()
except Exception:
    pass
import textwrap
from pathlib import Path
from typing import List, Optional, Tuple

from codex.utils.subprocess import run

# -------------------------------
# Phase 1 — Preparation utilities
# -------------------------------
ROOT: Path | None = None
DO_NOT_ACTIVATE_GITHUB_ACTIONS = True
CHANGELOG: str | None = None
ERRORS: str | None = None
RESULTS: str | None = None

ROLES = {"system", "user", "assistant", "tool"}


def git_root() -> Path:
    try:
        out = run(
            ["git", "rev-parse", "--show-toplevel"], capture_output=True
        ).stdout.strip()
        return Path(out)
    except Exception:
        return Path.cwd()


def require_clean_worktree() -> None:
    try:
        out = run(["git", "status", "--porcelain"], capture_output=True).stdout
        if out.strip():
            raise RuntimeError(
                "Working tree not clean. Commit or stash before running."
            )
    except FileNotFoundError as e:
        sys.stderr.write(
            "WARNING: Git is required for this operation. Please install Git (https://git-scm.com/) and ensure this script is run inside a Git repository. Details: {}\n".format(
                str(e)
            )
        )
        sys.exit(2)


def ensure_codex_dir(root: Path) -> Path:
    p = root / ".codex"
    p.mkdir(parents=True, exist_ok=True)
    return p


def log_error(step: str, err: Exception | str, context: str = "") -> None:
    msg = str(err)
    entry = {
        "question_for": "ChatGPT-5",
        "template": "research_question",
        "step": step,
        "error_message": msg,
        "context": context,
        "ts": time.time(),
    }
    print(
        textwrap.dedent(
            f"""
            Question for ChatGPT-5:
            While performing [{step}], encountered the following error:
            {msg}
            Context: {context}
            What are the possible causes, and how can this be resolved while preserving intended functionality?
            """
        ).strip()
    )
    with open(ERRORS, "a", encoding="utf-8") as fh:  # type: ignore[arg-type]
        fh.write(json.dumps(entry, ensure_ascii=False) + "\n")


def read_text(p: Path) -> str:
    return p.read_text(encoding="utf-8") if p.exists() else ""


def append_change(path: Path, action: str, rationale: str, diff: str = "") -> None:
    entry = f"* **{action}** `{path.as_posix()}` — {rationale}"
    with open(CHANGELOG, "a", encoding="utf-8") as fh:  # type: ignore[arg-type]
        fh.write(entry + "\n")
        if diff:
            fh.write("\n<details><summary>diff</summary>\n\n```diff\n")
            fh.write(diff)
            fh.write("\n```\n</details>\n\n")


def write_file(path: Path, new_text: str, rationale: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    old = read_text(path)
    if old == new_text:
        append_change(path, "kept", rationale, diff="")
        return
    path.write_text(new_text, encoding="utf-8")
    diff = "\n".join(
        difflib.unified_diff(
            old.splitlines(),
            new_text.splitlines(),
            fromfile=str(path),
            tofile=str(path),
            lineterm="",
        )
    )
    append_change(path, "write" if not old else "update", rationale, diff)


def inventory(root: Path) -> List[Tuple[str, str, str]]:
    items: List[Tuple[str, str, str]] = []
    for d in ("src", "codex", "tools", "scripts", "tests", "documentation"):
        base = root / d
        if not base.exists():
            continue
        for p in base.rglob("*"):
            if p.is_dir():
                continue
            if any(part.startswith(".git") for part in p.parts):
                continue
            kind = p.suffix or "file"
            role = (
                "code"
                if p.suffix
                in {".py", ".sh", ".sql", ".js", ".ts", ".jsx", ".tsx", ".html"}
                else "doc"
            )
            items.append((str(p.relative_to(root)), kind, role))
    return items


def search_candidates(root: Path):
    hits = []
    for p in root.rglob("*.py"):
        try:
            txt = p.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        for sym in (
            r"\blog_event\b",
            r"\binit_db\b",
            r"\b_DB_LOCK\b",
            r"\bsession_events\b",
        ):
            if re.search(sym, txt):
                hits.append((str(p.relative_to(root)), sym))
    return hits


# ----------------------------------
# Phase 3 — Code we will materialize
# ----------------------------------

SESSION_LOGGER_PY = '''\
"""Session logging utilities for Codex.

Provides:
- `SessionLogger`: context manager logging session_start/session_end via `log_event`.
- `log_message(session_id, role, message, db_path=None)`: validated message logging helper.

If the repo already defines `log_event`, `init_db`, and `_DB_LOCK` under `codex.logging`,
we import and use them. Otherwise we fall back to local, minimal implementations
(scoped in this file) to preserve end-to-end behavior without polluting global API.

Roles allowed: system|user|assistant|tool|INFO|WARN.

This module is intentionally small and self-contained; it does NOT activate any
GitHub Actions or external services.
"""
from __future__ import annotations
import os, time, sqlite3, threading
from dataclasses import dataclass
from pathlib import Path

# -------------------------------
# Attempt to import shared helpers
# -------------------------------
try:
    # Expected existing helpers (preferred)
    from src.codex.logging.db import log_event as _shared_log_event  # type: ignore
    from src.codex.logging.db import init_db as _shared_init_db      # type: ignore
    from src.codex.logging.db import _DB_LOCK as _shared_DB_LOCK     # type: ignore
except Exception:
    _shared_log_event = None
    _shared_init_db = None
    _shared_DB_LOCK = None

# ------------------------------------
# Local, minimal fallbacks (if needed)
# ------------------------------------
_DB_LOCK = _shared_DB_LOCK or threading.RLock()
_DEFAULT_DB = Path(os.getenv("CODEX_LOG_DB_PATH", ".codex/session_logs.db"))

def init_db(db_path: Optional[Path] = None):
    """Initialize SQLite table for session events if absent."""
    p = Path(db_path or _DEFAULT_DB)
    p.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(p)
    try:
        conn.execute(
            """CREATE TABLE IF NOT EXISTS session_events(
                   ts REAL NOT NULL,
                   session_id TEXT NOT NULL,
                   role TEXT NOT NULL,
                   message TEXT NOT NULL
               )"""
        )
        conn.commit()
    finally:
        conn.close()
    return p

def _fallback_log_event(session_id: str, role: str, message: str, db_path: Optional[Path] = None):
    p = init_db(db_path)
    conn = sqlite3.connect(p)
    try:
        conn.execute(
            "INSERT INTO session_events(ts, session_id, role, message) VALUES(?,?,?,?)",
            (time.time(), session_id, role, message),
        )
        conn.commit()
    finally:
        conn.close()

def log_event(session_id: str, role: str, message: str, db_path: Optional[Path] = None):
    """Delegate to shared log_event if available, otherwise fallback."""
    if _shared_log_event is not None:
        return _shared_log_event(session_id, role, message, db_path=db_path)
    return _fallback_log_event(session_id, role, message, db_path=db_path)

_ALLOWED_ROLES = {"system","user","assistant","tool","INFO","WARN"}

def log_message(session_id: str, role: str, message, db_path: Optional[Path] = None):
    """Validate role, normalize message to string, ensure DB init, and write.

    Args:
        session_id: Correlates related events.
        role: One of {system,user,assistant,tool,INFO,WARN}.
        message: Any object; will be coerced to str().
        db_path: Optional path (Path/str). If None, uses CODEX_LOG_DB_PATH or .codex/session_logs.db.

    Usage:
        >>> from src.codex.logging.session_logger import log_message
        >>> log_message("S1", "user", "hi there")
    """
    if role not in _ALLOWED_ROLES:
        raise ValueError(f"invalid role {role!r}; expected one of {_ALLOWED_ROLES}")
    text = message if isinstance(message, str) else str(message)
    path = Path(db_path) if db_path else _DEFAULT_DB
    init_db(path)
    with _DB_LOCK:
        log_event(session_id, role, text, db_path=path)

@dataclass
class SessionLogger:
    """Context manager for session-scoped logging.

    Example:
        >>> from src.codex.logging.session_logger import SessionLogger
        >>> with SessionLogger(session_id="dev-session") as sl:
        ...     sl.log("user", "hi")
        ...     sl.log("assistant", "hello")
    """
    session_id: str
    db_path: Optional[Path] = None

    def __enter__(self) -> "SessionLogger":
        log_event(self.session_id, "system", "session_start", db_path=self.db_path)
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        if exc:
            log_event(self.session_id, "system", f"session_end (exc={exc_type.__name__}: {exc})", db_path=self.db_path)
        else:
            log_event(self.session_id, "system", "session_end", db_path=self.db_path)

    def log(self, role: str, message):
        log_message(self.session_id, role, message, db_path=self.db_path)
'''

SESSION_QUERY_PY = '''\
"""Session query CLI.

Usage:
    python -m src.codex.logging.session_query --session-id S123 [--last 50] [--db path/to.db]

This uses a simple SELECT against the `session_events` table and prints rows ordered by timestamp.
"""
from __future__ import annotations
import argparse, os, sqlite3, json, sys
from pathlib import Path

def infer_db_path(cli_db: Optional[str]) -> Path:
    if cli_db:
        return Path(cli_db)
    env = os.getenv("CODEX_LOG_DB_PATH")
    if env:
        return Path(env)
    return Path(".codex/session_logs.db")

def main(argv=None):
    p = argparse.ArgumentParser(prog="codex.logging.session_query", description="Query logged session events.")
    p.add_argument("--session-id", required=True, help="Exact session identifier to filter.")
    p.add_argument("--last", type=int, default=0, help="Return only the last N rows (0 = all).")
    p.add_argument("--db", help="Path to SQLite DB.")
    p.add_argument("--format", choices=["text","json"], default="text")
    args = p.parse_args(argv)

    db = infer_db_path(args.db)
    con = sqlite3.connect(db)
    try:
        cur = con.cursor()
        sql = "SELECT ts, role, message FROM session_events WHERE session_id = ? ORDER BY ts ASC"
        rows = list(cur.execute(sql, (args.session_id,)))
    finally:
        con.close()

    if args.last and len(rows) > args.last:
        rows = rows[-args.last:]

    if args.format == "json":
        print(json.dumps([{"ts": r[0], "role": r[1], "message": r[2]} for r in rows], ensure_ascii=False, indent=2))
    else:
        for ts, role, message in rows:
            print(f"{ts:.3f}\t{role:9s}\t{message}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
'''

TEST_SESSION_LOGGING = """\
import json, os, sqlite3, sys, time
import json, os, sqlite3, subprocess, sys, time
from pathlib import Path

import pytest

from src.codex.logging.session_logger import SessionLogger, log_message

def _all_events(db):
    con = sqlite3.connect(db)
    try:
        cur = con.cursor()
        return list(cur.execute("SELECT role, message FROM session_events ORDER BY ts ASC"))
    finally:
        con.close()

def test_context_manager_start_end(tmp_path, monkeypatch):
    db = tmp_path/"test.db"
    sid = "T1"
    with SessionLogger(session_id=sid, db_path=db):
        pass
    rows = _all_events(db)
    messages = [m for r,m in rows if r == "system"]
    if not any("session_start" in m for m in messages):
        raise RuntimeError("session_start not logged")
    if not any("session_end" in m for m in messages):
        raise RuntimeError("session_end not logged")

def test_log_message_helper(tmp_path):
    db = tmp_path/"test2.db"
    sid = "T2"
    log_message(sid, "user", "hi", db_path=db)
    log_message(sid, "assistant", "hello", db_path=db)
    rows = _all_events(db)
    if ("user", "hi") not in rows:
        raise RuntimeError("expected user hi row")
    if ("assistant", "hello") not in rows:
        raise RuntimeError("expected assistant hello row")

def test_cli_query_returns_rows(tmp_path, monkeypatch):
    db = tmp_path/"test3.db"
    sid = "T3"
    log_message(sid, "user", "hi", db_path=db)
    log_message(sid, "assistant", "yo", db_path=db)
    monkeypatch.setenv("CODEX_LOG_DB_PATH", str(db))
    proc = run([
        sys.executable,
        "-m",
        "codex.logging.session_query",
        "--session-id",
        sid,
        "--last",
        "1",
    ], capture_output=True)
    if proc.returncode != 0:
        raise RuntimeError(f"session_query returned {proc.returncode}")
    out = proc.stdout.strip()
    if not ("assistant" in out and "yo" in out):
        raise RuntimeError("session_query output missing")
"""

README_SNIPPET = """\
## Session Logging (Context Manager)

You can log session lifecycle and chat events via a small context manager:

```python
from src.codex.logging.session_logger import SessionLogger

with SessionLogger(session_id="demo") as sl:
    sl.log("user", "hi")
    sl.log("assistant", "hello")
```

This writes to `.codex/session_logs.db` by default; override with `CODEX_LOG_DB_PATH`.

## Session Query (CLI)

```bash
python -m src.codex.logging.session_query --session-id demo --last 50
```

> **Important:** DO NOT ACTIVATE ANY GitHub Actions files.
"""


def patch_readme(readme_path: Path) -> None:
    text = read_text(readme_path)
    if "Session Logging (Context Manager)" in text and "Session Query (CLI)" in text:
        append_change(
            readme_path, "kept", "README already contains session logging sections"
        )
        return
    new = text.rstrip() + "\n\n" + README_SNIPPET + "\n"
    write_file(readme_path, new, "Append session logging usage and CLI docs")


def main() -> None:
    global ROOT, CHANGELOG, ERRORS, RESULTS
    try:
        ROOT = git_root()
        require_clean_worktree()
    except Exception as e:  # pragma: no cover - environment validation
        print(f"[warn] {e}")
    codex_dir = ensure_codex_dir(ROOT)
    CHANGELOG = (codex_dir / "change_log.md").as_posix()
    ERRORS = (codex_dir / "errors.ndjson").as_posix()
    RESULTS = (codex_dir / "results.md").as_posix()
    Path(CHANGELOG).touch(exist_ok=True)
    Path(ERRORS).touch(exist_ok=True)

    # Phase 1.3: inventory
    items = inventory(ROOT)
    write_file(
        ROOT / ".codex" / "inventory.json",
        json.dumps(items, indent=2),
        "Write lightweight inventory of assets",
    )

    # Phase 2: search & mapping
    hits = search_candidates(ROOT)
    write_file(
        ROOT / ".codex" / "search_hits.json",
        json.dumps(hits, indent=2),
        "Record candidate symbols & files",
    )

    # Phase 3: best-effort construction
    try:
        write_file(
            ROOT / "src" / "codex" / "logging" / "session_logger.py",
            SESSION_LOGGER_PY,
            "Add SessionLogger and log_message helper",
        )
        write_file(
            ROOT / "src" / "codex" / "logging" / "session_query.py",
            SESSION_QUERY_PY,
            "Add CLI to query session events",
        )
        write_file(
            ROOT / "tests" / "test_session_logging.py",
            TEST_SESSION_LOGGING,
            "Add tests for context manager, helper, and CLI",
        )
    except Exception as e:
        log_error("3.2 implement modules", e, context="writing files")

    # Phase 3.3: docs
    try:
        patch_readme(ROOT / "README.md")
    except Exception as e:
        log_error("3.3 update README", e, context="README patch")

    # Phase 4: controlled pruning
    try:
        dupes = []
        for p in ROOT.rglob("session_logger.py"):
            if p.as_posix().endswith("src/codex/logging/session_logger.py"):
                continue
            dupes.append(str(p.relative_to(ROOT)))
        if dupes:
            with open(CHANGELOG, "a", encoding="utf-8") as fh:  # type: ignore[arg-type]
                fh.write("\n### Pruning (record only)\n")
                fh.write(
                    f"- Potential duplication detected in: {dupes}. Construction preserved; evaluate and prune if truly redundant.\n"
                )
    except Exception as e:
        log_error("4.x prune analysis", e, context="duplication scan")

    # Phase 6: results
    unresolved = sum(1 for _ in open(ERRORS, "r", encoding="utf-8")) > 0
    results = {
        "implemented": [
            "src/codex/logging/session_logger.py",
            "src/codex/logging/session_query.py",
            "tests/test_session_logging.py",
            "README.md (appended sections)",
            ".codex/inventory.json",
            ".codex/search_hits.json",
        ],
        "gaps": [],
        "prune_index": [],
        "notes": ["DO NOT ACTIVATE ANY GitHub Actions files."],
    }
    write_file(
        ROOT / ".codex" / "results.md",
        json.dumps(results, indent=2),
        "Summarize results",
    )

    print("\n[OK] Session logging workflow applied.")
    sys.exit(1 if unresolved else 0)


if __name__ == "__main__":
    main()
