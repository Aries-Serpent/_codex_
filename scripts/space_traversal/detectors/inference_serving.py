"""
import logging
logger = logging.getLogger(__name__)
Dynamic Detector: Inference Serving (P4)

Identifies serving layer components (FastAPI / Flask, server modules, gRPC, model serving).

Heuristic:
- Evidence: files containing 'fastapi' or 'flask' tokens OR paths with 'serve'
- Content-based detection for API patterns
- required_patterns includes server framework indicators
"""

from __future__ import annotations

from pathlib import Path

MAX_READ_BYTES = 200_000
REPO_ROOT = Path(__file__).resolve().parents[3]


def _read_text(path_input) -> str:
    """
    Read text from file with bounded read.

    Safeguard: Bounded read to prevent memory issues.
    Validation: Handles both string and Path inputs.
    """
    try:
        path = Path(path_input) if isinstance(path_input, str) else path_input

        if not path.is_absolute():
            path = REPO_ROOT / path

        if not path.exists():
            return ""

        return path.read_text(encoding="utf-8", errors="ignore")[:MAX_READ_BYTES]
    except (OSError, IOError, UnicodeDecodeError):
        return ""


def detect(file_index: dict) -> dict:
    files = file_index.get("files", [])
    evidence = []
    found = set()
    required = ["fastapi", "flask", "serve", "predict", "inference"]

    # API patterns to detect
    api_patterns = {
        "fastapi": ["FastAPI", "@app.post", "@app.get", "from fastapi"],
        "flask": ["Flask", "@app.route", "from flask"],
        "grpc": ["grpc", "servicer", "proto"],
        "inference": ["predict", "inference", "model.predict"],
        "serve": ["/predict", "/inference", "/serve", "uvicorn", "gunicorn"],
    }

    for meta in files:
        p = meta["path"]
        lower = p.lower()

        # Path-based detection
        if "serve" in lower or lower.endswith("_server.py") or "api/" in lower:
            evidence.append(p)
            found.add("serve")

        # Content-based detection for Python files
        ext = meta.get("ext", ".")
        if ext == ".py":
            text = _read_text(p)
            if text:
                # Check for API patterns
                for pattern_name, keywords in api_patterns.items():
                    if any(kw in text for kw in keywords):
                        if p not in evidence:
                            evidence.append(p)
                        found.add(pattern_name)

    # Calculate functionality score
    functionality_score = len(found & set(required)) / len(required) if required else 0.0

    return {
        "id": "inference-serving",
        "evidence_files": sorted(set(evidence)),
        "found_patterns": sorted(found),
        "required_patterns": required,
        "docs_keywords": [
            "inference",
            "serving",
            "api",
            "predict",
            "fastapi",
            "flask",
            "model-serving",
        ],
        "safeguards": ["validation", "bounded", "error-handling", "timeout"],
        "functionality_impl": functionality_score,
        "meta": {
            "layer": "serving",
            "interface": "http",
            "deterministic": True,
            "offline": True,
            "bounded": True,
        },
    }
