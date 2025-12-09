"""
MCP Configuration Management Capability Detector

Tracks configuration files, environment handling, mcp.json schema validation,
and runtime configuration management for MCP services.
"""


def detect(file_index: dict) -> dict:
    """
    Detect MCP configuration management capability from file index.
    
    Args:
        file_index: Dictionary with 'files' list, each item has:
                    {'path': str, 'ext': str, 'size': int, 'sha': str}
    
    Returns:
        Dictionary with required fields:
        {
            "id": "mcp-configuration",
            "evidence_files": [str, ...],
            "found_patterns": [str, ...],
            "required_patterns": [str, ...],
            "meta": {}
        }
    """
    files = file_index.get("files", [])
    evidence = []
    found = set()
    
    # Configuration file patterns
    config_files = [
        "mcp.json",
        "mcp_config",
        ".env",
        ".env.example",
        "config.yaml",
        "config.yml",
        "settings.py",
        "configuration.py"
    ]
    
    # Patterns to detect
    config_patterns = {
        "config": ["config", "settings", "configuration"],
        "environment": [".env", "environment", "env_var"],
        "mcp.json": ["mcp.json", "mcp_schema", "mcp_config"]
    }
    
    required_patterns = ["config", "environment", "mcp.json"]
    
    # Check all files for configuration indicators
    for f in files:
        path = f["path"]
        path_lower = path.lower()
        filename = path.split("/")[-1].lower()
        
        # Direct config file matches
        if any(cfg_file in filename for cfg_file in config_files):
            evidence.append(path)
            
            # Determine which pattern this satisfies
            if "mcp.json" in filename or "mcp_config" in filename:
                found.add("mcp.json")
            if ".env" in filename or "environment" in filename:
                found.add("environment")
            if "config" in filename or "settings" in filename:
                found.add("config")
        
        # Check MCP and service directories for config-related files
        elif any(indicator in path_lower for indicator in ["mcp/", "services/", "config/"]):
            # Check for configuration-related content in path
            for pattern_name, pattern_variants in config_patterns.items():
                if any(variant in path_lower for variant in pattern_variants):
                    evidence.append(path)
                    found.add(pattern_name)
                    break
    
    return {
        "id": "mcp-configuration",
        "evidence_files": sorted(set(evidence)),
        "found_patterns": sorted(found),
        "required_patterns": required_patterns,
        "docs_keywords": [
            "mcp", "configuration", "settings", "environment", "mcp.json",
            "config", "management", "runtime", "validation", "safeguards",
            "configuration-management", "env-vars", "config-files"
        ],
        "meta": {
            "category": "mcp",
            "layer": "infrastructure",
            "detector_version": "1.1",
            "config_types": ["mcp.json", "environment", "yaml", "python"],
            "safeguards": ["validation", "type-checking", "bounds-checking", "secret-management"]
        }
    }
