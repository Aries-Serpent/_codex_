from __future__ import annotations

import sqlite3
from pathlib import Path

from codex_ml.logging.session_logger import SessionLogger


def test_session_logger_persists_epoch_metrics(tmp_path: Path) -> None:
    log_dir = tmp_path / "logs"
    db_path = tmp_path / "metrics.db"
    logger = SessionLogger(
        "session-test",
        log_dir,
        enable_sqlite_metrics=True,
        sqlite_db_path=db_path,
    )

    logger.log_event(
        "epoch",
        {"epoch": 1, "metrics": {"loss": 0.42, "accuracy": 0.75, "note": "skip"}},
    )

    conn = sqlite3.connect(db_path)
    try:
        rows = conn.execute(
            "SELECT metric, value FROM metric_records WHERE session_id=? ORDER BY metric",
            ("session-test",),
        ).fetchall()
    finally:
        conn.close()

    assert rows == [("accuracy", 0.75), ("loss", 0.42)]
