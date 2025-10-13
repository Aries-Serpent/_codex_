from __future__ import annotations

import os
import platform
from pathlib import Path
from typing import Any

from codex.archive.util import json_dumps_sorted, utcnow_iso

REQUIRED_FIELDS = ("action", "actor", "tool", "repo", "context")


def evidence_append(
    *, action: str, actor: str, tool: str, repo: str, context: dict[str, Any]
) -> None:
    rec = {
        "ts": utcnow_iso(),
        "action": action,
        "actor": actor or os.getenv("CODEX_ACTOR", "unknown"),
        "tool": tool,
        "repo": repo,
        "context": {
            **(context or {}),
            "os": platform.system(),
            "python": platform.python_version(),
        },
    }
    for field in REQUIRED_FIELDS:
        if not rec.get(field):
            raise ValueError(f"evidence missing required field: {field}")
    evdir = Path(os.getenv("CODEX_EVIDENCE_DIR", ".codex/evidence"))
    evdir.mkdir(parents=True, exist_ok=True)
    with (evdir / "archive_ops.jsonl").open("a", encoding="utf-8") as fh:
        fh.write(json_dumps_sorted(rec) + "\n")
