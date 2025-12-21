# Simple file-based checkpoint helper. Stores processed ids/checksums per input file.
import json
from pathlib import Path
from typing import Set


def load_checkpoint(path: str) -> Set[str]:
    p = Path(path)
    if not p.exists():
        return set()
    try:
        return set(json.loads(p.read_text()))
    except Exception:
        return set()


def save_checkpoint(path: str, seen: Set[str]):
    p = Path(path)
    p.write_text(json.dumps(list(seen)))
