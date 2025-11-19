"""
MCP Server Lifecycle Management Capability Detector

Tracks startup, shutdown, healthz endpoints, and application lifecycle hooks.
Part of the Space Traversal audit pipeline for MCP service maturity.
"""


def detect(file_index: dict) -> dict:
    """
    Detect MCP lifecycle management capability from file index.
    
    Args:
        file_index: Dictionary with 'files' list, each item has:
                    {'path': str, 'ext': str, 'size': int, 'sha': str}
    
    Returns:
        Dictionary with required fields:
        {
            "id": "mcp-lifecycle-management",
            "evidence_files": [str, ...],
            "found_patterns": [str, ...],
            "required_patterns": [str, ...],
            "meta": {}
        }
    """
    files = file_index.get("files", [])
    evidence = []
    found = set()
    
    # Patterns indicating lifecycle management
    lifecycle_patterns = {
        "startup": ["startup", "initialize", "on_startup", "lifespan"],
        "shutdown": ["shutdown", "cleanup", "on_shutdown", "teardown"],
        "healthz": ["health", "healthz", "readiness", "liveness", "probe"],
    }
    
    required_patterns = ["startup", "shutdown", "healthz"]
    
    # Check MCP and service-related files
    for f in files:
        path = f["path"]
        path_lower = path.lower()
        
        # Focus on MCP, services, and main application files
        if any(indicator in path_lower for indicator in ["mcp/", "services/", "main.py", "app.py"]):
            # Check path components for lifecycle indicators
            for pattern_name, pattern_variants in lifecycle_patterns.items():
                if any(variant in path_lower for variant in pattern_variants):
                    evidence.append(path)
                    found.add(pattern_name)
                    break
    
    return {
        "id": "mcp-lifecycle-management",
        "evidence_files": sorted(set(evidence)),
        "found_patterns": sorted(found),
        "required_patterns": required_patterns,
        "meta": {
            "category": "mcp",
            "priority": "high",
            "framework": "FastAPI",
            "detector_version": "1.0"
        }
    }
