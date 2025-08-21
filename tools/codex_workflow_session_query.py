#!/usr/bin/env python3
# tools/codex_workflow_session_query.py
"""
End-to-end workflow to add `codex.logging.session_query` CLI and docs.
- Dry-run by default; requires --apply (or --yes) to write.
- Never touches .github/workflows (DO_NOT_ACTIVATE_GITHUB_ACTIONS = True).
- Captures errors as ChatGPT-5 research questions in .codex/errors.ndjson.
"""

from __future__ import annotations

import argparse
import datetime
import difflib
import json
import os
import pathlib
import subprocess
import sys
import textwrap

# ----------------------------
# Globals & safety constraints
# ----------------------------
DO_NOT_ACTIVATE_GITHUB_ACTIONS = True
REPO_ROOT = None
NOW_ISO = datetime.datetime.now().astimezone().isoformat(timespec="seconds")


def run(cmd, cwd=None, check=True):
    try:
        proc = subprocess.run(cmd, cwd=cwd, check=check, capture_output=True, text=True)
        return proc.stdout.strip()
    except subprocess.CalledProcessError as e:
        raise RuntimeError(
            f"Command failed: {' '.join(cmd)}\nSTDOUT:\n{e.stdout}\nSTDERR:\n{e.stderr}"
        ) from e


def find_repo_root() -> pathlib.Path:
    try:
        p = run(["git", "rev-parse", "--show-toplevel"])
        return pathlib.Path(p)
    except Exception:
        # Fallback: current working directory
        return pathlib.Path.cwd()


def ensure_dir(p: pathlib.Path):
    p.mkdir(parents=True, exist_ok=True)


def read_text(p: pathlib.Path) -> str | None:
    try:
        return p.read_text(encoding="utf-8")
    except FileNotFoundError:
        return None


def write_if_changed(
    path: pathlib.Path, new_text: str, apply: bool, change_log, rationale: str
):
    old_text = read_text(path)
    if old_text == new_text:
        return False  # no change
    if not apply:
        change_log.append(f"- [DRY-RUN] Would write: {path}  — {rationale}")
        return False
    ensure_dir(path.parent)
    path.write_text(new_text, encoding="utf-8")
    # diff
    before = (old_text or "").splitlines(keepends=True)
    after = new_text.splitlines(keepends=True)
    udiff = "".join(
        difflib.unified_diff(
            before,
            after,
            fromfile=str(path) + " (before)",
            tofile=str(path) + " (after)",
        )
    )
    change_log.append(
        f"- Wrote: {path}\n  Rationale: {rationale}\n  Diff:\n\n```\n{udiff}\n```"
    )
    return True


def echo_and_log_error(
    step_number: str,
    step_desc: str,
    err_msg: str,
    context: str,
    errors_path: pathlib.Path,
):
    q = textwrap.dedent(f"""
    Question for ChatGPT-5:
    While performing [{step_number}: {step_desc}], encountered the following error:
    {err_msg.strip()}
    Context: {context}
    What are the possible causes, and how can this be resolved while preserving intended functionality?
    """).strip()
    print(q, file=sys.stderr)
    rec = {
        "ts": NOW_ISO,
        "step": step_number,
        "desc": step_desc,
        "error": err_msg,
        "context": context,
        "question": q,
    }
    with errors_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def is_clean_worktree(repo_root: pathlib.Path) -> bool:
    try:
        out = run(["git", "status", "--porcelain"], cwd=repo_root, check=True)
        return out.strip() == ""
    except Exception:
        return False  # treat unknown as not clean


def scan_inventory(repo_root: pathlib.Path):
    items = []
    skip_dirs = {
        ".git",
        ".venv",
        "venv",
        ".mypy_cache",
        "__pycache__",
        ".ruff_cache",
        ".pytest_cache",
    }
    for root, dirs, files in os.walk(repo_root):
        # prune
        dirs[:] = [d for d in dirs if d not in skip_dirs and not d.startswith(".")]
        for fn in files:
            if fn.endswith(
                (
                    ".py",
                    ".md",
                    ".toml",
                    ".cfg",
                    ".ini",
                    ".sql",
                    ".json",
                    ".yml",
                    ".yaml",
                    ".html",
                    ".js",
                )
            ):
                p = pathlib.Path(root) / fn
                rel = p.relative_to(repo_root)
                if ".github/workflows" in str(rel).replace("\\", "/"):
                    # Never touch actions; skip inventory if desired
                    pass
                items.append(str(rel))
    return sorted(items)[:5000]  # cap to keep lightweight


