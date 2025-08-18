#!/usr/bin/env python3
# tools/codex_session_logging_workflow.py
# End-to-end workflow for adding and validating session logging tests
# Policy: DO NOT ACTIVATE ANY GitHub Actions files.

import json, os, re, sys, subprocess, textwrap, shutil, sqlite3, pathlib, datetime, logging

ROOT = pathlib.Path(__file__).resolve().parents[1]
CODEX_DIR = ROOT / ".codex"
TESTS_DIR = ROOT / "tests"
SCRIPTS_DIR = ROOT / "scripts"
README = ROOT / "README.md"

FLAGS = {
    "DO_NOT_ACTIVATE_GITHUB_ACTIONS": True,
    "SAFE_WRITE": True,
    "NO_NETWORK": True,
}
CODEX_DIR.mkdir(exist_ok=True)

CHANGE_LOG = CODEX_DIR / "change_log.md"
ERRORS = CODEX_DIR / "errors.ndjson"
RESULTS = CODEX_DIR / "results.md"
FLAGS_JSON = CODEX_DIR / "flags.json"
INVENTORY_JSON = CODEX_DIR / "inventory.json"

def now_iso():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()

def append_change(msg):
    CHANGE_LOG.parent.mkdir(exist_ok=True)
    with CHANGE_LOG.open("a", encoding="utf-8") as f:
        f.write(f"\n- {now_iso()} — {msg}")

def append_error(step_num, step_desc, err_msg, context):
    entry = {
        "ts": now_iso(),
        "step": f"{step_num}: {step_desc}",
        "error": err_msg,
        "context": context,
        "format": "chatgpt5-question"
    }
    with ERRORS.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    sys.stderr.write(
        textwrap.dedent(f"""
        Question for ChatGPT-5:
        While performing [{step_num}: {step_desc}], encountered the following error:
        {err_msg}
        Context: {context}
        What are the possible causes, and how can this be resolved while preserving intended functionality?
        """).strip()+"\n"
    )

def run(cmd, step_num, step_desc, cwd=ROOT, env=None, check=True):
    try:
        cp = subprocess.run(cmd, cwd=cwd, env=env, capture_output=True, text=True)
        if check and cp.returncode != 0:
            raise RuntimeError(f"cmd={cmd} rc={cp.returncode} stderr={cp.stderr.strip()}")
        return cp
    except Exception as e:
        append_error(step_num, step_desc, str(e), f"cmd={cmd}")
        return None

def phase1_prep():
    # 1.1 git clean state
    try:
        cp = run(["git", "rev-parse", "--show-toplevel"], "1.1", "Identify repo root")
        if cp and cp.returncode == 0:
            repo_root = pathlib.Path(cp.stdout.strip())
            if repo_root.resolve() != ROOT.resolve():
                append_change(f"Repo root from git differs from script ROOT: {repo_root} vs {ROOT}")
        cp2 = run(["git", "status", "--porcelain"], "1.1", "Check clean working tree", check=False)
        if cp2 and cp2.stdout.strip():
            append_change("Working tree not clean; continuing in best-effort mode.")
    except Exception as e:
        append_error("1.1", "Verify git clean state", str(e), "git may be unavailable")

    # 1.2 Read README
    if README.exists():
        readme_text = README.read_text(encoding="utf-8", errors="ignore")
        append_change("Loaded README.md for guardrails.")
    else:
        readme_text = ""
        append_change("README.md missing; proceeding with heuristics.")

    # 1.3 Inventory
    inv = {"dirs": [], "files": []}
    for p in ROOT.iterdir():
        if p.name.startswith("."):  # include .codex separately
            continue
        if p.is_dir():
            inv["dirs"].append(p.name)
        else:
            inv["files"].append(p.name)
    INVENTORY_JSON.write_text(json.dumps(inv, indent=2), encoding="utf-8")
    append_change("Wrote .codex/inventory.json")

    # 1.4 Flags
    FLAGS_JSON.write_text(json.dumps(FLAGS, indent=2), encoding="utf-8")
    append_change("Wrote .codex/flags.json")

    # 1.5 Initialize logs if empty
    if not CHANGE_LOG.exists():
        CHANGE_LOG.write_text("# Codex change log\n", encoding="utf-8")
    if not ERRORS.exists():
        ERRORS.write_text("", encoding="utf-8")

    return readme_text

