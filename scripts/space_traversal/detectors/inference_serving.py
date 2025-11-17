"""
Dynamic Detector: Inference Serving (P4)

Identifies serving layer components (FastAPI / Flask, server modules).

Heuristic:
- Evidence: files containing 'fastapi' or 'flask' tokens OR paths with 'serve'
- required_patterns includes server framework indicators
"""

from __future__ import annotations


def detect(file_index: dict) -> dict:
    files = file_index.get("files", [])
    evidence = []
    found = set()
    required = ["fastapi", "flask", "serve"]

    for meta in files:
        p = meta["path"]
        lower = p.lower()
        if "serve" in lower or lower.endswith("_server.py"):
            evidence.append(p)
            found.add("serve")
        # lightweight content hint (only ext)
        ext = meta.get("ext", ".")
        if ext in {".py", ".md"}:
            # Just path-based hints; deeper content scan in future
            if "fastapi" in lower:
                evidence.append(p)
                found.add("fastapi")
            if "flask" in lower:
                evidence.append(p)
                found.add("flask")

    return {
        "id": "inference-serving",
        "evidence_files": sorted(set(evidence)),
        "found_patterns": sorted(found),
        "required_patterns": required,
        "meta": {"layer": "serving", "interface": "http"},
    }
