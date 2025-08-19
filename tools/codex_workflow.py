#!/usr/bin/env python3
# ruff: noqa: E501
# File: tools/codex_workflow.py
# Usage: python tools/codex_workflow.py
# Purpose: Implement Phases 1-6 for the supplied task set (tests for fetch_messages).
import json
import re
import subprocess
import sys
import textwrap
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(
    subprocess.run(
        ["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True
    ).stdout.strip()
    or "."
).resolve()
CODEX_DIR = REPO_ROOT / ".codex"
TOOLS_DIR = REPO_ROOT / "tools"
TESTS_DIR = REPO_ROOT / "tests"
INVENTORY = CODEX_DIR / "inventory.tsv"
FLAGS = CODEX_DIR / "flags.env"
CHANGE_LOG = CODEX_DIR / "change_log.md"
ERRORS = CODEX_DIR / "errors.ndjson"
RESULTS = CODEX_DIR / "results.md"
MAPPING = CODEX_DIR / "mapping.json"
GUARDRAILS = CODEX_DIR / "guardrails.md"

STEP = 0
UNRESOLVED = False


def now():
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")


def ensure_dirs():
    TOOLS_DIR.mkdir(parents=True, exist_ok=True)
    CODEX_DIR.mkdir(parents=True, exist_ok=True)
    TESTS_DIR.mkdir(parents=True, exist_ok=True)


def append_change(text: str):
    CHANGE_LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(CHANGE_LOG, "a", encoding="utf-8") as f:
        f.write(f"\n### {now()} — {text}\n")


def log_error(step_num: str, step_desc: str, error_msg: str, context: str):
    global UNRESOLVED
    UNRESOLVED = True
    entry = {
        "ts": now(),
        "step": f"{step_num}: {step_desc}",
        "error": error_msg,
        "context": context,
        "question": textwrap.dedent(f"""\
            Question for ChatGPT-5:
            While performing [{step_num}: {step_desc}], encountered the following error:
            {error_msg}
            Context: {context}
            What are the possible causes, and how can this be resolved while preserving intended functionality?
        """),
    }
    with open(ERRORS, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")
    print("\n" + entry["question"] + "\n", file=sys.stderr)


def run(cmd, step_num, step_desc, cwd=None, check=True):
    try:
        res = subprocess.run(cmd, cwd=cwd or REPO_ROOT, capture_output=True, text=True)
        if check and res.returncode != 0:
            raise RuntimeError(
                res.stderr.strip() or res.stdout.strip() or "Unknown error"
            )
        return res
    except Exception as e:
        log_error(step_num, step_desc, str(e), context=f"cmd={' '.join(cmd)}")
        if check:
            raise


def read_text_if(p: Path):
    return p.read_text(encoding="utf-8") if p.exists() else ""


def write_file(p: Path, content: str, change_reason: str):
    p.parent.mkdir(parents=True, exist_ok=True)
    existed = p.exists()
    before = p.read_text(encoding="utf-8") if existed else ""
    with open(p, "w", encoding="utf-8") as f:
        f.write(content)
    after = content
    append_change(
        f"Write {p.relative_to(REPO_ROOT)} — {change_reason}\n- existed: {existed}\n- before (first 200 chars): {before[:200]!r}\n- after  (first 200 chars): {after[:200]!r}"
    )


def phase1_prep():
    global STEP
    STEP += 1
    step = f"1.{STEP}"
    # 1.1
    try:
        status = run(
            ["git", "status", "--porcelain"], step, "Snapshot working tree", check=False
        )
        append_change(f"Working state snapshot:\n```\n{status.stdout.strip()}\n```")
    except Exception as e:
        log_error(step, "Snapshot working tree", str(e), "git status")
    # 1.2
    readme = read_text_if(REPO_ROOT / "README.md") or read_text_if(
        REPO_ROOT / "README.MD"
    )
    contrib = read_text_if(REPO_ROOT / "CONTRIBUTING.md")
    content = f"# Guardrails & Conventions ({now()})\n\n## README.md\n\n{readme}\n\n## CONTRIBUTING.md\n\n{contrib}\n"
    write_file(GUARDRAILS, content, "Capture guardrails")
    # 1.3 inventory
    lines = []
    for p in REPO_ROOT.rglob("*"):
        if not p.is_file():
            continue
        rel = p.relative_to(REPO_ROOT).as_posix()
        if (
            rel.startswith(".git/")
            or rel.startswith(".codex/")
            or rel.startswith(".venv/")
            or rel.startswith("node_modules/")
        ):
            continue
        if rel.startswith(".github/workflows/"):
            continue
        ext = p.suffix.lower()
        guess = (
            "code"
            if ext in (".py", ".js", ".ts", ".sql", ".sh", ".bash", ".ps1")
            else "doc"
            if ext in (".md", ".rst", ".txt")
            else "asset"
        )
        lines.append(f"{rel}\t{ext or 'none'}\t{guess}")
    write_file(INVENTORY, "\n".join(lines), "Inventory snapshot")
    # 1.4 flags
    write_file(FLAGS, "DO_NOT_ACTIVATE_GITHUB_ACTIONS=true\n", "Set constraint flags")
    # 1.5 logs ensured by writes above


def phase2_search_map():
    # Discover candidates for fetch_messages + writers
    candidates = {"fetch_messages": [], "writers": [], "db_constants": []}
    py_files = [
        p
        for p in REPO_ROOT.rglob("*.py")
        if "tests/" not in p.as_posix()
        and ".venv/" not in p.as_posix()
        and ".git/" not in p.as_posix()
    ]
    pattern_fetch = re.compile(r"\bdef\s+fetch_messages\b|\bfetch_messages\b")
    pattern_writer = re.compile(
        r"\bdef\s+(log_message|record_event|append_message|add_message|log_event)\b"
    )
    pattern_db_const = re.compile(
        r"(DEFAULT_DB|DB_PATH|DEFAULT_DB_PATH|MESSAGES_DB)\s*=\s*([\"'])(.*?)\2"
    )
    for pf in py_files:
        try:
            txt = pf.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        if pattern_fetch.search(txt):
            candidates["fetch_messages"].append(pf.relative_to(REPO_ROOT).as_posix())
        if pattern_writer.search(txt):
            candidates["writers"].append(pf.relative_to(REPO_ROOT).as_posix())
        for m in pattern_db_const.finditer(txt):
            candidates["db_constants"].append(
                {
                    "file": pf.relative_to(REPO_ROOT).as_posix(),
                    "name": m.group(1),
                    "value": m.group(3),
                }
            )
    mapping = {
        "test_fetch_messages": {
            "candidate_assets": candidates["fetch_messages"],
            "writers": candidates["writers"],
            "db_constants": candidates["db_constants"],
            "rationale": "Symbolic presence from regex scan; to be validated by dynamic import at test time.",
        }
    }
    write_file(MAPPING, json.dumps(mapping, indent=2), "Write mapping table")


def phase3_construct():
    # Generate introspector and tests
    introspect_code = r"""
# Auto-generated by codex_workflow.py
import sys, pkgutil, importlib, inspect, os
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
# common sys.path adds
for add in [REPO_ROOT, REPO_ROOT / "src", REPO_ROOT / "app", REPO_ROOT / "lib"]:
    if add.exists() and add.as_posix() not in sys.path:
        sys.path.insert(0, add.as_posix())

WRITER_NAMES = ["log_message","record_event","append_message","add_message","log_event"]

def _iter_module_names():
    base_dirs = [REPO_ROOT, REPO_ROOT / "src", REPO_ROOT / "app", REPO_ROOT / "lib"]
    seen = set()
    for base in base_dirs:
        if not base.exists(): continue
        for p in base.rglob("*.py"):
            rel = p.relative_to(base).as_posix()
            if rel.startswith("tests/"): continue
            if rel.endswith("__init__.py"):
                mod = rel[:-12].replace("/", ".")
            else:
                mod = rel[:-3].replace("/", ".")
            if not mod or any(seg.startswith(".") for seg in mod.split(".")):
                continue
            if mod not in seen:
                seen.add(mod)
                yield mod

def resolve_fetch_messages():
    errors = {}
    for mod in _iter_module_names():
        try:
            m = importlib.import_module(mod)
        except Exception as e:
            errors[mod] = f"import error: {e}"
            continue
        if hasattr(m, "fetch_messages"):
            fn = getattr(m, "fetch_messages")
            try:
                sig = inspect.signature(fn)
            except Exception:
                sig = None
            meta = {
                "module": mod,
                "callable": fn,
                "accepts_db_path": ("db" in (sig.parameters if sig else {}) or
                                    "db_path" in (sig.parameters if sig else {}) or
                                    (sig and any("path" in n for n in sig.parameters))),
                "signature": str(sig) if sig else "unknown",
                "module_obj": m
            }
            return meta
    return {"error": "fetch_messages not found", "errors": errors}

def resolve_writer():
    errors = {}
    for mod in _iter_module_names():
        try:
            m = importlib.import_module(mod)
        except Exception as e:
            errors[mod] = f"import error: {e}"
            continue
        for name in WRITER_NAMES:
            if hasattr(m, name):
                fn = getattr(m, name)
                try:
                    sig = inspect.signature(fn)
                except Exception:
                    sig = None
                return {
                    "module": mod,
                    "name": name,
                    "callable": fn,
                    "signature": str(sig) if sig else "unknown",
                    "accepts_db_path": (sig and any(k in sig.parameters for k in ["db","db_path","path","database"]))
                }
    return {"error": "no writer found", "errors": errors}

def patch_default_db_path(module_obj, tmp_db_path):
    # Try to overwrite common constants if present
    patched = []
    for attr in ["DEFAULT_DB","DB_PATH","DEFAULT_DB_PATH","MESSAGES_DB","DEFAULT_LOG_DB"]:
        if hasattr(module_obj, attr):
            try:
                setattr(module_obj, attr, str(tmp_db_path))
                patched.append(attr)
            except Exception:
                pass
    return patched
"""
    test_code = r'''
"""Tests for fetch_messages covering custom and default DB paths."""

import inspect
import os
import sqlite3
from pathlib import Path

import pytest

from tests._codex_introspect import (
    patch_default_db_path,
    resolve_fetch_messages,
    resolve_writer,
)

EVENTS = [
    {"level": "INFO", "content": "alpha", "ts": 1},
    {"level": "WARN", "content": "bravo", "ts": 2},
    {"level": "INFO", "content": "charlie", "ts": 3},
]


def _make_sqlite_db(db_path: Path, session_id: str = "SID") -> None:
    """Create a minimal session_events table populated with EVENTS."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS session_events(
            ts REAL NOT NULL,
            session_id TEXT NOT NULL,
            role TEXT NOT NULL,
            message TEXT NOT NULL
        )
        """
    )
    cur.executemany(
        "INSERT INTO session_events(ts, session_id, role, message) VALUES (?,?,?,?)",
        [(e["ts"], session_id, e["level"], e["content"]) for e in EVENTS],
    )
    conn.commit()
    conn.close()


def _populate_with_writer(writer_meta, db_path: Path | None) -> None:
    """Populate events using a discovered writer function."""
    w = writer_meta["callable"]
    accepts_path = writer_meta.get("accepts_db_path", False)
    params = inspect.signature(w).parameters
    for e in EVENTS:
        kwargs = {}
        if "session_id" in params:
            kwargs["session_id"] = "SID"
        if "sid" in params and "session_id" not in params:
            kwargs["sid"] = "SID"
        if "level" in params:
            kwargs["level"] = e["level"]
        elif "role" in params:
            kwargs["role"] = e["level"]
        if "message" in params:
            kwargs["message"] = e["content"]
        elif "text" in params:
            kwargs["text"] = e["content"]
        if accepts_path and db_path is not None:
            if "db" in params:
                kwargs["db"] = str(db_path)
            else:
                kwargs["db_path"] = str(db_path)
        w(**kwargs)


def _call_fetch(meta, db_path: Path | None, session_id: str = "SID"):
    """Invoke fetch_messages with flexible db_path handling."""
    fn = meta["callable"]
    if db_path is not None and meta.get("accepts_db_path"):
        return list(fn(session_id, db_path=str(db_path)))
    # try kwargs variations
    try:
        return list(fn(session_id, db=str(db_path))) if db_path is not None else list(fn(session_id))
    except TypeError:
        try:
            return list(fn(session_id, path=str(db_path))) if db_path is not None else list(fn(session_id))
        except TypeError:
            return list(fn(session_id))


def _assert_order_and_content(rows):
    """Validate retrieval order and message content."""
    def to_tuple(r):
        if isinstance(r, dict):
            return (str(r.get("role", "")), str(r.get("message", "")))
        if isinstance(r, (tuple, list)):
            if len(r) >= 4:
                return (str(r[2]), str(r[3]))
            if len(r) >= 3:
                return (str(r[1]), str(r[2]))
        return ("", "")

    got = [to_tuple(r) for r in rows]
    expected = [(e["level"], e["content"]) for e in EVENTS]
    assert got == expected, f"Expected {expected}, got {got}"


@pytest.mark.parametrize("mode", ["custom_path", "default_path"])
def test_fetch_messages(tmp_path, mode, monkeypatch):
    meta = resolve_fetch_messages()
    if "error" in meta:
        pytest.skip("fetch_messages not found in repository — best-effort skip")

    # Set up paths
    custom_db = tmp_path / "messages.db"

    # Try to find a writer
    writer = resolve_writer()  # may be error

    if mode == "custom_path":
        # Prefer to keep all IO under tmp_path
        if isinstance(writer, dict) and "callable" in writer:
            _populate_with_writer(writer, custom_db)
        else:
            # no writer; create SQLite DB as a fallback
            _make_sqlite_db(custom_db)
        rows = _call_fetch(meta, custom_db)
        _assert_order_and_content(rows)
        # cleanup: tmp_path is auto-removed by pytest

    elif mode == "default_path":
        # Try to patch default path constants in module to tmp_path db
        patched = patch_default_db_path(meta["module_obj"], custom_db)
        if not patched and not meta.get("accepts_db_path"):
            pytest.skip("No default DB constant to patch and fetch_messages has no db_path parameter")
        if isinstance(writer, dict) and "callable" in writer:
            _populate_with_writer(writer, custom_db if patched else None)
        else:
            # no writer; create SQLite when patched, otherwise we cannot enforce default target
            if patched:
                _make_sqlite_db(custom_db)
            else:
                pytest.skip("Cannot safely generate default-path data without writer or patchable constant")
        rows = _call_fetch(meta, None if patched else custom_db)
        _assert_order_and_content(rows)
        # cleanup via tmp_path
'''
    write_file(
        TESTS_DIR / "_codex_introspect.py", introspect_code, "Add introspection helpers"
    )
    write_file(
        TESTS_DIR / "test_fetch_messages.py",
        test_code,
        "Add tests for fetch_messages (default & custom)",
    )


def phase3_run_pytest():
    # Execute pytest and capture output for change log
    try:
        res = run([sys.executable, "-m", "pytest", "-q"], "3.6", "Run pytest")
        append_change(
            f"Pytest output:\n```\n{res.stdout.strip()}\n```\nErrors:\n```\n{res.stderr.strip()}\n```"
        )
    except Exception as e:
        append_change(f"Pytest failed; see errors.ndjson. {e}")


def phase4_prune_if_needed():
    # For this task, pruning is only recorded if fetch_messages not found
    try:
        mapj = json.loads(MAPPING.read_text(encoding="utf-8"))
        cands = mapj.get("test_fetch_messages", {}).get("candidate_assets", [])
        if not cands:
            append_change(
                textwrap.dedent("""\
                Pruning:
                - Purpose: test cannot bind to fetch_messages (symbol absent)
                - Alternatives: introspection, writer detection, SQLite fallback
                - Failure: no symbol discovered; tests marked skip (best-effort)
                - Decision: no repo code pruned; recorded as limitation
            """)
            )
    except Exception as e:
        log_error("4.x", "Record pruning rationale", str(e), "mapping.json parse")


def phase5_finalize():
    # Results summary
    results = {
        "ts": now(),
        "implemented": [
            "tests/_codex_introspect.py",
            "tests/test_fetch_messages.py",
            ".codex/inventory.tsv",
            ".codex/mapping.json",
            ".codex/guardrails.md",
            ".codex/change_log.md",
        ],
        "notes": [
            "Tests attempt both custom and default DB paths.",
            "Default path is redirected via monkeypatched constants when available.",
            "Writer functions are used if discovered; otherwise SQLite fallback is used.",
            "Temporary files are contained under pytest tmp_path and auto-cleaned.",
        ],
        "errors_present": UNRESOLVED,
        "do_not_activate_github_actions": True,
    }
    write_file(
        RESULTS,
        json.dumps(results, indent=2)
        + "\n\n**DO NOT ACTIVATE ANY GitHub Actions files.**\n",
        "Results summary",
    )


def main():
    ensure_dirs()
    try:
        phase1_prep()
        phase2_search_map()
        phase3_construct()
        phase3_run_pytest()
        phase4_prune_if_needed()
        phase5_finalize()
    except Exception:
        # already logged; ensure non-zero
        pass
    if UNRESOLVED:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
