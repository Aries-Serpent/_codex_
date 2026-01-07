# MCP Schema Validation

## Overview

The MCP schema validation capability ensures that Model Context Protocol (MCP) services use strongly-typed schemas for requests, responses, and configurations. This includes Pydantic models for runtime validation and OpenAPI specifications for API documentation.

**Keywords**: mcp, schema, validation, pydantic, openapi, basemodel, type-safety, api, specification, contracts

## Purpose

Provides schema validation for MCP services through:
- **Runtime Type Validation**: Pydantic BaseModel usage for request/response validation
- **API Documentation**: OpenAPI/Swagger specifications for service contracts
- **Schema Evolution**: Versioned schemas with backward compatibility
- **Error Prevention**: Catch type mismatches at service boundaries

## Architecture

### Validation Stack

```
┌─────────────────────────────────────┐
│   OpenAPI Specification             │
│   (openapi.yaml)                    │
└─────────────┬───────────────────────┘
              │
              ▼
┌─────────────────────────────────────┐
│   Pydantic BaseModel Classes        │
│   (runtime validation)              │
└─────────────┬───────────────────────┘
              │
              ▼
┌─────────────────────────────────────┐
│   MCP Service Endpoints             │
│   (FastAPI routes)                  │
└─────────────────────────────────────┘
```

### Detection Strategy

The detector identifies schema validation by:
1. **Pydantic Usage**: Scanning Python files for `BaseModel` imports
2. **OpenAPI Files**: Locating `openapi.yaml` or `openapi.yml` specifications
3. **Pattern Matching**: Finding validation patterns in MCP service code

## Configuration

### Pydantic Setup

```python
# Example: MCP request/response models
from pydantic import BaseModel, Field, validator

class MCPToolRequest(BaseModel):
    """Schema for MCP tool invocation request."""
    tool_name: str = Field(..., min_length=1, description="Tool identifier")
    parameters: dict = Field(default_factory=dict, description="Tool parameters")
    context: dict = Field(default_factory=dict, description="Execution context")
    
    @validator('tool_name')
    def validate_tool_name(cls, v):
        if not v.isidentifier():
            raise ValueError('tool_name must be valid Python identifier')
        return v

class MCPToolResponse(BaseModel):
    """Schema for MCP tool invocation response."""
    success: bool
    result: Any
    error: Optional[str] = None
    execution_time_ms: float
```

### OpenAPI Configuration

```yaml
# openapi.yaml
openapi: 3.0.0
info:
  title: MCP Service API
  version: 1.0.0
paths:
  /tools/invoke:
    post:
      summary: Invoke MCP tool
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/MCPToolRequest'
      responses:
        '200':
          description: Successful invocation
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/MCPToolResponse'

components:
  schemas:
    MCPToolRequest:
      type: object
      required: [tool_name]
      properties:
        tool_name:
          type: string
        parameters:
          type: object
        context:
          type: object
```

## Usage Examples

### Example 1: Basic Request Validation

```python
from pydantic import BaseModel, ValidationError

class ExecuteRequest(BaseModel):
    command: str
    timeout_seconds: int = 30

# Valid request
try:
    req = ExecuteRequest(command="ls -la", timeout_seconds=10)
    print(f"✓ Valid: {req}")
except ValidationError as e:
    print(f"✗ Invalid: {e}")

# Invalid request (missing required field)
try:
    req = ExecuteRequest(timeout_seconds=10)  # Missing 'command'
except ValidationError as e:
    print(f"✗ Validation error: {e}")
```

### Example 2: Complex Nested Validation

```python
from typing import List, Optional
from pydantic import BaseModel, Field

class MCPCapability(BaseModel):
    name: str
    version: str
    enabled: bool = True

class MCPServerConfig(BaseModel):
    server_id: str = Field(..., min_length=1)
    capabilities: List[MCPCapability]
    max_connections: int = Field(100, gt=0, le=1000)
    timeout_ms: Optional[int] = Field(None, gt=0)
    
    class Config:
        # Enable validation on assignment
        validate_assignment = True

# Usage
config = MCPServerConfig(
    server_id="mcp-001",
    capabilities=[
        MCPCapability(name="code_analysis", version="1.0"),
        MCPCapability(name="documentation", version="2.1", enabled=False)
    ],
    max_connections=500
)
```

### Example 3: OpenAPI Auto-Generation

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(
    title="MCP Service",
    version="1.0.0",
    description="Model Context Protocol Service API"
)

class HealthResponse(BaseModel):
    status: str
    uptime_seconds: float

@app.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(status="healthy", uptime_seconds=123.45)

# Auto-generated OpenAPI available at /docs
# Export with: app.openapi()
```

### Example 4: Schema Evolution

```python
from pydantic import BaseModel, Field
from typing import Optional

# Version 1
class RequestV1(BaseModel):
    user_id: str

# Version 2 (backward compatible)
class RequestV2(BaseModel):
    user_id: str
    session_id: Optional[str] = None  # New optional field
    
    class Config:
        # Allow extra fields for forward compatibility
        extra = "allow"

# Version 3 (with deprecation)
class RequestV3(BaseModel):
    user_id: str = Field(..., deprecated=True)
    account_id: str  # New required field (breaking change)
    session_id: Optional[str] = None
```

## Integration with Audit Pipeline

### Detection Command

```bash
# Check schema validation capability
python scripts/space_traversal/audit_runner.py explain mcp-schema-validation

# Run full audit
python scripts/space_traversal/audit_runner.py run

