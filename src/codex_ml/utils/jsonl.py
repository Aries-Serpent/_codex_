from __future__ import annotations

import json
from pathlib import Path
from typing import Mapping


def append_jsonl(path: str | Path, record: Mapping[str, object]) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(dict(record), ensure_ascii=False) + "\n")


__all__ = ["append_jsonl"]
