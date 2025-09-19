"""
Thin helpers to keep tool specs aligned and demonstrate integration with our safety wrapper.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

# Reuse existing safety harness if/when calling LLMs
# from tools.codex_safety.openai_wrapper import call_openai_stream, call_openai_json  # noqa: F401


def load_toolspecs(directory: str | Path) -> List[Dict[str, Any]]:
    """
    Load all *.json tool spec files from a directory.
    """
    d = Path(directory)
    specs: List[Dict[str, Any]] = []
    for p in sorted(d.glob("*.json")):
        with p.open("r", encoding="utf-8") as fh:
            specs.append(json.load(fh))
    return specs


if __name__ == "__main__":
    # Demo: list loaded specs
    here = Path(__file__).resolve().parents[1] / "toolspecs"
    for spec in load_toolspecs(here):
        print(f"- {spec['name']}: {spec.get('description','')}")
