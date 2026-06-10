import pytest
from pydantic import ValidationError
from mcp.server.schemas import CallToolParams, NegotiateParams, ListToolsParams

def test_call_tool_params_valid():
    params = CallToolParams(tool_id="tool1", input={"key": "value"})
    assert params.tool_id == "tool1"
    assert params.input == {"key": "value"}
    assert params.top_k == 5
    assert params.tenant is None

def test_call_tool_params_invalid():
    with pytest.raises(ValidationError):
        CallToolParams(tool_id="tool1")  # missing input

def test_negotiate_params():
    params = NegotiateParams()
    assert params.client_versions is None

def test_list_tools_params():
    params = ListToolsParams()
    assert params.include_internal is False