def detect_python_package_root(repo_root: pathlib.Path) -> pathlib.Path | None:
    candidates = [
        repo_root / "codex",
        repo_root / "src" / "codex",
    ]
    for c in candidates:
        if (c / "__init__.py").exists() or c.exists():
            return c
    return None


def file_exists(p: pathlib.Path) -> bool:
    try:
        return p.exists()
    except Exception:
        return False


def upsert_readme(repo_root: pathlib.Path):
    # Prefer README.md, but fallback to README or docs/README.md
    candidates = [
        repo_root / "README.md",
        repo_root / "README.MD",
        repo_root / "README",
        repo_root / "docs" / "README.md",
    ]
    for c in candidates:
        if c.exists():
            return c, (read_text(c) or "")
    # default new readme path
    return repo_root / "README.md", ""


def build_session_query_py() -> str:
    return textwrap.dedent(r'''
    """
    codex.logging.session_query
    A small CLI to query session events from a SQLite database.

    Usage:
      python -m src.codex.logging.session_query --session-id <ID> [--db PATH] [--desc]
      python -m src.codex.logging.session_query --last N [--db PATH] [--desc]
    """

    from __future__ import annotations
    import os, sys, argparse, sqlite3, shutil, textwrap
    from typing import Optional, Tuple, List

    DEFAULT_DB_CANDIDATES = [
        "data/codex.db",
        "db/codex.db",
        "codex.db",
    ]

    TS_CANDIDATES = ["timestamp", "ts", "event_ts", "created_at"]
    SID_CANDIDATES = ["session_id", "sid", "session"]

    def resolve_db_path(cli_db: Optional[str]) -> str:
        if cli_db:
            return cli_db
        env = os.getenv("CODEX_DB_PATH")
        if env:
            return env
        for c in DEFAULT_DB_CANDIDATES:
            if os.path.exists(c):
                return c
        raise FileNotFoundError("No database found. Provide --db or set CODEX_DB_PATH.")

    def detect_columns(conn: sqlite3.Connection) -> Tuple[str, str, List[str]]:
        cur = conn.cursor()
        # Find events table
        tables = [r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table'")]
        if "events" not in tables:
            # try heuristic
            ev = [t for t in tables if t.lower().startswith("event")]
            if not ev:
                raise RuntimeError(f"No 'events' table found. Tables: {tables}")
            table = ev[0]
        else:
            table = "events"
        # columns
        cols = [r[1] for r in cur.execute(f"PRAGMA table_info({table})")]
        ts_col = next((c for c in TS_CANDIDATES if c in cols), None)
        sid_col = next((c for c in SID_CANDIDATES if c in cols), None)
        if not ts_col:
            raise RuntimeError(f"No timestamp column found among {TS_CANDIDATES}. Columns={cols}")
        return table, ts_col, cols if sid_col else cols

    def guess_sid_column(cols: List[str]) -> Optional[str]:
        for c in SID_CANDIDATES:
            if c in cols:
                return c
        return None

    def run_query(db_path: str, session_id: Optional[str], last_n: Optional[int], desc: bool):
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        try:
            table, ts_col, cols = detect_columns(conn)
            sid_col = guess_sid_column(cols)
            cur = conn.cursor()

            if session_id:
                if not sid_col:
                    raise RuntimeError("Session filter requested but no session id column present.")
                order = "DESC" if desc else "ASC"
                sql = f"SELECT * FROM {table} WHERE {sid_col}=? ORDER BY {ts_col} {order}"
                rows = list(cur.execute(sql, (session_id,)))
            else:
                # last_n path (required)
                order = "DESC"  # efficient retrieval of last N
                sql = f"SELECT * FROM {table} ORDER BY {ts_col} {order} LIMIT ?"
                rows = list(cur.execute(sql, (last_n,)))
                if not desc:
                    rows = list(reversed(rows))  # display ascending if requested

            if not rows:
                print("(no rows)", file=sys.stderr)
                return 0

            # Pretty print: tab-separated header + rows
            headers = rows[0].keys()
            print("\t".join(headers))
            for r in rows:
                print("\t".join("" if v is None else str(v) for v in r))
            return 0
        finally:
            conn.close()

    def main(argv=None):
        ap = argparse.ArgumentParser(prog="python -m src.codex.logging.session_query",
                                     description="Query session events from a SQLite DB.")
        g = ap.add_mutually_exclusive_group(required=True)
        g.add_argument("--session-id", help="Filter events by session id")
        g.add_argument("--last", type=int, metavar="N", help="Show last N events by timestamp")
        ap.add_argument("--db", help="Path to SQLite DB (default: auto-discover)")
        ap.add_argument("--desc", action="store_true", help="Sort display in DESC order (default ASC for session-id)")
        args = ap.parse_args(argv)

        try:
            db = resolve_db_path(args.db)
            rc = run_query(db, args.session_id, args.last, args.desc)
            sys.exit(rc)
        except Exception as e:
            print(f"ERROR: {e}", file=sys.stderr)
            sys.exit(2)

    if __name__ == "__main__":
        main()
    ''').lstrip("\n")


