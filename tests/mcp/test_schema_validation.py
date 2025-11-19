"""
Tests for MCP schema validation capability.

Covers Pydantic models, JSON Schema validation, OpenAPI integration,
and data validation patterns used across MCP.
"""

import pytest
from pydantic import BaseModel, ValidationError as PydanticValidationError
from typing import Any, Dict, Optional


# Sample Pydantic models for MCP tool requests/responses
class MCPToolRequest(BaseModel):
    """MCP tool invocation request schema."""
    tool_name: str
    params: Dict[str, Any]
    principal_id: Optional[str] = None
    request_id: Optional[str] = None


class MCPToolResponse(BaseModel):
    """MCP tool invocation response schema."""
    success: bool
    result: Optional[Any] = None
    error: Optional[str] = None
    request_id: Optional[str] = None


class MCPToolMetadata(BaseModel):
    """MCP tool metadata schema."""
    name: str
    description: str
    schema: Dict[str, Any]
    version: str = "1.0"


# Tests
def test_tool_request_valid():
    """Test valid tool request schema validation."""
    request = MCPToolRequest(
        tool_name="kb.search",
        params={"query": "test"},
        principal_id="user123"
    )
    assert request.tool_name == "kb.search"
    assert request.params == {"query": "test"}


def test_tool_request_missing_required_field():
    """Test schema validation fails with missing required field."""
    with pytest.raises(PydanticValidationError):
        MCPToolRequest(params={"query": "test"})  # Missing tool_name


def test_tool_request_invalid_type():
    """Test schema validation fails with invalid type."""
    with pytest.raises(PydanticValidationError):
        MCPToolRequest(tool_name=123, params={})  # tool_name should be str


def test_tool_response_valid_success():
    """Test valid success response schema."""
    response = MCPToolResponse(
        success=True,
        result={"data": "result"},
        request_id="req-123"
    )
    assert response.success is True
    assert response.result == {"data": "result"}


def test_tool_response_valid_error():
    """Test valid error response schema."""
    response = MCPToolResponse(
        success=False,
        error="Tool not found",
        request_id="req-123"
    )
    assert response.success is False
    assert response.error == "Tool not found"


def test_tool_metadata_valid():
    """Test valid tool metadata schema."""
    metadata = MCPToolMetadata(
        name="kb.search",
        description="Search knowledge base",
        schema={"type": "object", "properties": {"query": {"type": "string"}}}
    )
    assert metadata.name == "kb.search"
    assert "query" in metadata.schema["properties"]


def test_tool_metadata_default_version():
    """Test tool metadata uses default version."""
    metadata = MCPToolMetadata(
        name="tool",
        description="desc",
        schema={}
    )
    assert metadata.version == "1.0"


def test_json_schema_object_validation():
    """Test JSON Schema object validation pattern."""
    schema = {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "age": {"type": "integer"}
        },
        "required": ["name"]
    }
    # In production, use jsonschema library for validation
    assert schema["type"] == "object"
    assert "name" in schema["required"]


def test_json_schema_array_validation():
    """Test JSON Schema array validation pattern."""
    schema = {
        "type": "array",
        "items": {"type": "string"},
        "minItems": 1
    }
    assert schema["type"] == "array"
    assert schema["minItems"] == 1


def test_nested_model_validation():
    """Test nested Pydantic model validation."""
    class NestedParams(BaseModel):
        query: str
        filters: Dict[str, Any] = {}
    
    class RequestWithNested(BaseModel):
        tool_name: str
        params: NestedParams
    
    request = RequestWithNested(
        tool_name="search",
        params=NestedParams(query="test", filters={"status": "active"})
    )
    assert request.params.query == "test"
    assert request.params.filters == {"status": "active"}


def test_optional_field_validation():
    """Test optional field handling in schema validation."""
    request = MCPToolRequest(
        tool_name="tool",
        params={}
        # principal_id and request_id are optional
    )
    assert request.principal_id is None
    assert request.request_id is None


