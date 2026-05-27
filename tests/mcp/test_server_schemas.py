"""Tests for ``mcp.server.schemas`` models."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from mcp.server.schemas import CallToolParams, ListToolsParams, NegotiateParams


def test_call_tool_params_defaults() -> None:
    params = CallToolParams(tool_id="mcp.search", input={"query": "abc"})
    assert params.tool_id == "mcp.search"
    assert params.input == {"query": "abc"}
    assert params.top_k == 5
    assert params.tenant is None


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
    assert params.top_k == 1


def test_call_tool_params_accepts_custom_values() -> None:
    params = CallToolParams(
        tool_id="mcp.search",
        input={"query": "abc"},
        top_k=12,
        tenant="tenant-a",
    )
    assert params.top_k == 12
    assert params.tenant == "tenant-a"


def test_negotiate_params_defaults() -> None:
    params = NegotiateParams()
    assert params.client_versions is None


def test_negotiate_params_accepts_client_versions() -> None:
    params = NegotiateParams(client_versions={"api": "1.0", "schema": "2.0"})
    assert params.client_versions == {"api": "1.0", "schema": "2.0"}


def test_list_tools_params_defaults_and_override() -> None:
    assert ListToolsParams().include_internal is False
    assert ListToolsParams(include_internal=True).include_internal is True

