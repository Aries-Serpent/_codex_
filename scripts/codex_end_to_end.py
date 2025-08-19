#!/usr/bin/env python3
"""
codex_end_to_end.py — End-to-end workflow executor for the `_codex_` repository.

What it does (best-effort, non-destructive):
- Verifies clean git state (warns if dirty).
- Inventories repo assets.
- Creates/updates `src/codex/logging/viewer.py` (CLI: --session-id, filters, --format json|text).
- Adds/updates README section "Session Logging (SQLite)".
- Adds automated smoke test invoking the CLI via subprocess.
- Writes .codex/change_log.md, .codex/errors.ndjson, .codex/results.md.
- Does NOT activate GitHub Actions; warns if workflows exist.

Run:
  python scripts/codex_end_to_end.py --repo . --yes
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sqlite3
try:
    from codex.db.sqlite_patch import auto_enable_from_env as _codex_sqlite_auto
    _codex_sqlite_auto()
except Exception:
    pass
import subprocess
import sys
import textwrap
import difflib
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

# ----------- Config / Flags -----------
DO_NOT_ACTIVATE_GITHUB_ACTIONS = True
DEFAULT_WEIGHTS = {"alpha": 0.5, "beta": 0.35, "gamma": 0.15}


# ----------- Helpers -----------
def now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def read_text(p: Path) -> str:
    return p.read_text(encoding="utf-8") if p.exists() else ""


def write_text(p: Path, content: str) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")


def append_text(p: Path, content: str) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a", encoding="utf-8") as f:
        f.write(content)


def run_cmd(cmd: List[str], cwd: Optional[Path] = None) -> Tuple[int, str, str]:
    try:
        proc = subprocess.run(
            cmd,
            cwd=str(cwd) if cwd else None,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )
        return proc.returncode, proc.stdout, proc.stderr
    except Exception as e:
        return 1, "", str(e)


def unified_diff(old: str, new: str, path: str) -> str:
    return "".join(
        difflib.unified_diff(
            old.splitlines(True),
            new.splitlines(True),
            fromfile=f"{path} (old)",
            tofile=f"{path} (new)",
            lineterm="",
        )
    )


def log_change(
    change_log: Path,
    file_path: Path,
    action: str,
    rationale: str,
    before: str,
    after: str,
) -> None:
    diff = unified_diff(before, after, str(file_path))
    entry = (
        textwrap.dedent(
            f"""
    ## {now_iso()} — {action}: {file_path}
    Rationale: {rationale}

    <details><summary>Diff</summary>

    ```diff
    {diff if diff.strip() else '(no textual diff or file created)'}
    ```

    </details>
    """
        ).strip()
        + "\n\n"
    )
    append_text(change_log, entry)


def log_error(errors_file: Path, step: str, err: str, ctx: str) -> None:
    entry = {"time": now_iso(), "step": step, "error": err, "context": ctx}
    append_text(errors_file, json.dumps(entry) + "\n")
    echo = textwrap.dedent(
        f"""
    Question for ChatGPT-5:
    While performing [{step}], encountered the following error:
    {err}
    Context: {ctx}
    What are the possible causes, and how can this be resolved while preserving intended functionality?
    """
    ).strip()
    print(echo, file=sys.stderr)


def is_git_clean(repo: Path) -> bool:
    code, out, _ = run_cmd(["git", "status", "--porcelain"], cwd=repo)
    if code != 0:
        return True
    return out.strip() == ""


def inventory(repo: Path) -> List[Dict[str, str]]:
    items: List[Dict[str, str]] = []
    for p in repo.rglob("*"):
        if any(seg in {".git", ".venv", ".mypy_cache", "__pycache__", ".tox", ".pytest_cache"} for seg in p.parts):
            continue
        if p.is_file():
            kind = (
                "code"
                if p.suffix in {".py", ".js", ".ts", ".sh", ".sql"}
                else "doc"
                if p.suffix in {".md", ".rst"}
                else "other"
            )
            items.append({"path": str(p.relative_to(repo)), "type": kind, "brief_role": ""})
    return items


def ensure_section_in_readme(
    readme: Path, section_title: str, new_section_md: str, change_log: Path
) -> None:
    before = read_text(readme)
    if not before:
        write_text(
            readme,
            f"# {_repo_name_from_cwd()}\n\n{new_section_md}\n",
        )
        log_change(
            change_log,
            readme,
            "Create README.md",
            "Initialize README with Session Logging section.",
            "",
            read_text(readme),
        )
        return

    pattern = re.compile(
        rf"(^|\n)#+\s+{re.escape(section_title)}\s*(\n|$)", re.IGNORECASE
    )
    if pattern.search(before):
        replaced = _replace_markdown_section(before, section_title, new_section_md)
        if replaced != before:
            write_text(readme, replaced)
            log_change(
                change_log,
                readme,
                "Update README.md",
                f"Refresh '{section_title}' section.",
                before,
                replaced,
            )
    else:
        after = before.rstrip() + "\n\n" + new_section_md + "\n"
        write_text(readme, after)
        log_change(
            change_log,
            readme,
            "Append README.md",
            f"Add '{section_title}' section.",
            before,
            after,
        )


def _replace_markdown_section(content: str, title: str, new_md: str) -> str:
    lines = content.splitlines()
    start_idx = None
    for i, line in enumerate(lines):
        if re.match(rf"^#+\s+{re.escape(title)}\s*$", line, flags=re.IGNORECASE):
            start_idx = i
            break
    if start_idx is None:
        return content
    end_idx = len(lines)
    for j in range(start_idx + 1, len(lines)):
        if re.match(r"^#+\s+\S", lines[j]):
            end_idx = j
            break
    new_block = new_md.strip().splitlines()
    return "\n".join(lines[:start_idx] + new_block + lines[end_idx:]) + (
        "\n" if content.endswith("\n") else ""
    )


def _repo_name_from_cwd() -> str:
    return Path.cwd().name


# ----------- Viewer.py content (robust CLI) -----------
VIEWER_PY = r'''# -*- coding: utf-8 -*-
"""
src/codex/logging/viewer.py — SQLite-backed session log viewer.

