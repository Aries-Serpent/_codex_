from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class KBRecord:
    id: str
    text: str
    meta: dict[str, Any]


def validate_kb(rec: dict[str, Any]) -> None:
    if not isinstance(rec, dict):
        raise ValueError("KB rec not object")
    if "id" not in rec or not rec["id"]:
        raise ValueError("KB rec missing id")
    if "text" not in rec or not isinstance(rec["text"], str):
        raise ValueError("KB rec missing text")
    if "meta" not in rec or not isinstance(rec["meta"], dict):
        raise ValueError("KB rec missing meta")
    meta = rec["meta"]
    for key in ("source_path", "domain", "intent", "lang"):
        if key not in meta:
            raise ValueError(f"KB meta missing {key}")
