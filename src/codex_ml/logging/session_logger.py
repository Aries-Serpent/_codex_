"""Session-scoped structured logging utilities."""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from codex_ml.safety.redaction import SecretRedactor

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
    ) -> None:
        self.session_id = session_id or str(uuid.uuid4())
        self.log_dir = (log_dir or DEFAULT_LOG_DIR).expanduser()
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.session_file = self.log_dir / f"session_{self.session_id}.jsonl"
        self._redactor = redactor or SecretRedactor()

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
        return self.session_file


__all__ = ["SessionLogger", "DEFAULT_LOG_DIR"]
