"""Tests for ToolSurfaceCategory / ToolSurfaceProfile capability registry (Phase 2C).

Covers:
- Unit: all four tool surface categories are registered
- Unit: GitHub MCP has 35 tools and is read-only
- Unit: Playwright has 21 tools
- Unit: web_search has 1 tool
- Unit: shell is policy-gated
- Unit: schema version compatibility checks
- Unit: ToolSurfaceProfile.is_compatible_with
- Unit: check_capability_schema_version
- Regression: CAPABILITY_SCHEMA_VERSION format is semver
"""

from __future__ import annotations

import re

from src.codex.cognitive_brain.capability_registry import (
    CAPABILITY_SCHEMA_VERSION,
    ToolSurfaceCategory,
    ToolSurfaceProfile,
    check_capability_schema_version,
    get_tool_surface_registry,
)

# ---------------------------------------------------------------------------
# Registry presence tests
# ---------------------------------------------------------------------------


class TestToolSurfaceRegistry:
    def test_all_four_categories_present(self) -> None:
        registry = get_tool_surface_registry()
        for cat in ToolSurfaceCategory:
            assert cat in registry, f"Missing category: {cat}"

    def test_registry_cached_singleton(self) -> None:
        r1 = get_tool_surface_registry()
        r2 = get_tool_surface_registry()
        assert r1 is r2

    def test_github_mcp_tool_count(self) -> None:
        registry = get_tool_surface_registry()
        gh = registry[ToolSurfaceCategory.GITHUB_MCP]
        assert gh.tool_count == 35

    def test_playwright_tool_count(self) -> None:
        registry = get_tool_surface_registry()
        pw = registry[ToolSurfaceCategory.PLAYWRIGHT]
        assert pw.tool_count == 21

    def test_web_search_tool_count(self) -> None:
        registry = get_tool_surface_registry()
        ws = registry[ToolSurfaceCategory.WEB_SEARCH]
        assert ws.tool_count == 1

    def test_shell_tool_count(self) -> None:
        registry = get_tool_surface_registry()
        sh = registry[ToolSurfaceCategory.SHELL]
        assert sh.tool_count == 1


# ---------------------------------------------------------------------------
# Capability attribute tests
# ---------------------------------------------------------------------------


class TestCapabilityAttributes:
    def test_github_mcp_is_read_only(self) -> None:
        registry = get_tool_surface_registry()
        gh = registry[ToolSurfaceCategory.GITHUB_MCP]
        assert gh.read_only is True

    def test_github_mcp_requires_auth(self) -> None:
        registry = get_tool_surface_registry()
        gh = registry[ToolSurfaceCategory.GITHUB_MCP]
        assert gh.requires_auth is True

    def test_github_mcp_network_access(self) -> None:
        registry = get_tool_surface_registry()
        gh = registry[ToolSurfaceCategory.GITHUB_MCP]
        assert gh.network_access is True

    def test_github_mcp_not_shell_access(self) -> None:
        registry = get_tool_surface_registry()
        gh = registry[ToolSurfaceCategory.GITHUB_MCP]
        assert gh.shell_access is False

    def test_playwright_not_read_only(self) -> None:
        registry = get_tool_surface_registry()
        pw = registry[ToolSurfaceCategory.PLAYWRIGHT]
        assert pw.read_only is False

    def test_shell_is_policy_gated(self) -> None:
        registry = get_tool_surface_registry()
        sh = registry[ToolSurfaceCategory.SHELL]
        assert sh.policy_gated is True

    def test_shell_has_shell_access(self) -> None:
        registry = get_tool_surface_registry()
        sh = registry[ToolSurfaceCategory.SHELL]
        assert sh.shell_access is True

    def test_web_search_not_policy_gated(self) -> None:
        registry = get_tool_surface_registry()
        ws = registry[ToolSurfaceCategory.WEB_SEARCH]
        assert ws.policy_gated is False


# ---------------------------------------------------------------------------
# Available tools lists
# ---------------------------------------------------------------------------


