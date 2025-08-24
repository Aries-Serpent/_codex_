#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Codex Supplied Task Runner (safe-local)
- Adds descriptive docstrings to target modules
- Updates README/AGENTS with CODEX_SQLITE_POOL + log layout & retention
- Writes .codex/change_log.md and .codex/errors.ndjson
- Optionally runs `pre-commit run --files <edited>`
- Never touches .github/workflows and refuses to run in CI
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shlex
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path.cwd()
CODEX_DIR = ROOT / ".codex"
CHANGE_LOG = CODEX_DIR / "change_log.md"
ERRORS_LOG = CODEX_DIR / "errors.ndjson"
RESULTS = CODEX_DIR / "results.md"

TARGETS = [
    "src/codex/logging/session_query.py",
    "src/codex/logging/viewer.py",
    "src/codex/logging/export.py",
]
README = ROOT / "README.md"
AGENTS = ROOT / "AGENTS.md"
PRE_COMMIT = ROOT / ".pre-commit-config.yaml"

DOCSTRINGS = {
    "src/codex/logging/viewer.py": '''"""
CLI viewer for session-scoped logs stored in SQLite.

Purpose:
    Render session events (chronological) as text or JSON with optional filters.

Usage:
    python -m codex.logging.viewer --session-id <ID> [--db path/to.db]
      [--format json|text] [--level INFO --contains token]
      [--since 2025-01-01 --until 2025-12-31] [--limit 200] [--table logs]

Environment:
    CODEX_LOG_DB_PATH   Override default DB path (defaults to .codex/session_logs.db).
    CODEX_SQLITE_POOL   If "1", prefer a pooled/shared connection for reduced overhead.

Examples:
    export CODEX_LOG_DB_PATH=".codex/session_logs.db"
    export CODEX_SQLITE_POOL=1
    python -m codex.logging.viewer --session-id S123 --format text --limit 100
    python -m codex.logging.viewer --session-id S123 --format json --since 2025-01-01

Notes:
    The README documents log viewing and exporting; flags here mirror that flow.
"""''',
    "src/codex/logging/export.py": '''"""
Export all events for a given session as JSON or plain text.

Usage:
    python -m codex.logging.export SESSION_ID --format {json,text}
    # custom DB:
    python -m codex.logging.export SESSION_ID --db /path/to/db.sqlite

Environment:
    CODEX_LOG_DB_PATH   Default DB path if --db not provided.
    CODEX_SQLITE_POOL   If "1", enable pooled connection behavior.

Examples:
    export CODEX_LOG_DB_PATH=".codex/session_logs.db"
    python -m codex.logging.export S123 --format json > out.json
    python -m codex.logging.export S123 --format text > out.txt

Behavior:
    Reads from default DB (e.g., .codex/session_logs.db) unless overridden.
"""''',
    "src/codex/logging/session_query.py": '''"""
Query logs across sessions with flexible filters (id/role/time/contains).

Usage:
    python -m codex.logging.session_query --session-id <ID>
      [--role user|assistant|system|tool] [--contains substring]
      [--after YYYY-MM-DD] [--before YYYY-MM-DD]
      [--order asc|desc] [--limit N] [--offset N] [--table logs]

Environment:
    CODEX_LOG_DB_PATH   Path to SQLite file with log rows.
    CODEX_SQLITE_POOL   If "1", prefer a pooled shared connection.

Examples:
    export CODEX_LOG_DB_PATH=".codex/session_logs.db"
    python -m codex.logging.session_query --session-id S123 --role user --after 2025-01-01

Columns:
    Expects compatible column names (e.g., session_id/session, ts/timestamp, message/content, level/severity).
"""''',
}

README_INSERT = """
#### SQLite Connection Pooling

Set `CODEX_SQLITE_POOL=1` to prefer a pooled/shared SQLite connection in CLI tools
(e.g., viewer/query/export). This reduces connection churn and can improve throughput
on repeated commands. Default is non-pooled behavior.

Examples:
  export CODEX_SQLITE_POOL=1
  python -m codex.logging.viewer --session-id S123 --format text
  python -m codex.logging.export  S123 --format json
""".lstrip()