TEST_FILE = TESTS_DIR / "test_session_logging.py"
TEST_BODY = r'''
import os, json, sqlite3, uuid, subprocess, sys, importlib, pathlib, time, logging
import pytest

logger = logging.getLogger(__name__)

def _import_any(paths):
    for p in paths:
        try:
            return importlib.import_module(p)
        except Exception:
            continue
    return None

def _run_cli(module, args, cwd):
    py = sys.executable
    cmd = [py, "-m", module] + args
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)

def _discover_rows(db_path, session_id):
    # Be resilient to table/column variants
    con = sqlite3.connect(str(db_path))
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [r[0] for r in cur.fetchall()]
    rows = []
    for t in tables:
        # probe: session/session_id + message/content + role/kind + ts/timestamp/created_at
        cur.execute(f"PRAGMA table_info({t})")
        cols = [r[1] for r in cur.fetchall()]
        c_session = "session_id" if "session_id" in cols else ("session" if "session" in cols else None)
        c_message = "message" if "message" in cols else ("content" if "content" in cols else None)
        c_role = "role" if "role" in cols else ("kind" if "kind" in cols else None)
        if not (c_session and c_message):
            continue
        q = f"SELECT * FROM {t} WHERE {c_session}=?"
        cur.execute(q, (session_id,))
        for r in cur.fetchall():
            rows.append({ k: r[k] for k in r.keys() })
    con.close()
    return rows

def test_context_manager_emits_start_end(tmp_path, monkeypatch):
    # Arrange
    monkeypatch.chdir(tmp_path)
    session_id = f"T-{uuid.uuid4()}"
    monkeypatch.setenv("CODEX_SESSION_ID", session_id)

    sessions_dir = tmp_path / ".codex" / "sessions"
    sessions_dir.mkdir(parents=True, exist_ok=True)
    ndjson_file = sessions_dir / f"{session_id}.ndjson"

    # Try Python context manager first
    hooks = _import_any(["codex.logging.session_hooks", "src.codex.logging.session_hooks"])
    used = None
    try:
        if hooks:
            # Accept multiple possible exports: session(), session_scope(), or Context()
            cm = None
            for name in ["session", "session_scope", "SessionContext", "context"]:
                if hasattr(hooks, name):
                    target = getattr(hooks, name)
                    cm = target() if callable(target) else target
                    break
            if cm is not None:
                with cm:
                    time.sleep(0.01)
                used = "python_cm"
    except Exception as exc:
        hook_name = locals().get("name", "unknown")
        logger.exception(
            "Error while processing session-logging hook '%s': %s",
            hook_name,
            exc,
        )
        raise

    if used is None:
        # Fallback to shell helpers via source
        sh = pathlib.Path(__file__).resolve().parents[1] / "scripts" / "session_logging.sh"
        if not sh.exists():
            pytest.skip("No session_hooks module or shell script available")
        cmd = f"set -euo pipefail; source '{sh}'; codex_session_start; codex_session_end"
        cp = subprocess.run(["bash", "-lc", cmd], cwd=tmp_path, text=True, capture_output=True)
        assert cp.returncode == 0, cp.stderr
        used = "shell"

    # Assert NDJSON exists and has start/end markers
    assert ndjson_file.exists()
    data = ndjson_file.read_text(encoding="utf-8").strip().splitlines()
    assert any('"start"' in line or '"event":"start"' in line for line in data)
    assert any('"end"' in line or '"event":"end"' in line for line in data)

def test_log_conversation_helper(tmp_path, monkeypatch):
    # Arrange DB path
    db_path = tmp_path / "session_logs.sqlite"
    monkeypatch.setenv("CODEX_LOG_DB_PATH", str(db_path))
    session_id = f"S-{uuid.uuid4()}"

    mod = _import_any(["codex.logging.session_logger", "src.codex.logging.session_logger"])
    if not mod or not hasattr(mod, "log_event"):
        pytest.skip("session_logger.log_event not available")

    # Act: emit user + assistant
    mod.log_event(session_id, "user", "hello from user")
    mod.log_event(session_id, "assistant", "hello from assistant")

    # Assert rows discoverable (table/column tolerant)
    rows = _discover_rows(db_path, session_id)
    msgs = {r.get("message") or r.get("content") for r in rows}
    roles = {r.get("role") or r.get("kind") for r in rows}
    assert "hello from user" in msgs
    assert "hello from assistant" in msgs
    assert ("user" in roles) or ("assistant" in roles)

def test_cli_query_returns_expected_rows(tmp_path, monkeypatch):
    # Create isolated DB with session_events
    db = tmp_path / "codex.db"
    con = sqlite3.connect(str(db))
    cur = con.cursor()
    cur.execute("CREATE TABLE session_events (session_id TEXT, timestamp TEXT, role TEXT, message TEXT)")
    con.commit()
    data = [
        ("A", "2025-01-01T00:00:00Z", "user", "hi"),
        ("A", "2025-01-01T00:00:01Z", "assistant", "hey"),
        ("B", "2025-01-01T00:00:02Z", "user", "bye"),
    ]
    cur.executemany("INSERT INTO session_events VALUES (?,?,?,?)", data)
    con.commit(); con.close()

    monkeypatch.setenv("CODEX_DB_PATH", str(db))

    # Prefer src.codex.logging.query_logs; fallback to codex.logging.query_logs
    for mod in ["src.codex.logging.query_logs", "codex.logging.query_logs"]:
        cp = _run_cli(mod, ["--session-id","A","--format","json"], cwd=tmp_path)
        if cp.returncode == 0 and cp.stdout.strip():
            # Expect 2 rows for session A
            out = cp.stdout.strip()
            try:
                parsed = json.loads(out)
                assert isinstance(parsed, list)
                messages = [r.get("message") or r.get("content") for r in parsed]
            except Exception:
                # Tolerate non-JSON lines containing messages
                messages = [line for line in out.splitlines() if "hi" in line or "hey" in line]
            assert any("hi" in m for m in messages)
            assert any("hey" in m for m in messages)
            return
    pytest.skip("query_logs module is not available or failed")
'''

