"""Capability Registry — model capability cache with TTL.

Provides a thread-safe, TTL-aware registry of model capability profiles.
Each profile declares which session configuration parameters a model supports,
enabling the ModelNegotiator to gate unsupported parameters before they reach
the session-creation API and cause runtime errors such as:

    Request session.create failed … Model 'claude-haiku-4.5' does not support
    reasoning effort configuration

Phase 2 additions
-----------------
- :class:`ToolSurfaceCategory` — enum for the four MCP-backed tool surfaces.
- :class:`ToolSurfaceProfile` — versioned capability descriptor per surface.
- :data:`CAPABILITY_SCHEMA_VERSION` — current schema version string.
- :func:`get_tool_surface_registry` — returns the built-in tool surface catalog.

Usage::

    registry = CapabilityRegistry()
    profile = registry.get("claude-haiku-4.5")
    if not profile.supports_reasoning_effort:
        config.pop("reasoning_effort", None)

    surfaces = get_tool_surface_registry()
    gh = surfaces[ToolSurfaceCategory.GITHUB_MCP]
    print(gh.tool_count)  # 35
"""

from __future__ import annotations

import logging
import threading
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Schema version (bump when breaking changes are made to capability profiles)
# ---------------------------------------------------------------------------

CAPABILITY_SCHEMA_VERSION: str = "2.0.0"

# ---------------------------------------------------------------------------
# Tool surface category (Phase 2C — MCP capability matrix parity)
# ---------------------------------------------------------------------------


class ToolSurfaceCategory(str, Enum):
    """Enumeration of the four MCP-backed tool surfaces available in the runtime."""

    GITHUB_MCP = "github_mcp"
    PLAYWRIGHT = "playwright"
    WEB_SEARCH = "web_search"
    SHELL = "shell"


@dataclass
class ToolSurfaceProfile:
    """Versioned capability descriptor for a single MCP tool surface.

    Attributes
    ----------
    category:
        Which surface this profile describes.
    tool_count:
        Number of individual tools exposed by this surface.
    schema_version:
        Schema version this profile was built against.
    read_only:
        True if all tools in this surface are non-mutating.
    requires_auth:
        True if the surface needs external credentials (e.g. a GitHub token).
    network_access:
        True if the surface makes outbound network calls.
    shell_access:
        True if the surface can run local OS commands.
    policy_gated:
        True if a policy check is required before invoking any tool.
    available_tools:
        List of canonical tool-name strings exposed by this surface.
    notes:
        Free-form notes about this surface.
    """

    category: ToolSurfaceCategory
    tool_count: int
    schema_version: str = CAPABILITY_SCHEMA_VERSION
    read_only: bool = True
    requires_auth: bool = False
    network_access: bool = False
    shell_access: bool = False
    policy_gated: bool = False
    available_tools: List[str] = field(default_factory=list)
    notes: str = ""

    def is_compatible_with(self, other_version: str) -> bool:
        """Return True if this profile is compatible with *other_version*.

        Uses SemVer major-version compatibility: same major → compatible.
        """
        try:
            our_major = int(self.schema_version.split(".")[0])
            other_major = int(other_version.split(".")[0])
            return our_major == other_major
        except (ValueError, IndexError):
            return False


