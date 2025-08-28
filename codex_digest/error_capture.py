from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass
class ErrorCapture:
    timestamp: str
    step_number: str
    step_description: str
    error_message: str
    context: str


def iso_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%MZ")


def make_error_block(step_no: str, step_desc: str, msg: str, ctx: str) -> str:
    ts = iso_now()
    return (
        f"Question for ChatGPT-5 {ts}:\n"
        f"While performing [{step_no}:{step_desc}], encountered the following error:\n"
        f"{msg}\n"
        f"Context: {ctx}\n"
        f"What are the possible causes, and how can this be resolved while preserving intended functionality?\n"
    )
