# MCP Versioning and Compatibility

## Overview

The MCP (Model Context Protocol) versioning and compatibility system ensures seamless communication between different versions of MCP servers and clients. This capability provides version negotiation, backward compatibility, and graceful degradation when version mismatches occur.

## Core Concepts

### Version Negotiation

MCP versioning uses semantic versioning (MAJOR.MINOR.PATCH) to manage compatibility:

- **MAJOR**: Breaking changes that require coordinated upgrades
- **MINOR**: Backward-compatible feature additions
- **PATCH**: Backward-compatible bug fixes

### Compatibility Matrix

The system maintains a compatibility matrix that defines which versions can interoperate:

```python
# Example compatibility definition
MCP_VERSIONS = {
    "supported": ["1.0.0", "1.1.0", "1.2.0"],
    "minimum": "1.0.0",
    "current": "1.2.0",
    "deprecated": ["0.9.0"],
}
```

## Implementation

### Version Constants

Define supported versions in your MCP implementation:

```python
from typing import List, Dict, Optional

# Version configuration
MCP_VERSIONS = {
    "supported": ["1.0.0", "1.1.0", "1.2.0"],
    "minimum": "1.0.0",  # Oldest supported version
    "current": "1.2.0",  # Current implementation version
    "deprecated": ["0.9.0"],  # Warn but still support
}

def get_supported_versions() -> List[str]:
    """
    Returns list of supported MCP versions.
    
    This function provides version information for negotiation
    with MCP clients and servers.
    
    Returns:
        List of version strings in semantic versioning format
    """
    return MCP_VERSIONS["supported"]
```

### Version Negotiation

Implement version negotiation to establish compatible communication:

```python
def negotiate_version(
    requested_version: str,
    supported_versions: List[str] = None
) -> Optional[str]:
    """
    Negotiate MCP version between client and server.
    
    Selects the highest mutually supported version. Returns None
    if no compatible version exists.
    
    Args:
        requested_version: Version requested by client/server
        supported_versions: List of versions we support (defaults to MCP_VERSIONS)
        
    Returns:
        Negotiated version string, or None if incompatible
        
    Examples:
        >>> negotiate_version("1.1.0")
        "1.1.0"
        
        >>> negotiate_version("2.0.0")  # Not supported
        None
        
        >>> negotiate_version("0.9.0")  # Deprecated but still works
        "0.9.0"
    """
    if supported_versions is None:
        supported_versions = MCP_VERSIONS["supported"]
    
    # Validate input
    if not requested_version or not isinstance(requested_version, str):
        return None
        
    # Check if requested version is supported
    if requested_version in supported_versions:
        return requested_version
        
    # Check deprecated versions (warn but allow)
    if requested_version in MCP_VERSIONS.get("deprecated", []):
        import warnings
        warnings.warn(
            f"MCP version {requested_version} is deprecated. "
            f"Please upgrade to {MCP_VERSIONS['current']}"
        )
        return requested_version
        
    # No compatible version found
    return None
```

### Backward Compatibility Handling

Handle version-specific features gracefully:

```python
def supports_feature(feature: str, version: str) -> bool:
    """
    Check if a feature is supported in given MCP version.
    
    This enables backward-compatible feature detection
    and graceful degradation for older clients.
    
    Args:
        feature: Feature identifier (e.g., "streaming", "batch_ops")
        version: MCP version to check
        
    Returns:
        True if feature is supported in this version
        
    Examples:
        >>> supports_feature("streaming", "1.2.0")
        True
        
        >>> supports_feature("streaming", "1.0.0")
        False
    """
    # Feature availability matrix
    feature_versions = {
        "streaming": "1.1.0",  # Available from 1.1.0+
        "batch_ops": "1.2.0",  # Available from 1.2.0+
        "compression": "1.0.0",  # Available from start
    }
    
    min_version = feature_versions.get(feature)
    if not min_version:
        return False
        
    # Simple version comparison (in production, use packaging.version)
    from packaging import version as pkg_version
    try:
        return pkg_version.parse(version) >= pkg_version.parse(min_version)
    except Exception:
        return False
```

## Configuration

### Environment Variables

Configure versioning behavior via environment:

```bash
# Set current MCP version
export MCP_VERSION="1.2.0"

# Set minimum supported version
export MCP_MIN_VERSION="1.0.0"

# Enable strict version checking (reject deprecated)
export MCP_STRICT_VERSIONS="true"
```

### Configuration File

Use YAML/JSON for more complex version policies:

```yaml
# mcp_versions.yaml
versioning:
  current: "1.2.0"
  minimum: "1.0.0"
  supported:
    - "1.0.0"
    - "1.1.0"
    - "1.2.0"
  deprecated:
    - "0.9.0"
  features:
    streaming:
      min_version: "1.1.0"
      description: "Streaming response support"
    batch_ops:
      min_version: "1.2.0"
      description: "Batch operation support"
```

## Best Practices

### 1. Version Detection

