from __future__ import annotations

import json
import os
from typing import Any, Callable, Dict, List, Optional

from .errors import ValidationError
from .safeguards import (
    compute_secure_checksum,
    enforce_dry_run_support,
    ensure_offline_mode,
    fingerprint_metadata,
    require_confirmation,
)


class MCPToolRegistry:
    """Registry for MCP tools with checksum-backed safeguard metadata."""

    def __init__(self, *, offline: Optional[bool] = None) -> None:
        self._tools: Dict[str, Dict[str, Any]] = {}
        self._offline_mode = (
            offline
            if offline is not None
            else os.environ.get("MCP_OFFLINE", "false").lower() in {"1", "true"}
        )

    def register_tool(
        self,
        name: str,
        handler: Callable[..., Any],
        schema: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Register a tool with checksum, confirm, dry_run, and offline safeguards."""

        stored_metadata: Dict[str, Any] = metadata.copy() if metadata else {}
        safeguards = stored_metadata.setdefault("safeguards", {})
        safeguards.setdefault("requires_confirmation", stored_metadata.get("confirm", False))
        safeguards.setdefault("supports_dry_run", stored_metadata.get("dry_run", True))
        ensure_offline_mode(safeguards)
        stored_metadata.setdefault("confirm", safeguards["requires_confirmation"])
        stored_metadata.setdefault("dry_run", False)

        signature_payload = json.dumps(
            {
                "name": name,
                "schema": schema or {},
                "metadata": stored_metadata,
            },
            sort_keys=True,
            default=str,
        )
        signature_checksum = compute_secure_checksum(signature_payload)
        stored_metadata.setdefault("checksum", signature_checksum)
        stored_metadata.setdefault("sha256", signature_checksum)
        stored_metadata.setdefault("signature", signature_checksum)

        self._tools[name] = {
            "handler": handler,
            "schema": schema,
            "metadata": stored_metadata,
        }

    def list_tools(self) -> List[Dict[str, Any]]:
        """Return tool metadata excluding raw handler implementations."""

        tools_info = []
        for name, info in self._tools.items():
            data = {"name": name}
            if info.get("schema"):
                data["schema"] = info["schema"]
            if info.get("metadata"):
                data["metadata"] = info["metadata"]
            tools_info.append(data)
        return tools_info

    def get_tool(self, name: str) -> Optional[Callable[..., Any]]:
        """Return the handler for a given tool by name."""

        entry = self._tools.get(name)
        if entry:
            return entry["handler"]
        return None

    def get_metadata(self, name: str) -> Dict[str, Any]:
        """Return stored metadata for a tool, raising ValidationError if missing."""

        entry = self._tools.get(name)
        if not entry:
            raise ValidationError(f"Unknown tool: {name}")
        return entry.get("metadata", {})

    def enforce_safeguards(self, name: str, params: Dict[str, Any]) -> None:
        """Ensure confirm/dry_run semantics are honored before tool execution."""

        metadata = self.get_metadata(name)
        safeguards = metadata.get("safeguards", {})
        confirm_flag = bool(params.get("confirm", False))
        dry_run_flag = bool(params.get("dry_run", metadata.get("dry_run", False)))

        if safeguards.get("requires_confirmation"):
            require_confirmation(confirm_flag, name)
        enforce_dry_run_support(safeguards.get("supports_dry_run", True), dry_run_flag, name)

    def offline_mode(self) -> bool:
        """Return whether the registry is currently in offline mode."""

        return self._offline_mode
