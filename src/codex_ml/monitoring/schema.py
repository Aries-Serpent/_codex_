from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Dict, Optional

LOG_VERSION = 1
_SECRET_RE = re.compile(r"(api[-_]?key|token|secret)", re.I)


@dataclass
class LogRecord:
    """Strict schema for metric log records."""

    ts: float
    run_id: str
    phase: str
    step: int
    metric: str
    value: float
    split: str = "train"
    dataset: Optional[str] = None
    meta: Dict[str, Any] = field(default_factory=dict)

    def redacted(self) -> "LogRecord":
        """Return a copy with secrets redacted and string sizes capped."""

        new_meta: Dict[str, Any] = {}
        for k, v in self.meta.items():
            if isinstance(v, str) and _SECRET_RE.search(v):
                new_meta[k] = "<redacted>"
            elif isinstance(v, str) and len(v) > 4096:
                new_meta[k] = v[:4096]
            else:
                new_meta[k] = v
        return LogRecord(
            self.ts,
            self.run_id,
            self.phase,
            self.step,
            self.metric,
            self.value,
            self.split,
            self.dataset,
            new_meta,
        )

    def dict(self) -> Dict[str, Any]:
        """Convert the record to a dictionary with explicit column order."""

        return {
            "version": LOG_VERSION,
            "ts": self.ts,
            "run_id": self.run_id,
            "phase": self.phase,
            "step": self.step,
            "split": self.split,
            "dataset": self.dataset or "",
            "metric": self.metric,
            "value": self.value,
            "meta": self.meta,
        }