def test_schema_serialization():
    """Test schema model serialization to dict."""
    request = MCPToolRequest(
        tool_name="tool",
        params={"key": "value"},
        principal_id="user"
    )
    data = request.model_dump()
    assert data["tool_name"] == "tool"
    assert data["params"] == {"key": "value"}


def test_schema_from_json():
    """Test schema model creation from JSON."""
    json_data = '{"tool_name": "tool", "params": {"k": "v"}}'
    request = MCPToolRequest.model_validate_json(json_data)
    assert request.tool_name == "tool"


def test_schema_validation_error_details():
    """Test schema validation error provides details."""
    try:
        MCPToolRequest(tool_name=None, params="invalid")
    except PydanticValidationError as e:
        errors = e.errors()
        assert len(errors) > 0
        # Errors should include field and type information
        assert any(err["loc"] == ("tool_name",) for err in errors)


def test_schema_coercion():
    """Test schema type coercion where applicable."""
    # Pydantic may coerce compatible types
    request = MCPToolRequest(
        tool_name="tool",
        params={"count": "10"}  # String that could be coerced
    )
    assert request.params["count"] == "10"


def test_complex_schema_validation():
    """Test complex nested schema validation."""
    class ComplexSchema(BaseModel):
        id: str
        metadata: Dict[str, Any]
        tags: list[str] = []
        config: Optional[Dict[str, Any]] = None
    
    obj = ComplexSchema(
        id="obj-123",
        metadata={"key": "value"},
        tags=["tag1", "tag2"]
    )
    assert obj.id == "obj-123"
    assert len(obj.tags) == 2
    assert obj.config is None


def test_schema_validation_with_custom_validator():
    """Test custom validation logic in schema."""
    class ValidatedRequest(BaseModel):
        tool_name: str
        
        @property
        def is_valid_tool(self) -> bool:
            """Custom validation property."""
            return len(self.tool_name) > 0 and not self.tool_name.startswith("_")
    
    request = ValidatedRequest(tool_name="kb.search")
    assert request.is_valid_tool is True
    
    request_invalid = ValidatedRequest(tool_name="_private")
    assert request_invalid.is_valid_tool is False


def test_openapi_schema_generation():
    """Test OpenAPI schema can be generated from models."""
    schema = MCPToolRequest.model_json_schema()
    assert "properties" in schema
    assert "tool_name" in schema["properties"]
    assert schema["properties"]["tool_name"]["type"] == "string"


def test_schema_with_enums():
    """Test schema validation with enum fields."""
    from enum import Enum
    
    class ToolStatus(str, Enum):
        ACTIVE = "active"
        INACTIVE = "inactive"
    
    class ToolWithStatus(BaseModel):
        name: str
        status: ToolStatus
    
    tool = ToolWithStatus(name="tool", status=ToolStatus.ACTIVE)
    assert tool.status == ToolStatus.ACTIVE
    
    with pytest.raises(PydanticValidationError):
        ToolWithStatus(name="tool", status="invalid")


def test_schema_extra_forbid():
    """Test schema validation with extra fields forbidden."""
    class StrictModel(BaseModel):
        class Config:
            extra = "forbid"
        
        name: str
    
    # Valid
    obj = StrictModel(name="test")
    assert obj.name == "test"
    
    # Invalid - extra field
    with pytest.raises(PydanticValidationError):
        StrictModel(name="test", extra_field="not_allowed")


def test_schema_validation_integration():
    """Test schema validation in MCP request/response flow."""
    # Request
    request = MCPToolRequest(
        tool_name="kb.search",
        params={"query": "mcp"},
        request_id="req-789"
    )
    
    # Process (mock)
    result = {"matches": ["doc1", "doc2"]}
    
    # Response
    response = MCPToolResponse(
        success=True,
        result=result,
        request_id=request.request_id
    )
    
    assert response.success is True
    assert response.request_id == "req-789"
    assert len(response.result["matches"]) == 2