def build_tests_smoke() -> str:
    return textwrap.dedent(r"""
    import importlib, sys, subprocess

    def test_import():
        mod = importlib.import_module("codex.logging.session_query")
        assert hasattr(mod, "main")

    def test_help_invocation():
        # python -m src.codex.logging.session_query --help
        proc = subprocess.run([sys.executable, "-m", "codex.logging.session_query", "--help"],
                              capture_output=True, text=True)
        assert proc.returncode == 0
        assert "Query session events" in proc.stdout
    """).lstrip("\n")


def build_readme_appendix() -> str:
    return textwrap.dedent(r"""
    ## Session Query (Experimental)

    **DO NOT ACTIVATE ANY GitHub Actions files.**

    Query session events from the local SQLite database.

    ```bash
    # by session id (ascending by default)
    python -m src.codex.logging.session_query --session-id 12345 --db data/codex.db

    # last N events (most recent first)
    python -m src.codex.logging.session_query --last 50 --db data/codex.db

    # descending order for session view (optional)
    python -m src.codex.logging.session_query --session-id 12345 --db data/codex.db --desc
    ```

    The tool auto-detects common timestamp columns (`timestamp`, `ts`, `event_ts`, `created_at`)
    and session columns (`session_id`, `sid`, `session`). Override the database path via `--db`
    or `CODEX_DB_PATH`.
    """).lstrip("\n")