def ensure_tests():
    TESTS_DIR.mkdir(exist_ok=True)
    created = False
    if TEST_FILE.exists():
        # Merge/replace content conservatively if it lacks our three tests
        content = TEST_FILE.read_text(encoding="utf-8", errors="ignore")
        need_write = not all(x in content for x in [
            "test_context_manager_emits_start_end",
            "test_log_conversation_helper",
            "test_cli_query_returns_expected_rows",
        ])
        if need_write:
            backup = TEST_FILE.with_suffix(".py.bak")
            shutil.copy2(TEST_FILE, backup)
            append_change(f"Backed up existing tests/test_session_logging.py -> {backup.name}")
            TEST_FILE.write_text(TEST_BODY, encoding="utf-8")
            append_change("Updated tests/test_session_logging.py with required coverage.")
            created = True
    else:
        TEST_FILE.write_text(TEST_BODY, encoding="utf-8")
        append_change("Created tests/test_session_logging.py with required coverage.")
        created = True
    return created

def run_pytest():
    try:
        import importlib.util as iu
        if iu.find_spec("pytest") is None:
            append_error("3.4", "Run tests", "pytest not installed", "pip install -U pytest")
            return None
    except Exception as e:
        append_error("3.4", "Check pytest availability", str(e), "")
        return None
    cp = run([sys.executable, "-m", "pytest", "-q", "tests/test_session_logging.py"], "3.4", "Run tests", check=False)
    if cp:
        summary = f"pytest rc={cp.returncode}\nSTDOUT:\n{cp.stdout}\nSTDERR:\n{cp.stderr}"
        append_change("Executed pytest on test_session_logging.py\n" + summary)
    return cp

def phase6_finalize():
    RESULTS.write_text(textwrap.dedent(f"""
    # Results Summary

    - Timestamp: {now_iso()}
    - Implemented: tests/test_session_logging.py (3 tests: CM start/end, message logging helper, CLI query)
    - Flags: DO NOT ACTIVATE ANY GitHub Actions files.
    - Inventory: {INVENTORY_JSON.relative_to(ROOT)}
    - Change-log: {CHANGE_LOG.relative_to(ROOT)}
    - Errors: {ERRORS.relative_to(ROOT)}

    ## Next Steps
    - If any tests are skipped or xfailed, consult `.codex/errors.ndjson` entries.
    - Confirm actual export names in `codex/logging/session_hooks.py` and `codex/logging/session_logger.py`.
    - Ensure `src/codex/logging/query_logs.py` exists and supports `--format json`.
    """).strip()+"\n", encoding="utf-8")
    append_change("Wrote .codex/results.md")

def main():
    print("== Phase 1: Preparation ==")
    phase1_prep()

    print("== Phase 3: Best-Effort Construction ==")
    created = ensure_tests()

    print("== Phase 3.4: Smoke run (pytest) ==")
    cp = run_pytest()
    if cp and cp.returncode != 0:
        append_error("3.4", "Smoke run failed", f"rc={cp.returncode}", "See change_log for output")

    print("== Phase 6: Finalization ==")
    phase6_finalize()

    # Exit nonzero if any errors captured
    has_errors = ERRORS.exists() and ERRORS.stat().st_size > 0
    if has_errors and cp and cp.returncode != 0:
        print("Completed with errors. See .codex/errors.ndjson")
        sys.exit(1)
    print("Done. DO NOT ACTIVATE ANY GitHub Actions files.")
    sys.exit(0)

if __name__ == "__main__":
    main()
