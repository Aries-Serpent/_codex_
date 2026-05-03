"""Zendesk API integration package."""

from __future__ import annotations

from .api_client import ZendeskAPIClient, ZendeskConfig
from .json_generator import (
    PLACEHOLDER_PATTERN,
    ScriptTemplate,
    TemplateVariable,
    ZendeskJSONGenerator,
)

__all__ = [
    "PLACEHOLDER_PATTERN",
    "ScriptTemplate",
    "TemplateVariable",
    "ZendeskAPIClient",
    "ZendeskConfig",
    "ZendeskJSONGenerator",
]