# Built-in tool surface registry (aligned with MCP Capability Matrix).
def _build_tool_surface_registry() -> Dict[ToolSurfaceCategory, ToolSurfaceProfile]:
    """Construct the canonical tool surface registry from documented capabilities."""
    return {
        ToolSurfaceCategory.GITHUB_MCP: ToolSurfaceProfile(
            category=ToolSurfaceCategory.GITHUB_MCP,
            tool_count=35,
            read_only=True,
            requires_auth=True,
            network_access=True,
            shell_access=False,
            policy_gated=False,
            available_tools=[
                # Repository
                "get_file_contents",
                "search_code",
                "search_repositories",
                "list_commits",
                "get_commit",
                "list_branches",
                "list_tags",
                "get_tag",
                "list_repository_collaborators",
                # Pull requests
                "list_pull_requests",
                "search_pull_requests",
                "pull_request_read",
                "get_job_logs",
                # Issues
                "list_issues",
                "search_issues",
                "issue_read",
                "list_label",
                "get_label",
                "list_issue_types",
                "list_issue_fields",
                # CI/Actions
                "actions_get",
                "actions_list",
                # Security
                "list_code_scanning_alerts",
                "get_code_scanning_alert",
                "list_secret_scanning_alerts",
                "get_secret_scanning_alert",
                # Releases
                "list_releases",
                "get_latest_release",
                "get_release_by_tag",
                # Discussions
                "list_discussions",
                "get_discussion",
                "get_discussion_comments",
                "list_discussion_categories",
                # Users/search
                "search_users",
                "search_commits",
            ],
            notes="35 read-only GitHub MCP tools as documented on 2026-08-01",
        ),
        ToolSurfaceCategory.PLAYWRIGHT: ToolSurfaceProfile(
            category=ToolSurfaceCategory.PLAYWRIGHT,
            tool_count=21,
            read_only=False,  # browser can fill forms / click
            requires_auth=False,
            network_access=True,
            shell_access=False,
            policy_gated=False,
            available_tools=[
                "playwright-browser_click",
                "playwright-browser_close",
                "playwright-browser_console_messages",
                "playwright-browser_drag",
                "playwright-browser_evaluate",
                "playwright-browser_file_upload",
                "playwright-browser_fill_form",
                "playwright-browser_handle_dialog",
                "playwright-browser_hover",
                "playwright-browser_install",
                "playwright-browser_navigate",
                "playwright-browser_navigate_back",
                "playwright-browser_network_requests",
                "playwright-browser_press_key",
                "playwright-browser_resize",
                "playwright-browser_select_option",
                "playwright-browser_snapshot",
                "playwright-browser_tabs",
                "playwright-browser_take_screenshot",
                "playwright-browser_type",
                "playwright-browser_wait_for",
            ],
            notes="21 Playwright MCP tools as documented on 2026-08-01",
        ),
        ToolSurfaceCategory.WEB_SEARCH: ToolSurfaceProfile(
            category=ToolSurfaceCategory.WEB_SEARCH,
            tool_count=1,
            read_only=True,
            requires_auth=False,
            network_access=True,
            shell_access=False,
            policy_gated=False,
            available_tools=["web_search"],
            notes="Standalone web_search tool (AI-powered search with citations)",
        ),
        ToolSurfaceCategory.SHELL: ToolSurfaceProfile(
            category=ToolSurfaceCategory.SHELL,
            tool_count=1,
            read_only=False,
            requires_auth=False,
            network_access=True,
            shell_access=True,
            policy_gated=True,  # Must pass ShellPolicy.gate() before execution
            available_tools=["bash"],
            notes=(
                "Local shell execution — policy-gated via ShellPolicy. "
                "Requires COGNITIVE_BRAIN_ALLOW_SHELL=true."
            ),
        ),
    }


_TOOL_SURFACE_REGISTRY: Optional[Dict[ToolSurfaceCategory, ToolSurfaceProfile]] = None
_surface_lock = threading.Lock()


def get_tool_surface_registry() -> Dict[ToolSurfaceCategory, ToolSurfaceProfile]:
    """Return the canonical (cached) tool surface registry."""
    global _TOOL_SURFACE_REGISTRY
    with _surface_lock:
        if _TOOL_SURFACE_REGISTRY is None:
            _TOOL_SURFACE_REGISTRY = _build_tool_surface_registry()
    return _TOOL_SURFACE_REGISTRY


def check_capability_schema_version(required_version: str) -> bool:
    """Return True if the current schema is compatible with *required_version*."""
    try:
        current_major = int(CAPABILITY_SCHEMA_VERSION.split(".")[0])
        required_major = int(required_version.split(".")[0])
        return current_major == required_major
    except (ValueError, IndexError):
        return False


# Known models that support extended-thinking / reasoning-effort config.
# Populated from public Anthropic/OpenAI documentation; update as APIs evolve.
_REASONING_EFFORT_SUPPORTED: frozenset[str] = frozenset(
    {
        "claude-opus-4.5",
        "claude-opus-4.6",
        "claude-opus-4.7",
        "claude-opus-4.8",
        "claude-opus-4.8-fast",
        "claude-opus-5",
        "claude-sonnet-4.5",
        "claude-sonnet-4.6",
        "claude-sonnet-5",
        "claude-fable-5",
        "o1",
        "o1-mini",
        "o1-preview",
        "o3",
        "o3-mini",
        "o4-mini",
        "gemini-3.1-pro-preview",
        "gpt-5.3-codex",
        "gpt-5.4",
        "gpt-5.4-mini",
        "gpt-5.5",
        "gpt-5.6-luna",
        "gpt-5.6-sol",
        "gpt-5.6-terra",
        "grok-4.5",
        "kimi-k2.7-code",
    }
)

