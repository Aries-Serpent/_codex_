"""Zendesk integration package.

This compatibility package shares the same import contract as the repo-root
`zendesk/` modules while remaining under the editable-install `src/` layout used by
pytest.
"""

from __future__ import annotations

from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
_ROOT_ZENDESK = _ROOT / "zendesk"
if _ROOT_ZENDESK.exists():
    __path__ = [str(Path(__file__).resolve().parent), str(_ROOT_ZENDESK)]

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
