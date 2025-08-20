import json
import os
import shutil
import sqlite3
import subprocess
import sys
from pathlib import Path


def _write_ndjson(path: Path, events: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for obj in events:
            f.write(json.dumps(obj) + "\n")


def _run_cli(cmd: list[str], log_dir: Path) -> subprocess.CompletedProcess:
    env = os.environ.copy()
    src_dir = Path(__file__).resolve().parents[1] / "src"
    env["PYTHONPATH"] = os.pathsep.join([str(src_dir), env.get("PYTHONPATH", "")])
    env["CODEX_SESSION_LOG_DIR"] = str(log_dir)
    return subprocess.run(cmd, capture_output=True, text=True, env=env)


def test_import_ndjson_cli_idempotent(tmp_path: Path):
    session_id = "S-cli"
    log_dir = tmp_path / "logs"
    ndjson_file = log_dir / f"{session_id}.ndjson"
    events = [
        {"ts": "2024-01-01T00:00:00Z", "role": "user", "message": "hi"},
        {"ts": "2024-01-01T00:00:01Z", "role": "assistant", "message": "yo"},
    ]
    _write_ndjson(ndjson_file, events)
    db_path = tmp_path / "events.db"

    cmd_base = ["codex-import-ndjson"]
    if shutil.which("codex-import-ndjson") is None:
        cmd_base = [sys.executable, "-m", "codex.logging.import_ndjson"]
    cmd = cmd_base + ["--session", session_id, "--db", str(db_path)]

    proc = _run_cli(cmd, log_dir)
    assert proc.returncode == 0, proc.stderr
    with sqlite3.connect(db_path) as con:
        count = con.execute(
            "SELECT COUNT(*) FROM session_events WHERE session_id=?",
            (session_id,),
        ).fetchone()[0]
    assert count == len(events)

    proc2 = _run_cli(cmd, log_dir)
    assert proc2.returncode == 0, proc2.stderr
    with sqlite3.connect(db_path) as con:
        count2 = con.execute(
            "SELECT COUNT(*) FROM session_events WHERE session_id=?",
            (session_id,),
        ).fetchone()[0]
    assert count2 == len(events)