# View evidence files
cat audit_artifacts/capabilities_raw.json | \
  jq '.capabilities[] | select(.id=="mcp-schema-validation")'
```

### Programmatic Detection

```python
from scripts.space_traversal.detectors import mcp_schema_validation

# Run detector
file_index = {
    "files": [
        {"path": "src/services/mcp/models.py"},
        {"path": "docs/api/openapi.yaml"}
    ]
}

result = mcp_schema_validation.detect(file_index)
print(f"Found patterns: {result['found_patterns']}")
print(f"Evidence files: {result['evidence_files']}")
```

## Best Practices

### Schema Design

1. **Use Descriptive Field Names**
   ```python
   # Good
   request_timestamp_ms: int
   
   # Avoid
   ts: int
   ```

2. **Add Field Descriptions**
   ```python
   timeout: int = Field(..., description="Request timeout in seconds", gt=0, le=300)
   ```

3. **Validate Business Logic**
   ```python
   @validator('end_date')
   def end_after_start(cls, v, values):
       if 'start_date' in values and v < values['start_date']:
           raise ValueError('end_date must be after start_date')
       return v
   ```

4. **Use Enums for Fixed Values**
   ```python
   from enum import Enum
   
   class Status(str, Enum):
       PENDING = "pending"
       RUNNING = "running"
       COMPLETED = "completed"
       FAILED = "failed"
   ```

### OpenAPI Best Practices

1. **Complete Descriptions**: Add descriptions to all schemas, endpoints, and parameters
2. **Example Values**: Provide realistic examples for complex schemas
3. **Error Responses**: Document all possible error codes and formats
4. **Versioning**: Include API version in URL path (`/v1/tools/invoke`)

### Validation Performance

1. **Cache Validators**: Reuse model instances when possible
2. **Lazy Validation**: Use `.construct()` for trusted internal data
3. **Selective Validation**: Use `.update_forward_refs()` for complex recursive models

## Troubleshooting

### Issue: ValidationError on Valid Data

**Symptom**: Pydantic raises errors for seemingly correct input

**Causes**:
- Type mismatch (e.g., string instead of integer)
- Missing required fields
- Field name mismatch (case sensitivity)

**Solution**:
```python
try:
    model = MyModel(**data)
except ValidationError as e:
    print(e.json(indent=2))  # Detailed error information
```

### Issue: OpenAPI Schema Mismatch

**Symptom**: OpenAPI spec doesn't match Pydantic models

**Solution**: Use FastAPI's auto-generation or `pydantic-to-openapi`:
```python
from pydantic.schema import schema

schemas = schema([MyModel, OtherModel])
with open('openapi.yaml', 'w') as f:
    yaml.dump(schemas, f)
```

### Issue: Circular References

**Symptom**: Models reference each other, causing validation failures

**Solution**:
```python
from __future__ import annotations
from typing import Optional

class Node(BaseModel):
    value: str
    children: Optional[List[Node]] = None

Node.update_forward_refs()
```

## Performance Considerations

### Validation Overhead

- **Typical overhead**: 10-50 microseconds per validation
- **Bulk validation**: Use `.parse_obj()` for lists
- **Skip validation**: Use `.construct()` for internal data

### Optimization Tips

```python
# Fast path for trusted data
fast_model = MyModel.construct(**trusted_data)

# Bulk validation
items = [MyModel.parse_obj(item) for item in data_list]

# Reuse compiled validators
validator = MyModel.__fields__['field_name'].validator
```

## Monitoring

### Schema Compliance Metrics

```python
# Track validation failures
validation_errors = 0
total_requests = 0

@app.middleware("http")
async def track_validation(request, call_next):
    global validation_errors, total_requests
    total_requests += 1
    try:
        response = await call_next(request)
        return response
    except ValidationError:
        validation_errors += 1
        raise

# Log metrics
print(f"Validation failure rate: {validation_errors/total_requests:.2%}")
```

### OpenAPI Coverage

```bash
# Check OpenAPI spec completeness
python -c "
import yaml
with open('openapi.yaml') as f:
    spec = yaml.safe_load(f)
paths = len(spec.get('paths', {}))
schemas = len(spec.get('components', {}).get('schemas', {}))
print(f'Documented: {paths} paths, {schemas} schemas')
"
```

## Related Capabilities

- **mcp-configuration**: Configuration schema validation
- **mcp-protocol-surface**: MCP protocol implementation
- **inference-serving**: API endpoint validation
- **mcp-security-safeguards**: Input sanitization validation

## References

- [Pydantic Documentation](https://pydantic-docs.helpmanual.io/)
- [OpenAPI Specification](https://swagger.io/specification/)
- [FastAPI Schema Documentation](https://fastapi.tiangolo.com/tutorial/schema-extra-example/)
- [JSON Schema](https://json-schema.org/)

## Safeguards

The MCP schema validation system includes:

1. **Type Safety**: Strong typing with Pydantic prevents type errors
2. **Validation**: All inputs validated before processing
3. **Error Handling**: Detailed validation errors with field-level feedback
4. **Security**: Input sanitization through schema constraints
5. **Versioning**: Schema evolution with backward compatibility checks

## Changelog

- **v1.0**: Initial detection for Pydantic and OpenAPI
- **v1.1**: Added pattern detection for validation decorators
- **v1.2**: Enhanced evidence collection for complex schemas
- **v1.3**: Added safeguards and security validation patterns

---

**Last Updated**: 2024-12-09  
**Maintainer**: Codex MCP Team  
**Capability ID**: mcp-schema-validation
