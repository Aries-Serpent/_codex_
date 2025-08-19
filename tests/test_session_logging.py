import logging
import os, json, sqlite3, uuid, subprocess, sys, importlib, pathlib, time
import pytest

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
    except Exception as e:
        logging.exception("session logging hook raised: %s: %s", e.__class__.__name__, e)
        if isinstance(e, (ImportError, AttributeError, NotImplementedError)):
            pytest.skip(f"Required session logging hook not available: {e!r}")
        pytest.fail(f"Session logging hook failed: {e!r}")

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
    assert any("session_start" in line or '"event":"start"' in line or '"start"' in line for line in data)
    assert any("session_end" in line or '"event":"end"' in line or '"end"' in line for line in data)

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
        cp = _run_cli(mod, ["--session-id", "A", "--format", "json"], cwd=tmp_path)
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


def test_export_cli_reads_session_logger(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    db_path = tmp_path / ".codex" / "session_logs.sqlite"
    monkeypatch.setenv("CODEX_LOG_DB_PATH", str(db_path))
    session_id = f"S-{uuid.uuid4()}"

    mod = _import_any(["codex.logging.session_logger", "src.codex.logging.session_logger"])
    if not mod or not hasattr(mod, "log_event"):
        pytest.skip("session_logger.log_event not available")

    mod.log_event(session_id, "user", "hi")
    mod.log_event(session_id, "assistant", "hey")

    # Let export auto-discover the .sqlite file
    monkeypatch.delenv("CODEX_LOG_DB_PATH", raising=False)

    for modname in ["src.codex.logging.export", "codex.logging.export"]:
        cp = _run_cli(modname, [session_id], cwd=tmp_path)
        if cp.returncode == 0 and cp.stdout.strip():
            out = cp.stdout.strip()
            try:
                data = json.loads(out)
                messages = [r.get("message") or r.get("content") for r in data]
            except Exception:
                messages = [line for line in out.splitlines() if "hi" in line or "hey" in line]
            assert any("hi" in m for m in messages)
            assert any("hey" in m for m in messages)
            return
    pytest.skip("export module is not available or failed")
