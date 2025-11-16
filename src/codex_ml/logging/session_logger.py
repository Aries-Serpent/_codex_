"""Session-scoped structured logging utilities."""

from __future__ import annotations

import json
import logging
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from codex_ml.safety.redaction import SecretRedactor

try:  # pragma: no cover - optional logging backend
    from codex.logging.db_manager import DBManager
except (ImportError, ModuleNotFoundError):  # pragma: no cover - fallback if logging package unavailable
    DBManager = None

_LOGGER = logging.getLogger(__name__)

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
        sqlite_db_path: Path | None = None,
        enable_sqlite_metrics: bool | None = None,
        # Backward compatibility aliases
        metrics_db_path: Path | None = None,
        mirror_metrics: bool | None = None,
    ) -> None:
        # Handle backward-compatible parameter names
        if metrics_db_path is not None:
            if sqlite_db_path is not None and sqlite_db_path != metrics_db_path:
                _LOGGER.warning(
                    "Both 'sqlite_db_path' (%s) and legacy 'metrics_db_path' (%s) are provided and differ. "
                    "Using 'metrics_db_path' for backward compatibility.",
                    sqlite_db_path, metrics_db_path
                )
            sqlite_db_path = metrics_db_path
        if mirror_metrics is not None:
            if enable_sqlite_metrics is not None and enable_sqlite_metrics != mirror_metrics:
                _LOGGER.warning(
                    "Both 'enable_sqlite_metrics' (%s) and legacy 'mirror_metrics' (%s) are provided and differ. "
                    "Using 'mirror_metrics' for backward compatibility.",
                    enable_sqlite_metrics, mirror_metrics
                )
            enable_sqlite_metrics = mirror_metrics
        self.session_id = session_id or str(uuid.uuid4())
        self.log_dir = (log_dir or DEFAULT_LOG_DIR).expanduser()
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.session_file = self.log_dir / f"session_{self.session_id}.jsonl"
        self._redactor = redactor or SecretRedactor()
        self._db_manager: DBManager | None = None
        self._enable_sqlite_metrics = self._should_persist_metrics(enable_sqlite_metrics)
        if self._enable_sqlite_metrics and DBManager is not None:
            try:
                self._db_manager = DBManager(sqlite_db_path)
            except Exception as exc:  # pragma: no cover - optional backend failure
                _LOGGER.debug("SQLite metric logging unavailable: %s", exc)
                self._enable_sqlite_metrics = False

    def _should_persist_metrics(self, flag: bool | None) -> bool:
        if DBManager is None:
            return False
        if flag is not None:
            return bool(flag)
        env_value = os.getenv("CODEX_LOG_SQLITE_METRICS", "0").strip().lower()
        return env_value not in {"0", "false", "off"}

    def _maybe_store_metrics(self, event_type: str, data: Mapping[str, Any] | None) -> None:
        """Store epoch metrics to SQLite (synchronous operation).
        
        Note: This method performs synchronous SQLite writes during log_event calls.
        While the context manager pattern is used, executemany and commit operations
        may introduce latency in high-frequency logging scenarios or with slow disk I/O.
        The impact is typically minimal for epoch-level metrics (infrequent writes),
        but could be noticeable in tight training loops with many metrics.
        
        To disable this feature, set CODEX_LOG_SQLITE_METRICS=0 or pass
        enable_sqlite_metrics=False during SessionLogger initialization.
        """
        if not self._enable_sqlite_metrics or self._db_manager is None:
            return
        if event_type != "epoch" or not data:
            return
        metrics = data.get("metrics")
        if not isinstance(metrics, Mapping):
            return
        epoch_value = data.get("epoch")
        try:
            epoch_idx = int(epoch_value)
        except (TypeError, ValueError):
            return
        timestamp = datetime.now(timezone.utc).timestamp()
        rows: list[tuple[float, str, str, int, str, float]] = []
        for key, value in metrics.items():
            if isinstance(value, (int, float)):
                rows.append((timestamp, self.session_id, event_type, epoch_idx, str(key), float(value)))
        if not rows:
            return
        try:
            with self._db_manager.connection() as conn:
                conn.executemany(
                    "INSERT INTO metric_records (ts, session_id, event_type, epoch, metric, value) VALUES (?, ?, ?, ?, ?, ?)",
                    rows,
                )
                conn.commit()
        except Exception as exc:  # pragma: no cover - avoid failing training loops
            _LOGGER.debug("Skipping metric persistence: %s", exc)

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
        self._maybe_store_metrics(event_type, data)
        return self.session_file


__all__ = ["SessionLogger", "DEFAULT_LOG_DIR"]
