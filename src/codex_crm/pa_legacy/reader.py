"""
Reader Module

This module provides functionality for reader.

Usage:
    from pa_legacy.reader import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)
"""Readers for legacy Power Automate export packages."""


import json  # noqa: E402
import zipfile  # noqa: E402
from pathlib import Path  # noqa: E402
from typing import Any  # noqa: E402


class PowerAutomateParseError(Exception):
    """Raised when a Power Automate package cannot be parsed."""


class PowerAutomatePackageError(PowerAutomateParseError):
    """Backward-compatible alias maintained for older callers."""


def read_pa_legacy(zip_path: str | Path) -> dict[str, Any]:
    """Read a legacy Power Automate ZIP package."""

    try:
        with zipfile.ZipFile(zip_path) as archive:
            manifest = json.loads(archive.read("manifest.json"))
            flows: dict[str, Any] = {}
            for name in archive.namelist():
                if name.startswith("flows/") and name.endswith(".json"):
                    flows[Path(name).stem] = json.loads(archive.read(name))
    except Exception as exc:
        logger.debug(f"Exception: {exc}")
        raise PowerAutomateParseError(str(exc)) from exc
    return {"manifest": manifest, "flows": flows}


def to_template(package: dict[str, Any]) -> dict[str, Any]:
    """Render a sanitised template representation from a parsed package."""

    # Validate package structure
    if not package.get("flows"):
        raise PowerAutomatePackageError("Package must contain at least one flow")

    # Build connections dictionary from flow connection references
    connections_by_flow: dict[str, list[str]] = {}

    for flow_name, flow in package.get("flows", {}).items():
        flow_connections = []
        # Extract connection references from flow properties
        conn_refs = (flow.get("properties") or {}).get("connectionReferences", {})
        for conn_name in conn_refs.keys():
            flow_connections.append(conn_name)
        connections_by_flow[flow_name] = flow_connections

    # Templatize connection names in flows
    templatized_flows = {}
    for flow_name, flow in package.get("flows", {}).items():
        flow_copy = flow.copy()
        props = flow_copy.get("properties", {})
        if props and "connectionReferences" in props:
            conn_refs = props["connectionReferences"]
            for conn_name, conn_data in conn_refs.items():
                # Replace actual connection name with template variable
                conn_upper = conn_name.upper()
                placeholder = f"{{{{{conn_upper}_CONNECTION}}}}"
                if isinstance(conn_data, dict) and "connectionName" in conn_data:
                    conn_data["connectionName"] = placeholder
        templatized_flows[flow_name] = flow_copy

    return {
        "manifest": package.get("manifest", {}),
        "flows": templatized_flows,
        "connections": connections_by_flow,
    }
