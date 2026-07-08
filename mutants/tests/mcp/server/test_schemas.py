import pytest
from pydantic import ValidationError

from mcp.server.schemas import CallToolParams, ListToolsParams, NegotiateParams


def test_call_tool_params_valid():
    params = CallToolParams(tool_id="tool1", input={"key": "value"})
    assert params.tool_id == "tool1", "tool_id is not valid"
    assert params.input == {"key": "value"}, "Value must be initialized"
    assert params.top_k == 5, "top_k is not valid"
    assert params.tenant is None, "tenant is not valid"


def test_call_tool_params_invalid():
    with pytest.raises(ValidationError):
        CallToolParams(tool_id="tool1")  # missing input


def test_negotiate_params():
    params = NegotiateParams()
    assert params.client_versions is None, "client_versions is not valid"


def test_list_tools_params():
    params = ListToolsParams()
    assert params.include_internal is False, "include_internal is not valid"
