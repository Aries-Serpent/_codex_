# MCP Tooling Registry

## Overview

The MCP tooling registry capability provides centralized registration, discovery, and invocation of tools in Model Context Protocol services. Tools are reusable capabilities that can be dynamically loaded, configured, and executed.

**Keywords**: mcp, tools, registry, tooling, discovery, invocation, capabilities, plugins, extensions, management

## Purpose

Manages MCP tools through:
- **Tool Registration**: Register tools with metadata and schemas
- **Tool Discovery**: Find available tools by name, category, or capability
- **Tool Invocation**: Execute tools with validation and error handling
- **Tool Lifecycle**: Load, unload, and reload tools dynamically
- **Tool Metadata**: Store descriptions, schemas, versions for each tool

## Architecture

### Registry Components

```
┌─────────────────────────────────────┐
│   Tool Registry (Central Store)     │
│   - Tool metadata                   │
│   - Tool schemas                    │
│   - Tool handlers                   │
└─────────────┬───────────────────────┘
              │
              ├──── Tool Loader
              │     (Dynamic import)
              │
              ├──── Tool Validator
              │     (Schema validation)
              │
              └──── Tool Executor
                    (Safe execution)
```

### Tool Lifecycle

```
Register → Validate → Store → Discover → Invoke → Result
    ↓                                      ↓
  Metadata                            Execution
  Schema                              Context
```

## Configuration

### mcp.json Tool Configuration

```json
{
  "tools": {
    "registry_path": "./tools",
    "auto_discover": true,
    "enabled_tools": ["code_analysis", "documentation", "testing"],
    "tool_config": {
      "code_analysis": {
        "max_file_size_mb": 10,
        "timeout_seconds": 30
      },
      "documentation": {
        "formats": ["markdown", "html"],
        "templates_path": "./templates"
      }
    }
  }
}
```

### Tool Registration

```python
# registry.py
from typing import Dict, Callable, Any
from pydantic import BaseModel

class ToolMetadata(BaseModel):
    name: str
    version: str
    description: str
    category: str
    schema: dict
    enabled: bool = True

class ToolRegistry:
    """Central registry for MCP tools."""
    
    def __init__(self):
        self._tools: Dict[str, tuple[ToolMetadata, Callable]] = {}
    
    def register(self, metadata: ToolMetadata, handler: Callable):
        """Register a tool with the registry."""
        if metadata.name in self._tools:
            raise ValueError(f"Tool '{metadata.name}' already registered")
        
        # Validate handler signature
        self._validate_handler(handler, metadata.schema)
        
        self._tools[metadata.name] = (metadata, handler)
        print(f"✓ Registered tool: {metadata.name} v{metadata.version}")
    
    def get_tool(self, name: str) -> tuple[ToolMetadata, Callable]:
        """Retrieve tool by name."""
        if name not in self._tools:
            raise KeyError(f"Tool '{name}' not found in registry")
        return self._tools[name]
    
    def list_tools(self, category: str = None) -> list[ToolMetadata]:
        """List all registered tools, optionally filtered by category."""
        tools = [meta for meta, _ in self._tools.values()]
        if category:
            tools = [t for t in tools if t.category == category]
        return tools
    
    def _validate_handler(self, handler: Callable, schema: dict):
        """Validate handler signature matches schema."""
        import inspect
        sig = inspect.signature(handler)
        # Validate parameters match schema
        # ... validation logic ...

# Global registry instance
registry = ToolRegistry()
```

## Usage Examples

### Example 1: Register a Tool

```python
from pydantic import BaseModel

# Define tool schema
class CodeAnalysisRequest(BaseModel):
    file_path: str
    analysis_types: list[str]

class CodeAnalysisResponse(BaseModel):
    issues: list[dict]
    metrics: dict

# Define tool handler
def analyze_code(request: CodeAnalysisRequest) -> CodeAnalysisResponse:
    """Analyze code quality and detect issues."""
    # ... analysis logic ...
    return CodeAnalysisResponse(
        issues=[],
        metrics={"complexity": 5, "lines": 100}
    )

# Register tool
metadata = ToolMetadata(
    name="code_analysis",
    version="1.0.0",
    description="Analyzes code quality and detects issues",
    category="analysis",
    schema={
        "request": CodeAnalysisRequest.schema(),
        "response": CodeAnalysisResponse.schema()
    }
)

registry.register(metadata, analyze_code)
```

### Example 2: Discover Tools

```python
# List all tools
all_tools = registry.list_tools()
for tool in all_tools:
    print(f"- {tool.name} v{tool.version}: {tool.description}")

# Filter by category
analysis_tools = registry.list_tools(category="analysis")
print(f"Found {len(analysis_tools)} analysis tools")

# Get specific tool
metadata, handler = registry.get_tool("code_analysis")
print(f"Tool schema: {metadata.schema}")
```

### Example 3: Invoke a Tool

```python
def invoke_tool(tool_name: str, parameters: dict) -> dict:
    """Safely invoke a tool with validation."""
    try:
        # Get tool from registry
        metadata, handler = registry.get_tool(tool_name)
        
        if not metadata.enabled:
            raise ValueError(f"Tool '{tool_name}' is disabled")
        
        # Validate parameters against schema
        request_model = metadata.schema["request"]
        validated_params = request_model(**parameters)
        
        # Execute tool
        result = handler(validated_params)
        
        return {
            "success": True,
            "result": result.dict(),
            "tool": tool_name,
            "version": metadata.version
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "tool": tool_name
        }

# Usage
response = invoke_tool(
    "code_analysis",
    {
        "file_path": "src/main.py",
        "analysis_types": ["complexity", "style"]
    }
)
```

