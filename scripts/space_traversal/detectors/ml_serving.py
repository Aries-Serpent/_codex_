"""
Dynamic Detector: ML Serving (v1.4.0)

Identifies ML serving and inference capabilities including:
- API endpoints (FastAPI, Flask)
- Prediction/inference modules
- Model serving infrastructure

Enhanced patterns for Codex ML platform.
"""
from __future__ import annotations

from typing import Set


def detect(file_index: dict) -> dict:
    """
    Detect ML serving capability.
    
    Args:
        file_index: Context index with file metadata
        
    Returns:
        Detection result with id, evidence, patterns, and metadata
    """
    files = file_index.get("files", [])
    evidence: Set[str] = set()
    found: Set[str] = set()
    required = ["serve", "predict", "api"]
    
    # Patterns to detect serving infrastructure
    serve_patterns = ["serve", "server", "serving"]
    api_patterns = ["fastapi", "flask", "api"]
    inference_patterns = ["predict", "inference", "infer"]
    
    for meta in files:
        path = meta["path"]
        lower_path = path.lower()
        
        # Check for serving patterns
        if any(pattern in lower_path for pattern in serve_patterns):
            evidence.add(path)
            found.add("serve")
        
        # Check for API frameworks
        if any(pattern in lower_path for pattern in api_patterns):
            evidence.add(path)
            found.add("api")
        
        # Check for inference/prediction
        if any(pattern in lower_path for pattern in inference_patterns):
            evidence.add(path)
            found.add("predict")
        
        # Check specific file patterns
        if path.endswith("_server.py") or path.endswith("_api.py"):
            evidence.add(path)
            found.add("serve")
            found.add("api")
    
    return {
        "id": "ml-serving",
        "evidence_files": sorted(evidence),
        "found_patterns": sorted(found),
        "required_patterns": required,
        "meta": {
            "layer": "inference",
            "priority": "high",
            "category": "deployment"
        }
    }