CLI:
  python -m src.codex.logging.viewer --session-id ABC123 [--db path/to.db] [--format json|text]
                                      [--level INFO --contains token --since 2025-01-01 --until 2025-12-31]
                                      [--limit 200] [--table logs]

Best-effort schema inference:
- Finds a table with columns like: session_id/session/ctx, ts/timestamp/time/created_at, message/msg, level/lvl.
- Orders chronologically by inferred timestamp column (ASC).
"""
from __future__ import annotations
import argparse, json, os, sqlite3, sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

CANDIDATE_TS = ["ts","timestamp","time","created_at","logged_at"]
CANDIDATE_SID = ["session_id","session","sid","context_id"]
CANDIDATE_MSG = ["message","msg","text","detail"]
CANDIDATE_LVL = ["level","lvl","severity","log_level"]

def parse_args(argv: Optional[List[str]]=None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Session Logging (SQLite) viewer")
    p.add_argument("--session-id", required=True, help="Session identifier to filter")
    p.add_argument("--db", default=None, help="Path to SQLite database (autodetects common names if omitted)")
    p.add_argument("--format", choices=["json","text"], default="text", help="Output format")
    p.add_argument("--level", action="append", help="Filter by level (repeatable)")
    p.add_argument("--contains", help="Substring filter on message (case-insensitive)")
    p.add_argument("--since", help="ISO date/time lower bound (inclusive)")
    p.add_argument("--until", help="ISO date/time upper bound (inclusive)")
    p.add_argument("--limit", type=int, help="Max rows to return")
    p.add_argument("--table", help="Explicit table name (skip inference)")
    return p.parse_args(argv)

def autodetect_db(root: Path) -> Optional[Path]:
    """Locate a database under ``root`` without deep filesystem scans."""
    # Prefer explicit, common locations
    candidates = [
        root/".codex"/"session_logs.db",
        root/"data"/"logs.sqlite",
        root/"data"/"logs.db",
        root/"logs.db",
    ]
    for c in candidates:
        if c.exists():
            return c

    # Shallow scan: inspect only root, `.codex`, and `data` directories
    for base in (root/".codex", root/"data", root):
        if base.exists():
            for pattern in ("*.db", "*.sqlite"):
                for p in base.glob(pattern):
                    if p.is_file():
                        return p
    return None

def connect_db(db_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    return conn

def list_tables(conn: sqlite3.Connection) -> List[str]:
    rows = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'").fetchall()
    return [r["name"] for r in rows]

def table_columns(conn: sqlite3.Connection, table: str) -> List[str]:
    rows = conn.execute(f"PRAGMA table_info({table})").fetchall()
    return [r["name"] for r in rows]

def infer_schema(conn: sqlite3.Connection, explicit_table: Optional[str]=None) -> Dict[str,str]:
    candidates = [explicit_table] if explicit_table else list_tables(conn)
    for t in candidates:
        if not t:
            continue
        cols = [c.lower() for c in table_columns(conn, t)]
        def pick(pref: List[str]) -> Optional[str]:
            for k in pref:
                if k in cols: return k
            return None
        ts = pick(CANDIDATE_TS)
        sid = pick(CANDIDATE_SID)
        msg = pick(CANDIDATE_MSG)
        lvl = pick(CANDIDATE_LVL)
        if sid and ts and msg:
            return {"table": t, "sid": sid, "ts": ts, "msg": msg, "lvl": lvl}
    raise RuntimeError("No suitable table found (need at least session_id, timestamp, message columns).")

def parse_iso(s: Optional[str]) -> Optional[str]:
    if not s: return None
    try:
        return datetime.fromisoformat(s).isoformat(sep=" ", timespec="seconds")
    except Exception:
        return s

def build_query(schema: Dict[str,str], level: Optional[List[str]], contains: Optional[str],
                since: Optional[str], until: Optional[str], limit: Optional[int]) -> (str, list):
    t, sid, ts, msg, lvl = schema["table"], schema["sid"], schema["ts"], schema["msg"], schema.get("lvl")
    where = [f"{sid} = ?"]
    args: List[Any] = []
    if level and lvl:
        placeholders = ",".join(["?"]*len(level))
        where.append(f"{lvl} IN ({placeholders})")
        args.extend([v for v in level])
    if contains:
        where.append(f"LOWER({msg}) LIKE ?")
        args.append(f"%{contains.lower()}%")
    s_iso = parse_iso(since)
    u_iso = parse_iso(until)
    if s_iso:
        where.append(f"{ts} >= ?")
        args.append(s_iso)
    if u_iso:
        where.append(f"{ts} <= ?")
        args.append(u_iso)
    where_clause = " AND ".join(where)
    q = f"SELECT * FROM {t} WHERE {where_clause} ORDER BY {ts} ASC"
    if limit:
        q += f" LIMIT {int(limit)}"
    args = [None] + args
    return q, args

def main(argv: Optional[List[str]]=None) -> int:
    ns = parse_args(argv)
    root = Path.cwd()
    db_path = Path(ns.db) if ns.db else autodetect_db(root)
    if not db_path:
        print("ERROR: SQLite DB not found. Provide --db or place logs.db/logs.sqlite in repo.", file=sys.stderr)
        return 2
    try:
        conn = connect_db(db_path)
        schema = infer_schema(conn, ns.table)
        q, args = build_query(schema, ns.level, ns.contains, ns.since, ns.until, ns.limit)
        args[0] = ns.session_id
        rows = conn.execute(q, args).fetchall()
        if ns.format == "json":
            print(json.dumps([dict(r) for r in rows], ensure_ascii=False, indent=2))
        else:
            for r in rows:
                ts = r.get(schema["ts"], "")
                lvl = r.get(schema.get("lvl") or "", "")
                msg = r.get(schema["msg"], "")
                print(f"{ts} {('['+lvl+'] ') if lvl else ''}{msg}")
        return 0
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    raise SystemExit(main())
'''

# ----------- Pytest smoke test -----------
TEST_VIEWER = r'''# -*- coding: utf-8 -*-
import json, sqlite3, subprocess, sys, tempfile
from pathlib import Path

def _make_db(tmp: Path) -> Path:
    db = tmp/"logs.db"
    conn = sqlite3.connect(str(db))
    conn.execute("""CREATE TABLE logs(
        session_id TEXT, ts TEXT, level TEXT, message TEXT
    )""")
    rows = [
        ("S-1","2025-08-18 01:00:00","INFO","start session"),
        ("S-1","2025-08-18 01:01:00","WARN","minor warning"),
        ("S-2","2025-08-18 01:02:00","INFO","other session"),
        ("S-1","2025-08-18 01:03:00","ERROR","boom"),
    ]
    conn.executemany("INSERT INTO logs VALUES (?,?,?,?)", rows)
    conn.commit(); conn.close()
    return db

def test_cli_text_output(tmp_path: Path):
    db = _make_db(tmp_path)
    viewer = Path("src/codex/logging/viewer.py").resolve()
    cmd = [sys.executable, str(viewer), "--session-id","S-1","--db", str(db), "--format","text"]
    p = subprocess.run(cmd, capture_output=True, text=True)
    assert p.returncode == 0, p.stderr
    out = p.stdout.strip().splitlines()
    assert out[0].endswith("start session")
    assert out[-1].endswith("boom")
    assert len(out) == 3

def test_cli_json_output(tmp_path: Path):
    db = _make_db(tmp_path)
    viewer = Path("src/codex/logging/viewer.py").resolve()
    cmd = [sys.executable, str(viewer), "--session-id","S-1","--db", str(db), "--format","json","--level","ERROR"]
    p = subprocess.run(cmd, capture_output=True, text=True)
    assert p.returncode == 0, p.stderr
    data = json.loads(p.stdout)
    assert len(data) == 1
    assert data[0]["message"] == "boom"
'''

# ----------- README section -----------
README_SECTION_TITLE = "Session Logging (SQLite)"
README_SECTION = f"""## {README_SECTION_TITLE}