def main():
    global REPO_ROOT
    ap = argparse.ArgumentParser(
        description="Add codex.logging.session_query and docs (dry-run by default)."
    )
    ap.add_argument(
        "--apply", action="store_true", help="Apply changes to the working tree"
    )
    ap.add_argument("--yes", action="store_true", help="Alias for --apply")
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()
    apply = args.apply or args.yes

    REPO_ROOT = find_repo_root()
    codex_dir = REPO_ROOT / ".codex"
    ensure_dir(codex_dir)
    change_log_path = codex_dir / "change_log.md"
    errors_path = codex_dir / "errors.ndjson"
    results_path = codex_dir / "results.md"

    change_log_notes = []
    results_lines = [f"# Results — {NOW_ISO}", ""]

    # Phase 1: Prep
    try:
        if not is_clean_worktree(REPO_ROOT):
            raise RuntimeError(
                "Working tree is not clean. Commit/stash changes before running."
            )
    except Exception as e:
        echo_and_log_error(
            "1.1",
            "Verify clean working state",
            str(e),
            f"repo={REPO_ROOT}",
            errors_path,
        )
        print("Aborting due to unclean state (or unable to verify).", file=sys.stderr)
        sys.exit(3)

    inventory = scan_inventory(REPO_ROOT)
    results_lines.append("## Inventory (lightweight)")
    results_lines.extend([f"- {p}" for p in inventory[:200]])
    if len(inventory) > 200:
        results_lines.append(f"... (+{len(inventory) - 200} more)")

    # Phase 2: Mapping
    pkg_root = detect_python_package_root(REPO_ROOT)
    if not pkg_root:
        echo_and_log_error(
            "2.2",
            "Detect Python package root",
            "No 'codex' package found",
            f"repo={REPO_ROOT}",
            errors_path,
        )
        # Best-effort: prepare 'codex' if applying
        pkg_root = REPO_ROOT / "codex"
        if apply:
            ensure_dir(pkg_root)
            write_if_changed(
                pkg_root / "__init__.py",
                "# codex package\n",
                apply,
                change_log_notes,
                "Create package root",
            )
        else:
            change_log_notes.append(
                "- [DRY-RUN] Would create codex/__init__.py (package root)"
            )

    logging_pkg = pkg_root / "logging"
    if apply and not file_exists(logging_pkg):
        ensure_dir(logging_pkg)
    if not (logging_pkg / "__init__.py").exists():
        write_if_changed(
            logging_pkg / "__init__.py",
            "# codex.logging package\n",
            apply,
            change_log_notes,
            "Ensure logging package",
        )

    # Phase 3: Construction
    session_query_path = logging_pkg / "session_query.py"
    write_if_changed(
        session_query_path,
        build_session_query_py(),
        apply,
        change_log_notes,
        "Add CLI module for session queries",
    )

    # tests
    tests_dir = REPO_ROOT / "tests"
    ensure_dir(tests_dir)
    write_if_changed(
        tests_dir / "test_session_query_smoke.py",
        build_tests_smoke(),
        apply,
        change_log_notes,
        "Add smoke tests for session_query",
    )

    # README updates
    readme_path, readme_text = upsert_readme(REPO_ROOT)
    appendix = build_readme_appendix()
    if "Session Query (Experimental)" not in (readme_text or ""):
        new_readme = (readme_text + ("\n\n" if readme_text else "")) + appendix
        write_if_changed(
            readme_path,
            new_readme,
            apply,
            change_log_notes,
            "Append Session Query usage docs",
        )
    else:
        change_log_notes.append(
            f"- README already contains Session Query section: {readme_path}"
        )

    # Phase 4: Pruning (none expected here)
    # Document no-op pruning
    change_log_notes.append(
        "- Pruning: none required; new module is localized and non-invasive."
    )

    # Phase 5: Errors already captured via echo_and_log_error

    # Phase 6: Finalization
    results_lines.append("")
    results_lines.append("## Implemented")
    results_lines.extend(
        [
            "- Added `codex/logging/session_query.py` with CLI (`python -m src.codex.logging.session_query`).",
            "- Auto-detection of DB path + timestamp/session columns.",
            "- Smoke tests under `tests/test_session_query_smoke.py`.",
            "- README usage section appended.",
        ]
    )
    results_lines.append("")
    results_lines.append("## Explicit Constraint")
    results_lines.append("**DO NOT ACTIVATE ANY GitHub Actions files.**")
    results_lines.append("")
    results_lines.append("## Next Steps")
    results_lines.extend(
        [
            "- Provide a stable DB path (e.g., `data/codex.db`) or set `CODEX_DB_PATH`.",
            "- Optionally add console_scripts entry in packaging if you want a `codex-session-query` binary.",
            "- Extend filters (date range, event types) if needed.",
        ]
    )

    # Write logs
    ensure_dir(codex_dir)
    if apply:
        with change_log_path.open("a", encoding="utf-8") as f:
            f.write(f"\n\n## Run @ {NOW_ISO}\n")
            for line in change_log_notes:
                f.write(line + "\n")
    else:
        print("\n".join(["# Planned Change Log (dry-run)"] + change_log_notes))

    results = "\n".join(results_lines) + "\n"
    if apply:
        results_path.write_text(results, encoding="utf-8")
    else:
        print("\n# Planned Results (dry-run)\n" + results)

    # exit code based on errors.ndjson presence with content
    unresolved = errors_path.exists() and errors_path.stat().st_size > 0
    sys.exit(1 if unresolved else 0)


if __name__ == "__main__":
    main()
