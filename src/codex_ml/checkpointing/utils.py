"""Checkpointing scaffolding for _codex_.

Provides trivial save/load helpers for small dictionaries. Real implementations
should handle model weights, optimizer state, and RNG.
"""

import json
from pathlib import Path
from typing import Any


def save_checkpoint(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload), encoding="utf-8")


def load_checkpoint(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))
