"""
Example dynamic detector: inference-serving

Contract:
  detect(file_index: dict) -> dict with fields:
    - id (str)
    - evidence_files (list[str])
    - found_patterns (list[str])
    - required_patterns (list[str])
    - meta (dict, optional)
"""

from __future__ import annotations

from typing import Any, Dict, List


def detect(file_index: Dict[str, Any]) -> Dict[str, Any]:
    files: List[Dict[str, Any]] = file_index.get("files", [])
    py_paths = [
        f["path"] for f in files if isinstance(f, dict) and str(f.get("path", "")).endswith(".py")
    ]
    evidence = [
        p
        for p in py_paths
        if any(tok in p.lower() for tok in ("serve", "server", "fastapi", "uvicorn"))
    ]
    found = []
    req = ["server", "fastapi"]
    # naive path-level pattern mapping (content scanning is outside this minimal example)
    for p in evidence:
        lp = p.lower()
        if "server" in lp:
            found.append("server")
        if "fastapi" in lp:
            found.append("fastapi")

    return {
        "id": "inference-serving",
        "evidence_files": sorted(set(evidence)),
        "found_patterns": sorted(set(found)),
        "required_patterns": req,
        "meta": {"layer": "serving"},
    }
