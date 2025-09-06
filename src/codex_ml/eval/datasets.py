from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

PRESETS: Dict[str, Dict[str, List[Dict[str, str]]]] = {
    "toy_copy_task": {
        "test": [
            {"input": "hello", "target": "hello"},
            {"input": "world", "target": "world"},
        ]
    },
    "tiny_wikitext": {
        "test": [
            {
                "input": "Anarchism is a political philosophy.",
                "target": "Anarchism is a political philosophy.",
            }
        ]
    },
}


def load_dataset(name_or_path: str) -> Dict[str, List[Dict[str, str]]]:
    """Load a dataset by preset name or JSONL path.

    JSONL files should contain objects with at least ``input`` and ``target`` fields.
    The return value maps split name to a list of examples.
    """
    path = Path(name_or_path)
    if path.exists():
        records = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
        return {"test": records}
    if name_or_path in PRESETS:
        return PRESETS[name_or_path]
    raise ValueError(f"Unknown dataset '{name_or_path}'")