This repository provides a CLI viewer for session-scoped logs stored in SQLite.

### Usage
```bash
python -m src.codex.logging.viewer --session-id <ID> [--db path/to.db] [--format json|text] \\
  [--level INFO --contains token --since 2025-01-01 --until 2025-12-31] [--limit 200] [--table logs]
```

* **--session-id** (required): Which session to view.
* **--db**: Path to the SQLite DB. If omitted, common names like `data/logs.sqlite` or `logs.db` are autodetected.
* **--format**: Output `json` or `text` (default).
* **--level**: Filter by level (repeatable), e.g., `--level INFO --level ERROR`.
* **--contains**: Case-insensitive substring match over the message.
* **--since / --until**: ISO timestamps or dates. Results are chronological.
* **--limit**: Cap the number of returned rows.
* **--table**: Explicit table name. If omitted, the CLI infers a suitable table/columns.

> **Note:** Inference expects columns like `session_id`, `ts`/`timestamp`, and `message`. If levels are present, common names (`level`, `severity`) are detected.

**DO NOT ACTIVATE ANY GitHub Actions files.**
"""

# ----------- Mapping & scoring (Phase 2) -----------

def score_candidate(io_ok: float, cohesion: float, risk: float, w=DEFAULT_WEIGHTS) -> float:
    return w["alpha"] * io_ok + w["beta"] * cohesion - w["gamma"] * risk


def search_candidates(repo: Path) -> Dict[str, Any]:
    found = {"sqlite_usage": [], "cli_helpers": [], "tests": []}
    for p in repo.rglob("*.py"):
        txt = read_text(p)
        if "sqlite3" in txt:
            found["sqlite_usage"].append(str(p.relative_to(repo)))
        if re.search(r"\b(argparse|click|typer)\b", txt):
            found["cli_helpers"].append(str(p.relative_to(repo)))
        if p.parts and "tests" in p.parts:
            found["tests"].append(str(p.relative_to(repo)))

    mapping = {
        "Create viewer CLI": {
            "candidates": found["cli_helpers"],
            "selected": found["cli_helpers"][:1],
            "rationale": "Prefer existing CLI patterns; fallback to argparse in new module.",
        },
        "SQLite integration": {
            "candidates": found["sqlite_usage"],
            "selected": found["sqlite_usage"][:1],
            "rationale": "Leverage similar DB access idioms if present; else fresh implementation.",
        },
        "Testing strategy": {
            "candidates": found["tests"],
            "selected": found["tests"][:1],
            "rationale": "Match repository test runner; default to pytest-style smoke tests.",
        },
    }
    return mapping


# ----------- Main workflow -----------

def main() -> int:
    ap = argparse.ArgumentParser(description="Codex end-to-end workflow executor")
    ap.add_argument("--repo", default=".", help="Path to repository root")
    ap.add_argument("--yes", action="store_true", help="Proceed without interactive prompts")
    args = ap.parse_args()

    repo = Path(args.repo).resolve()
    codex_dir = repo / ".codex"
    change_log = codex_dir / "change_log.md"
    errors_file = codex_dir / "errors.ndjson"
    results = codex_dir / "results.md"

    try:
        codex_dir.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        log_error(errors_file, "1.5: init .codex", str(e), f"repo={repo}")
        return 2

    if not is_git_clean(repo):
        msg = "Working tree not clean (git status). Proceeding anyway (best-effort)."
        log_error(errors_file, "1.1: verify clean", msg, "Safety: will still write files; user can review diffs.")
        print(msg, file=sys.stderr)

    readme = repo / "README.md"
    contributing = None
    for name in ("CONTRIBUTING.md", "CONTRIBUTING.rst", ".github/CONTRIBUTING.md"):
        p = repo / name
        if p.exists():
            contributing = p
            break

    inv = inventory(repo)

    mapping = search_candidates(repo)

    viewer_path = repo / "src" / "codex" / "logging" / "viewer.py"
    before_viewer = read_text(viewer_path)
    try:
        write_text(viewer_path, VIEWER_PY)
        log_change(
            change_log,
            viewer_path,
            "Write",
            "Add robust SQLite session log viewer CLI.",
            before_viewer,
            read_text(viewer_path),
        )
    except Exception as e:
        log_error(errors_file, "3.2: write viewer.py", str(e), f"path={viewer_path}")

    try:
        ensure_section_in_readme(readme, README_SECTION_TITLE, README_SECTION, change_log)
    except Exception as e:
        log_error(errors_file, "3.3: update README", str(e), f"path={readme}")

    test_path = repo / "tests" / "test_logging_viewer_cli.py"
    before_test = read_text(test_path)
    try:
        write_text(test_path, TEST_VIEWER)
        log_change(
            change_log,
            test_path,
            "Write",
            "Add CLI smoke tests for viewer.",
            before_test,
            read_text(test_path),
        )
    except Exception as e:
        log_error(errors_file, "3.4: write tests", str(e), f"path={test_path}")

    snapshot = textwrap.dedent(
        f"""
