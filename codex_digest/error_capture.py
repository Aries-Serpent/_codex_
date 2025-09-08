from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


@dataclass
class ErrorCapture:
    timestamp: str
    step_number: str
    step_description: str
    error_message: str
    context: str


def iso_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%MZ")


def make_error_block(step_no: str, step_desc: str, msg: str, ctx: str, ts: str | None = None) -> str:
    ts = ts or iso_now()
    return (
        f"Question for ChatGPT-5 {ts}:\n"
        f"While performing [{step_no}:{step_desc}], encountered the following error:\n"
        f"{msg}\n"
        f"Context: {ctx}\n"
        f"What are the possible causes, and how can this be resolved while preserving intended functionality?\n"
    )


CODEX_DIR = Path(__file__).resolve().parents[1] / ".codex"
ERRORS_NDJSON = CODEX_DIR / "errors.ndjson"


def log_error(step_no: str, step_desc: str, msg: str, ctx: str, *, errors_path: Path | None = None) -> str:
    """Append an error capture block to `.codex/errors.ndjson` and stderr."""
    ts = iso_now()
    block = make_error_block(step_no, step_desc, msg, ctx, ts=ts)
    path = errors_path or ERRORS_NDJSON
    path.parent.mkdir(parents=True, exist_ok=True)
    record = {
        "ts": ts,
        "step": step_no,
        "step_description": step_desc,
        "error": msg,
        "context": ctx,
    }
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record) + "\n")
    sys.stderr.write(block)
    return block
