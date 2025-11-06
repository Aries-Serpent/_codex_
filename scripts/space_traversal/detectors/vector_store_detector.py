"""
Detector: Vector Stores Presence (stub/mocks) (S-vector)

Detects vector store stub implementations for audit pipeline.
"""
from typing import Dict, List

TARGET_DIR = "codex_addons/vector_stores/"


def detect(file_index: dict) -> dict:
    """
    Detect vector store stub files in the codebase.
    
    Args:
        file_index: Dictionary containing file information
        
    Returns:
        Detection result with evidence files and patterns
    """
    files: List[str] = [
        f["path"] 
        for f in file_index.get("files", []) 
        if f["path"].startswith(TARGET_DIR)
    ]
    
    found = []
    required = ["connect", "upsert", "query"]
    
    # Evidence is path-based; patterns will be validated by static scans in the future.
    return {
        "id": "vector-stores",
        "evidence_files": sorted(files),
        "found_patterns": found,
        "required_patterns": required,
        "meta": {"mode": "stub-or-mock"}
    }