AGENTS_BLOCK = """
### Log Directory Layout & Retention

Structure:
  ./.codex/
    session_logs.db
    sessions/
      <SESSION_ID>.ndjson

Retention:
  Keep NDJSON files and SQLite rows for 30 days. Purge anything older.

Symbolic policy:
  purge(file) = 1 if age_days(file) > 30 else 0

POSIX purge example:
  find ./.codex/sessions -type f -mtime +30 -print -delete || true

PowerShell purge example:
  Get-ChildItem .\.codex\sessions -File | Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-30) } | Remove-Item -Force
""".lstrip()


def now() -> str:
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")


def ensure_codex_dirs() -> None:
    CODEX_DIR.mkdir(parents=True, exist_ok=True)
    if not CHANGE_LOG.exists():
        CHANGE_LOG.write_text(f"# Change Log\n\nInitialized {now()}\n")
    if not ERRORS_LOG.exists():
        ERRORS_LOG.write_text("")
    if not RESULTS.exists():
        RESULTS.write_text(f"# Results\n\nInitialized {now()}\n")


def log_change(title: str, details: str) -> None:
    with CHANGE_LOG.open("a", encoding="utf-8") as f:
        f.write(f"\n## {title}\n\n{details}\n")


def record_error(step: str, err: str, ctx: str = "") -> None:
    payload = {
        "ts": now(),
        "step": step,
        "error": err,
        "context": ctx,
        "chatgpt5_question": (
            "Question for ChatGPT-5:\n"
            f"While performing [{step}], encountered the following error:\n{err}\n"
            f"Context: {ctx}\n"
            "What are the possible causes, and how can this be resolved while preserving intended functionality?"
        ),
    }
    with ERRORS_LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload) + "\n")
    print(payload["chatgpt5_question"], file=sys.stderr)


def run(cmd: list[str], check: bool = False) -> subprocess.CompletedProcess:
    return subprocess.run(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=check
    )


def is_clean_repo() -> bool:
    try:
        r = run(["git", "status", "--porcelain"])
        return r.returncode == 0 and r.stdout.strip() == ""
    except Exception:
        return True


def guard_no_ci() -> None:
    if os.getenv("GITHUB_ACTIONS"):
        record_error(
            "1.4 GUARD",
            "Running in GitHub Actions is forbidden",
            "Environment=GITHUB_ACTIONS",
        )
        sys.exit(2)


def inject_docstring(path: Path, doc: str, apply: bool, changed: list[str]) -> None:
    if not path.exists():
        record_error(
            "3.1 DOCSTRINGS", f"Missing target file: {path}", "Will skip insertion"
        )
        return
    text = path.read_text(encoding="utf-8")
    orig = text
    has_top_doc = bool(re.match(r'^\s*("""|\'\'\')', text))
    if not has_top_doc:
        text = doc + "\n" + text
        if apply:
            path.write_text(text, encoding="utf-8")
        changed.append(str(path))
        before = orig.splitlines()[:5]
        after = text.splitlines()[:12]
        log_change(
            f"Docstring added: {path}",
            "**Before (head):**\n```\n"
            + "\n".join(before)
            + "\n```\n\n"
            + "**After (head):**\n```\n"
            + "\n".join(after)
            + "\n```\n",
        )
    else:
        log_change(
            f"Docstring unchanged: {path}", "Existing top-level docstring detected."
        )


def patch_readme(apply: bool, changed: list[str]) -> None:
    if not README.exists():
        record_error("3.3 README", "README.md not found", "Skipping README patch")
        return
    text = README.read_text(encoding="utf-8")
    if "SQLite Connection Pooling" in text or "CODEX_SQLITE_POOL" in text:
        log_change("README.md", "Pooling section already present; no change.")
        return
    idx = text.lower().find("session logging")
    new_text = None
    if idx != -1:
        m = re.search(r"(###[^\n]*session logging[^\n]*\n)", text, re.IGNORECASE)
        if m:
            insert_at = m.end()
            new_text = text[:insert_at] + "\n" + README_INSERT + "\n" + text[insert_at:]
    if new_text is None:
        new_text = text.rstrip() + "\n\n" + README_INSERT + "\n"
    if apply:
        README.write_text(new_text, encoding="utf-8")
    changed.append(str(README))
    log_change(
        "README.md", "Inserted `SQLite Connection Pooling` subsection with examples."
    )


