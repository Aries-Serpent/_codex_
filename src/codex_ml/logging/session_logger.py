"""Session-scoped structured logging utilities."""

from __future__ import annotations

import json
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from codex_ml.safety.redaction import SecretRedactor

try:  # pragma: no cover - codex logging module may be unavailable in slim envs
    from codex.logging.db_manager import DBManager
except Exception:  # pragma: no cover
    DBManager = None  # type: ignore[assignment]

DEFAULT_LOG_DIR = Path(".codex") / "logs"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


class SessionLogger:
    """Structured NDJSON logger that annotates records with a session id."""

    def __init__(
        self,
        session_id: str | None = None,
        log_dir: Path | None = None,
        *,
        redactor: SecretRedactor | None = None,
        metrics_db_path: Path | None = None,
        mirror_metrics: bool = True,
    ) -> None:
        self.session_id = session_id or str(uuid.uuid4())
        self.log_dir = (log_dir or DEFAULT_LOG_DIR).expanduser()
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.session_file = self.log_dir / f"session_{self.session_id}.jsonl"
        self._redactor = redactor or SecretRedactor()
        self._metrics_db: DBManager | None = None
        if mirror_metrics and DBManager is not None:
            try:
                self._metrics_db = DBManager(metrics_db_path)
                self._metrics_db.init_schema()
            except Exception:  # pragma: no cover - SQLite optional
                self._metrics_db = None

    def log_event(
        self,
        event_type: str,
        data: Mapping[str, Any] | None = None,
        *,
        role: str = "system",
    ) -> Path:
        payload: dict[str, Any] = {
            "timestamp": _utc_now(),
            "session_id": self.session_id,
            "role": role,
            "event_type": event_type,
        }
        if data:
            payload["data"] = self._redactor.redact_dict(dict(data))
        with self.session_file.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, ensure_ascii=False) + "\n")
        self._mirror_metric_payload(event_type, data)
        return self.session_file

    def _mirror_metric_payload(
        self, event_type: str, data: Mapping[str, Any] | None
    ) -> None:
        if not data or self._metrics_db is None:
            return
        metrics = data.get("metrics")
        if not isinstance(metrics, Mapping):
            return
        epoch_value = data.get("epoch")
        try:
            epoch_int = int(epoch_value) if epoch_value is not None else None
        except (TypeError, ValueError):  # pragma: no cover - metadata mismatch
            epoch_int = None
        timestamp = time.time()
        rows: list[tuple[float, str, str, int | None, str, float]] = []
        for key, value in metrics.items():
            if isinstance(value, (int, float)):
                rows.append(
                    (
                        timestamp,
                        self.session_id,
                        event_type,
                        epoch_int,
                        str(key),
                        float(value),
                    )
                )
        if not rows:
            return
        try:
            with self._metrics_db.connection() as conn:
                conn.executemany(
                    "INSERT INTO metric_records (ts, session_id, event_type, epoch, metric, value) "
                    "VALUES (?, ?, ?, ?, ?, ?)",
                    rows,
                )
                conn.commit()
        except Exception:  # pragma: no cover - metrics mirroring is best effort
            return


__all__ = ["SessionLogger", "DEFAULT_LOG_DIR"]