class TestAvailableToolsList:
    def test_github_mcp_available_tools_non_empty(self) -> None:
        registry = get_tool_surface_registry()
        gh = registry[ToolSurfaceCategory.GITHUB_MCP]
        assert len(gh.available_tools) > 0

    def test_playwright_available_tools_match_count(self) -> None:
        registry = get_tool_surface_registry()
        pw = registry[ToolSurfaceCategory.PLAYWRIGHT]
        assert len(pw.available_tools) == pw.tool_count

    def test_web_search_in_available_tools(self) -> None:
        registry = get_tool_surface_registry()
        ws = registry[ToolSurfaceCategory.WEB_SEARCH]
        assert "web_search" in ws.available_tools

    def test_bash_in_shell_available_tools(self) -> None:
        registry = get_tool_surface_registry()
        sh = registry[ToolSurfaceCategory.SHELL]
        assert "bash" in sh.available_tools


# ---------------------------------------------------------------------------
# Schema version tests
# ---------------------------------------------------------------------------


class TestCapabilitySchemaVersion:
    _SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+$")

    def test_schema_version_is_semver(self) -> None:
        assert self._SEMVER_RE.match(
            CAPABILITY_SCHEMA_VERSION
        ), f"CAPABILITY_SCHEMA_VERSION '{CAPABILITY_SCHEMA_VERSION}' is not semver"

    def test_registry_profiles_have_schema_version(self) -> None:
        registry = get_tool_surface_registry()
        for cat, profile in registry.items():
            assert profile.schema_version, f"{cat} profile missing schema_version"
            assert self._SEMVER_RE.match(
                profile.schema_version
            ), f"{cat} schema_version '{profile.schema_version}' is not semver"

    def test_check_capability_schema_version_same_major(self) -> None:
        assert check_capability_schema_version(CAPABILITY_SCHEMA_VERSION) is True

    def test_check_capability_schema_version_different_major(self) -> None:
        # Major version 99 must be incompatible with current (2.x.x).
        assert check_capability_schema_version("99.0.0") is False

    def test_check_capability_schema_version_same_major_different_minor(self) -> None:
        # Same major, different minor → compatible.
        major = CAPABILITY_SCHEMA_VERSION.split(".")[0]
        assert check_capability_schema_version(f"{major}.999.0") is True

    def test_check_capability_schema_version_invalid_string(self) -> None:
        assert check_capability_schema_version("not-a-version") is False


# ---------------------------------------------------------------------------
# ToolSurfaceProfile.is_compatible_with
# ---------------------------------------------------------------------------


class TestToolSurfaceProfileCompatibility:
    def test_compatible_same_major(self) -> None:
        profile = ToolSurfaceProfile(
            category=ToolSurfaceCategory.GITHUB_MCP,
            tool_count=35,
            schema_version="2.0.0",
        )
        assert profile.is_compatible_with("2.5.3") is True

    def test_incompatible_different_major(self) -> None:
        profile = ToolSurfaceProfile(
            category=ToolSurfaceCategory.GITHUB_MCP,
            tool_count=35,
            schema_version="2.0.0",
        )
        assert profile.is_compatible_with("3.0.0") is False

    def test_incompatible_invalid_version(self) -> None:
        profile = ToolSurfaceProfile(
            category=ToolSurfaceCategory.PLAYWRIGHT,
            tool_count=21,
            schema_version="2.0.0",
        )
        assert profile.is_compatible_with("invalid") is False


# ---------------------------------------------------------------------------
# ToolSurfaceCategory enum values
# ---------------------------------------------------------------------------


class TestToolSurfaceCategoryEnum:
    def test_category_values(self) -> None:
        assert ToolSurfaceCategory.GITHUB_MCP.value == "github_mcp"
        assert ToolSurfaceCategory.PLAYWRIGHT.value == "playwright"
        assert ToolSurfaceCategory.WEB_SEARCH.value == "web_search"
        assert ToolSurfaceCategory.SHELL.value == "shell"

    def test_four_categories_defined(self) -> None:
        assert len(ToolSurfaceCategory) == 4