def patch_agents_or_readme(apply: bool, changed: list[str]) -> None:
    target = AGENTS if AGENTS.exists() else README
    if not target.exists():
        record_error(
            "3.3 AGENTS/README",
            "Neither AGENTS.md nor README.md exist",
            "Cannot document log layout & retention",
        )
        return
    text = target.read_text(encoding="utf-8")
    if "Log Directory Layout & Retention" in text:
        log_change(target.name, "Retention section already present; no change.")
        return
    new_text = text.rstrip() + "\n\n" + AGENTS_BLOCK + "\n"
    if apply:
        target.write_text(new_text, encoding="utf-8")
    changed.append(str(target))
    log_change(target.name, "Appended `Log Directory Layout & Retention` section.")


def write_results(changed: list[str]) -> int:
    errors = ERRORS_LOG.read_text(encoding="utf-8").strip()
    ok = errors == ""
    summary = [
        f"Completed: {now()}",
        "",
        "## Implemented",
        "- Module docstrings for: session_query.py, viewer.py, export.py (if present).",
        "- README: SQLite pooling section.",
        "- AGENTS/README: log directory + 30-day retention.",
        f"- Lint via pre-commit for {len(changed)} file(s) (if configured).",
        "",
        "## Residual gaps",
        "- Any missing target files are recorded in errors.ndjson.",
        "",
        "## Pruning decisions",
        "- (None performed unless duplicates detected.)",
        "",
        "## Next steps",
        "- Validate CLI flags vs. actual implementations.",
        "- Consider adding unit smoke-tests for each CLI module.",
        "",
        "## Policy",
        "**DO NOT ACTIVATE ANY GitHub Actions files.**",
    ]
    with RESULTS.open("a", encoding="utf-8") as f:
        f.write("\n".join(summary) + "\n")
    return 0 if ok else 1


def maybe_pre_commit(changed: list[str]) -> None:
    if not changed:
        return
    if not PRE_COMMIT.exists():
        log_change("pre-commit", "Config not present; skipping.")
        return
    try:
        cmd = ["pre-commit", "run", "--files", *changed]
        r = run(cmd)
        log_change(
            "pre-commit",
            f"Command: {' '.join(shlex.quote(x) for x in cmd)}\nExit: {r.returncode}\nSTDOUT:\n{r.stdout}\nSTDERR:\n{r.stderr}",
        )
        if r.returncode != 0:
            record_error(
                "3.5 LINT",
                f"`pre-commit` failed with exit {r.returncode}",
                r.stderr[:1024],
            )
    except FileNotFoundError as e:
        record_error("3.5 LINT", "pre-commit not installed", str(e))


def build_inventory() -> None:
    items = []
    for p in ROOT.rglob("*"):
        try:
            if p.is_file():
                st = p.stat()
                items.append(
                    {
                        "path": str(p.relative_to(ROOT)),
                        "size": st.st_size,
                        "mtime": st.st_mtime,
                    }
                )
        except Exception:
            continue
    (CODEX_DIR / "inventory.json").write_text(
        json.dumps(items, indent=2), encoding="utf-8"
    )
    log_change("Inventory", f"{len(items)} files indexed.")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="Write changes to disk")
    ap.add_argument("--dry-run", action="store_true", help="Preview only; do not write")
    args = ap.parse_args()

    if os.getenv("GITHUB_ACTIONS"):
        guard_no_ci()

    ensure_codex_dirs()
    build_inventory()

    if not is_clean_repo():
        record_error(
            "1.1 CLEAN", "Uncommitted changes detected", "Proceeding anyway (non-fatal)"
        )

    changed: list[str] = []

    for rel in TARGETS:
        p = ROOT / rel
        doc = DOCSTRINGS.get(rel)
        if doc:
            inject_docstring(
                p, doc, apply=(args.apply and not args.dry_run), changed=changed
            )

    patch_readme(apply=(args.apply and not args.dry_run), changed=changed)
    patch_agents_or_readme(apply=(args.apply and not args.dry_run), changed=changed)

    maybe_pre_commit(changed)

    code = write_results(changed)
    sys.exit(code)


if __name__ == "__main__":
    main()
