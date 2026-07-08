"""Tests for ``mcp.server.schemas`` models."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from mcp.server.schemas import CallToolParams, ListToolsParams, NegotiateParams


def test_call_tool_params_defaults() -> None:
    params = CallToolParams(tool_id="mcp.search", input={"query": "abc"})
    assert params.tool_id == "mcp.search", "tool_id is not valid"
    assert params.input == {"query": "abc"}, "input is not valid"
    assert params.top_k == 5, "top_k is not valid"
    assert params.tenant is None, "tenant is not valid"


def test_call_tool_params_top_k_validation() -> None:
    for invalid_top_k in (0, -1):
        with pytest.raises(ValidationError):
            CallToolParams(
                tool_id="mcp.search",
                input={"query": "abc"},
                top_k=invalid_top_k,
            )


def test_call_tool_params_top_k_lower_boundary_is_valid() -> None:
    params = CallToolParams(tool_id="mcp.search", input={"query": "abc"}, top_k=1)
    assert params.top_k == 1, "top_k is not valid"


def test_call_tool_params_accepts_custom_values() -> None:
    params = CallToolParams(
        tool_id="mcp.search",
        input={"query": "abc"},
        top_k=12,
        tenant="tenant-a",
    )
    assert params.top_k == 12, "top_k is not valid"
    assert params.tenant == "tenant-a", "tenant is not valid"


def test_negotiate_params_defaults() -> None:
    params = NegotiateParams()
    assert params.client_versions is None, "client_versions is not valid"


def test_negotiate_params_accepts_client_versions() -> None:
    params = NegotiateParams(client_versions={"api": "1.0", "schema": "2.0"})
    assert params.client_versions == {"api": "1.0", "schema": "2.0"}


def test_list_tools_params_defaults_and_override() -> None:
    assert ListToolsParams().include_internal is False, "include_internal is not valid"
    assert ListToolsParams(include_internal=True).include_internal is True, "include_internal is not valid"
