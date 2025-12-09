"""
MCP Server Lifecycle Management Capability Detector

Tracks startup, shutdown, healthz endpoints, and application lifecycle hooks.
Part of the Space Traversal audit pipeline for MCP service maturity.
"""
from pathlib import Path


def detect(file_index: dict) -> dict:
    """
    Detect MCP lifecycle management capability from file index.
    
    Args:
        file_index: Dictionary with 'files' list, each item has:
                    {'path': str, 'ext': str, 'size': int, 'sha': str}
    
    Returns:
        Dictionary with required fields
    """
    files = file_index.get("files", [])
    evidence = []
    found = set()
    
    # Patterns indicating lifecycle management
    lifecycle_keywords = {
        "startup": ["startup", "initialize", "LifecycleManager", "register_startup_hook"],
        "shutdown": ["shutdown", "cleanup", "register_shutdown_hook", "teardown"],
        "healthz": ["healthz", "is_healthy", "is_ready", "health_check"],
    }
    
    required_patterns = ["startup", "shutdown", "healthz"]
    
    # Check relevant files
    for f in files:
        path = f["path"]
        path_lower = path.lower()
        
        # Focus on lifecycle-related files
        is_relevant = (
            "lifecycle" in path_lower or
            "mcp/" in path_lower or
            "services/mcp/" in path_lower or
            ("test" in path_lower and "mcp" in path_lower) or
            ("docs" in path_lower and "mcp" in path_lower and "lifecycle" in path_lower)
        )
        
        if is_relevant:
            evidence.append(path)
            # Check what patterns this file likely contains based on name
            for pattern_name, keywords in lifecycle_keywords.items():
                if any(kw.lower() in path_lower for kw in keywords):
                    found.add(pattern_name)
    
    return {
        "id": "mcp-lifecycle-management",
        "evidence_files": sorted(set(evidence)),
        "found_patterns": sorted(found),
        "required_patterns": required_patterns,
        "docs_keywords": ["startup", "shutdown", "healthz", "lifecycle", "initialization", "cleanup"],
        "meta": {
            "category": "mcp",
            "priority": "high",
            "framework": "FastAPI",
            "detector_version": "1.2",
            "implementation": "src/services/mcp/lifecycle.py",
            "tests": "tests/mcp/test_lifecycle_management.py"
        }
    }