Always detect and log the negotiated version:

```python
def establish_connection(client_version: str):
    """Establish MCP connection with version negotiation."""
    negotiated = negotiate_version(client_version)
    
    if not negotiated:
        raise ValueError(
            f"Incompatible MCP version: {client_version}. "
            f"Supported: {MCP_VERSIONS['supported']}"
        )
        
    logging.info(f"MCP connection established: v{negotiated}")
    return negotiated
```

### 2. Graceful Degradation

Provide fallback behavior for unsupported features:

```python
def process_request(request, version):
    """Process request with version-appropriate handling."""
    if supports_feature("streaming", version):
        return stream_response(request)
    else:
        # Fallback to buffered response
        return buffer_response(request)
```

### 3. Migration Paths

Provide clear migration guidance when deprecating versions:

```python
def check_version_status(version: str) -> Dict[str, Any]:
    """
    Check version status and provide migration guidance.
    
    Returns information about version support status,
    deprecation warnings, and upgrade recommendations.
    """
    if version in MCP_VERSIONS["deprecated"]:
        return {
            "status": "deprecated",
            "supported": True,
            "warning": f"Version {version} will be removed in next major release",
            "recommended": MCP_VERSIONS["current"],
            "migration_guide": "http://localhost:8080/mcp/migration"
        }
    elif version in MCP_VERSIONS["supported"]:
        return {
            "status": "supported",
            "supported": True,
            "current": version == MCP_VERSIONS["current"]
        }
    else:
        return {
            "status": "unsupported",
            "supported": False,
            "error": f"Version {version} is not supported",
            "minimum": MCP_VERSIONS["minimum"]
        }
```

## Testing

### Version Negotiation Tests

Test version negotiation scenarios:

```python
def test_version_negotiation():
    """Test version negotiation logic."""
    # Supported version
    assert negotiate_version("1.1.0") == "1.1.0"
    
    # Unsupported version
    assert negotiate_version("2.0.0") is None
    
    # Edge cases
    assert negotiate_version("") is None
    assert negotiate_version(None) is None
```

### Compatibility Tests

Test backward compatibility:

```python
def test_feature_compatibility():
    """Test feature availability across versions."""
    assert supports_feature("compression", "1.0.0")
    assert supports_feature("streaming", "1.2.0")
    assert not supports_feature("streaming", "1.0.0")
```

## Troubleshooting

### Version Mismatch Errors

**Problem**: Client cannot connect due to version mismatch

**Solution**:
1. Check client and server versions
2. Verify compatibility matrix
3. Upgrade to mutually supported version

```python
# Debug version issues
def debug_version_compatibility(client_version, server_version):
    """Debug version compatibility issues."""
    print(f"Client version: {client_version}")
    print(f"Server version: {server_version}")
    print(f"Server supports: {MCP_VERSIONS['supported']}")
    
    compatible = negotiate_version(client_version)
    if compatible:
        print(f"✓ Compatible: {compatible}")
    else:
        print("✗ Incompatible versions")
        print(f"  Minimum required: {MCP_VERSIONS['minimum']}")
```

### Deprecated Version Warnings

**Problem**: Using deprecated MCP version

**Solution**: Plan migration to current version

1. Review migration guide
2. Test new version in development
3. Schedule upgrade
4. Monitor for issues

## Security Considerations

### Version-Based Vulnerabilities

- **Validation**: Always validate version strings to prevent injection
- **Bounds Checking**: Enforce maximum supported version
- **Timeout**: Set negotiation timeout to prevent DoS
- **Rate Limiting**: Limit version negotiation attempts

```python
def validate_version_string(version: str) -> bool:
    """
    Validate version string format for security.
    
    Prevents version string injection and ensures
    valid semantic versioning format.
    
    Args:
        version: Version string to validate
        
    Returns:
        True if valid, False otherwise
    """
    import re
    
    # Semantic versioning pattern with safeguards
    pattern = r'^(\d+)\.(\d+)\.(\d+)$'
    
    if not isinstance(version, str):
        return False
        
    # Length bounds check (prevent DoS)
    if len(version) > 20:
        return False
        
    # Format validation
    if not re.match(pattern, version):
        return False
        
    # Component bounds (reasonable limits)
    parts = version.split('.')
    for part in parts:
        if int(part) > 999:
            return False
            
    return True
```

## Related Capabilities

- **mcp-configuration**: Version-specific configuration
- **mcp-schema-validation**: Version-specific schema validation  
- **mcp-error-handling**: Version-aware error handling
- **mcp-protocol-surface**: Protocol evolution across versions

## Keywords

versioning, compatibility, negotiation, semver, semantic-versioning, backward-compatible, deprecation, migration, protocol-version, API-version, version-negotiation, compatibility-matrix

## References

- [Semantic Versioning 2.0.0](https://semver.org/)
- [API Versioning Best Practices](http://localhost:8080/api-versioning)
- MCP Protocol Specification
- Version Negotiation RFC
