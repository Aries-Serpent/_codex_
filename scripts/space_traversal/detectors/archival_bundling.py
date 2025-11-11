"""
Dynamic Detector: Archival & Bundling (v1.4.0)

Identifies archival and bundling capabilities including:
- Archive creation and extraction
- Bundle management and validation
- Manifest generation
- Pointer file handling

Codex-specific archival infrastructure for reproducibility.
"""
from __future__ import annotations

from typing import Set


def detect(file_index: dict) -> dict:
    """
    Detect archival and bundling capability.
    
    Args:
        file_index: Context index with file metadata
        
    Returns:
        Detection result with id, evidence, patterns, and metadata
    """
    files = file_index.get("files", [])
    evidence: Set[str] = set()
    found: Set[str] = set()
    required = ["archive", "bundle", "manifest"]
    
    # Patterns to detect archival infrastructure
    archive_patterns = ["archive", "archival"]
    bundle_patterns = ["bundle", "bundling"]
    manifest_patterns = ["manifest", "pointer"]
    
    for meta in files:
        path = meta["path"]
        lower_path = path.lower()
        
        # Check for archival modules
        if any(pattern in lower_path for pattern in archive_patterns):
            evidence.add(path)
            found.add("archive")
        
        # Check for bundling infrastructure
        if any(pattern in lower_path for pattern in bundle_patterns):
            evidence.add(path)
            found.add("bundle")
        
        # Check for manifest/pointer files
        if any(pattern in lower_path for pattern in manifest_patterns):
            evidence.add(path)
            found.add("manifest")
        
        # Specific patterns
        if path.endswith(".pointer.json"):
            evidence.add(path)
            found.add("manifest")
        
        # Archive validation scripts
        if "validate_prefix" in lower_path or "prefix_validation" in lower_path:
            evidence.add(path)
            found.add("archive")
    
    return {
        "id": "archival-bundling",
        "evidence_files": sorted(evidence),
        "found_patterns": sorted(found),
        "required_patterns": required,
        "meta": {
            "layer": "storage",
            "priority": "high",
            "category": "reproducibility"
        }
    }
