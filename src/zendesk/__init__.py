"""Zendesk API integration package."""

from __future__ import annotations

from src.zendesk.api_client import ZendeskAPIClient, ZendeskConfig
from src.zendesk.json_generator import (
    ScriptTemplate,
    TemplateVariable,
    ZendeskJSONGenerator,
)

__all__ = [
    "ZendeskAPIClient",
    "ZendeskConfig",
    "ZendeskJSONGenerator",
    "ScriptTemplate",
    "TemplateVariable",
]