# Snapshot — {now_iso()}

## Inventory (truncated to first 50)
{os.linesep.join(f"- {i['path']} ({i['type']})" for i in inv[:50])}

## Mapping
```json
{json.dumps(mapping, indent=2)}
```
"""
    ).strip() + "\n"
    append_text(change_log, snapshot)

    if DO_NOT_ACTIVATE_GITHUB_ACTIONS and (repo / ".github" / "workflows").exists():
        print(
            "NOTICE: .github/workflows exists. This tool does not enable or modify CI files.",
            file=sys.stderr,
        )

    unresolved = read_text(errors_file).strip() != ""
    summary = textwrap.dedent(
        f"""
# Results Summary — {now_iso()}

## Implemented
- `src/codex/logging/viewer.py` CLI created (session-scoped SQLite viewer; text/JSON; filters; chronological).
- README updated with **Session Logging (SQLite)** usage.
- Pytest smoke tests added: `tests/test_logging_viewer_cli.py`.

## Residual Gaps
- Real DB schema may differ; viewer uses best-effort inference. If your schema lacks `session_id`/`timestamp`/`message` equivalents, pass `--table` and consider adding a view.

## Pruning
- No assets pruned in this pass.

## Next Steps
- Run tests: `pytest -q` (or your repo's test runner).
- Integrate viewer into your dev workflow or CI *without enabling GH Actions here*.
- If inference misses your schema, extend `CANDIDATE_*` lists or expose a simple SQL view.

**DO NOT ACTIVATE ANY GitHub Actions files.**

## Exit Status
{"Unresolved errors exist — inspect .codex/errors.ndjson" if unresolved else "No unresolved errors detected."}
"""
    ).strip() + "\n"
    write_text(results, summary)

    print(summary)
    return 1 if unresolved else 0


if __name__ == "__main__":
    sys.exit(main())