# Models that are lightweight / fast and may lack extended reasoning.
_LIGHTWEIGHT_MODELS: frozenset[str] = frozenset(
    {
        "claude-haiku-4.5",
        "gpt-5-mini",
        "gemini-3.5-flash",
        "gemini-3.6-flash",
        "mai-code-1-flash-picker",
    }
)


@dataclass
class ModelCapabilityProfile:
    """Declared capability profile for a single model identifier."""

    model_id: str
    supports_reasoning_effort: bool = False
    supports_streaming: bool = True
    supports_tools: bool = True
    supports_vision: bool = False
    is_lightweight: bool = False
    max_output_tokens: int = 8192
    # Additional arbitrary capability flags for forward-compatibility.
    extra_flags: Dict[str, bool] = field(default_factory=dict)

    def supports(self, capability: str) -> bool:
        """Return True if this profile declares *capability* as supported."""
        if capability == "reasoning_effort":
            return self.supports_reasoning_effort
        if capability == "streaming":
            return self.supports_streaming
        if capability == "tools":
            return self.supports_tools
        if capability == "vision":
            return self.supports_vision
        return self.extra_flags.get(capability, False)


def _build_default_profile(model_id: str) -> ModelCapabilityProfile:
    """Construct a best-effort capability profile from the known-models tables."""
    reasoning = model_id in _REASONING_EFFORT_SUPPORTED
    lightweight = model_id in _LIGHTWEIGHT_MODELS
    return ModelCapabilityProfile(
        model_id=model_id,
        supports_reasoning_effort=reasoning,
        is_lightweight=lightweight,
    )


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------


class CapabilityRegistry:
    """Thread-safe, TTL-aware cache of :class:`ModelCapabilityProfile` objects.

    On a cache miss the registry synthesises a default profile from the
    built-in known-models tables.  Externally obtained profiles (e.g., from a
    live ``models.list`` API call) can be injected via :meth:`register`.

    Parameters
    ----------
    ttl_seconds:
        How long a cached profile is considered fresh.  Defaults to 3600 s.
    """

    def __init__(self, ttl_seconds: float = 3600.0) -> None:
        self._ttl = ttl_seconds
        self._lock = threading.Lock()
        # Maps model_id → (profile, expiry_epoch)
        self._cache: Dict[str, tuple[ModelCapabilityProfile, float]] = {}

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get(self, model_id: str) -> ModelCapabilityProfile:
        """Return the :class:`ModelCapabilityProfile` for *model_id*.

        Returns a cached profile if still fresh, otherwise rebuilds from
        the built-in tables and stores it.
        """
        with self._lock:
            entry = self._cache.get(model_id)
            if entry is not None:
                profile, expiry = entry
                if time.monotonic() < expiry:
                    return profile
                logger.debug("Capability cache expired for model=%s; rebuilding", model_id)

            profile = _build_default_profile(model_id)
            self._cache[model_id] = (profile, time.monotonic() + self._ttl)
            logger.debug(
                "Capability profile built: model=%s reasoning_effort=%s",
                model_id,
                profile.supports_reasoning_effort,
            )
            return profile

    def register(self, profile: ModelCapabilityProfile) -> None:
        """Inject or replace a profile in the cache, resetting its TTL."""
        with self._lock:
            self._cache[profile.model_id] = (profile, time.monotonic() + self._ttl)
            logger.info("Registered capability profile for model=%s", profile.model_id)

    def invalidate(self, model_id: Optional[str] = None) -> None:
        """Evict *model_id* from the cache (or clear all entries if None)."""
        with self._lock:
            if model_id is None:
                self._cache.clear()
                logger.debug("Capability cache cleared")
            else:
                self._cache.pop(model_id, None)
                logger.debug("Capability cache invalidated for model=%s", model_id)

    def all_known(self) -> Dict[str, ModelCapabilityProfile]:
        """Return a snapshot of all currently cached profiles."""
        with self._lock:
            return {mid: p for mid, (p, _) in self._cache.items()}


# ---------------------------------------------------------------------------
# Module-level default registry (singleton)
# ---------------------------------------------------------------------------

_default_registry: Optional[CapabilityRegistry] = None
_registry_lock = threading.Lock()


def get_default_registry() -> CapabilityRegistry:
    """Return the process-level default :class:`CapabilityRegistry`."""
    global _default_registry
    with _registry_lock:
        if _default_registry is None:
            _default_registry = CapabilityRegistry()
    return _default_registry
