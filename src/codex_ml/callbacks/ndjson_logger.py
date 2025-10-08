"""Callback that writes metrics to an NDJSON file per epoch."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional

from .base import Callback


class NDJSONLogger(Callback):
    """Append epoch metrics to an NDJSON log."""

    def __init__(self, out_path: str) -> None:
        super().__init__(name="NDJSONLogger")
        self.path = Path(out_path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def on_epoch_end(
        self, epoch: int, metrics: Dict[str, Any], state: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        rec = {"epoch": epoch, **(metrics or {})}
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(rec) + "\n")
        return None