### Example 4: Dynamic Tool Loading

```python
import importlib
from pathlib import Path

def auto_discover_tools(tools_dir: str = "./tools"):
    """Automatically discover and register tools."""
    tools_path = Path(tools_dir)
    
    for tool_file in tools_path.glob("*.py"):
        if tool_file.stem.startswith("_"):
            continue
        
        # Import tool module
        module_name = f"tools.{tool_file.stem}"
        module = importlib.import_module(module_name)
        
        # Look for register function
        if hasattr(module, "register_tool"):
            try:
                module.register_tool(registry)
                print(f"✓ Loaded tool from {tool_file.name}")
            except Exception as e:
                print(f"✗ Failed to load {tool_file.name}: {e}")

# Usage
auto_discover_tools()
```

### Example 5: Tool Versioning

```python
class VersionedRegistry(ToolRegistry):
    """Registry supporting multiple tool versions."""
    
    def register(self, metadata: ToolMetadata, handler: Callable):
        """Register tool with version support."""
        key = f"{metadata.name}@{metadata.version}"
        self._tools[key] = (metadata, handler)
    
    def get_tool(self, name: str, version: str = "latest") -> tuple:
        """Get specific version of tool."""
        if version == "latest":
            # Find latest version
            versions = [
                (meta, handler)
                for key, (meta, handler) in self._tools.items()
                if key.startswith(f"{name}@")
            ]
            if not versions:
                raise KeyError(f"Tool '{name}' not found")
            
            # Sort by version and return latest
            latest = max(versions, key=lambda x: x[0].version)
            return latest
        else:
            key = f"{name}@{version}"
            if key not in self._tools:
                raise KeyError(f"Tool '{name}' version '{version}' not found")
            return self._tools[key]

# Usage
registry_v = VersionedRegistry()
metadata_v1, _ = registry_v.get_tool("code_analysis", "1.0.0")
metadata_latest, _ = registry_v.get_tool("code_analysis", "latest")
```

## Integration with Audit Pipeline

### Detection Command

```bash
# Check tooling registry capability
python scripts/space_traversal/audit_runner.py explain mcp-tooling-registry

# Run full audit
python scripts/space_traversal/audit_runner.py run
```

### Programmatic Detection

```python
from scripts.space_traversal.detectors import mcp_tooling_registry

# Run detector
file_index = {
    "files": [
        {"path": "mcp.json"},
        {"path": "src/services/mcp/registry.py"},
        {"path": "tools/code_analysis.py"}
    ]
}

result = mcp_tooling_registry.detect(file_index)
print(f"Found patterns: {result['found_patterns']}")
```

## Best Practices

### Tool Design

1. **Single Responsibility**: Each tool should do one thing well
2. **Clear Schema**: Define explicit input/output schemas
3. **Error Handling**: Return structured errors, don't raise exceptions
4. **Idempotent**: Tools should be safe to retry

### Registry Management

1. **Lazy Loading**: Load tools on first use, not at startup
2. **Tool Isolation**: Execute tools in isolated contexts
3. **Resource Limits**: Set timeouts and memory limits per tool
4. **Audit Logging**: Log all tool invocations

### Security

1. **Validate Inputs**: Always validate against schema
2. **Sanitize Outputs**: Clean tool results before returning
3. **Permission Checks**: Verify user has permission to invoke tool
4. **Rate Limiting**: Limit tool invocation frequency

## Troubleshooting

### Issue: Tool Not Found

```python
if tool_name not in registry._tools:
    available = registry.list_tools()
    print(f"Available tools: {[t.name for t in available]}")
```

### Issue: Tool Invocation Failure

```python
import traceback

try:
    result = handler(request)
except Exception as e:
    print(f"Tool failed: {e}")
    traceback.print_exc()
```

### Issue: Schema Validation Error

```python
from pydantic import ValidationError

try:
    validated = RequestModel(**params)
except ValidationError as e:
    print(f"Invalid parameters: {e.json()}")
```

## Performance Considerations

- **Tool Caching**: Cache tool handlers after first load
- **Async Execution**: Use async for I/O-bound tools
- **Batch Processing**: Support batch invocations for efficiency

## Monitoring

### Tool Usage Metrics

```python
tool_invocations = {}

def track_invocation(tool_name: str, duration_ms: float, success: bool):
    if tool_name not in tool_invocations:
        tool_invocations[tool_name] = {
            "count": 0,
            "success": 0,
            "total_duration_ms": 0
        }
    
    stats = tool_invocations[tool_name]
    stats["count"] += 1
    stats["success"] += int(success)
    stats["total_duration_ms"] += duration_ms
```

## Related Capabilities

- **mcp-configuration**: Tool configuration management
- **mcp-schema-validation**: Tool schema validation
- **mcp-protocol-surface**: MCP protocol tool integration

## Safeguards

1. **Input Validation**: All tool inputs validated
2. **Timeout Handling**: Tools have execution timeouts
3. **Error Isolation**: Tool errors don't crash system
4. **Resource Limits**: Memory and CPU limits per tool
5. **Audit Trail**: All invocations logged

---

**Last Updated**: Previous Cycle-12-09  
**Capability ID**: mcp-tooling-registry
