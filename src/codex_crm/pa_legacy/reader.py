"""Readers for legacy Power Automate export packages."""

from __future__ import annotations

import json
import zipfile
from pathlib import Path
from typing import Any


class PowerAutomateParseError(Exception):
    """Raised when a Power Automate package cannot be parsed."""


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
        raise PowerAutomateParseError(str(exc)) from exc
    return {"manifest": manifest, "flows": flows}


def to_template(package: dict[str, Any]) -> dict[str, Any]:
    """Render a sanitised template representation from a parsed package."""

    connections: list[dict[str, str]] = []
    for flow in package.get("flows", {}).values():
        resources = (flow.get("definition") or {}).get("resources", {})
        for name, resource in resources.items():
            placeholder = f"${{CONN_{name.upper()}}}"
            connections.append(
                {
                    "name": name,
                    "type": resource.get("type", "unknown"),
                    "placeholder": placeholder,
                }
            )

    return {
        "connections": connections,
        "flows": package.get("flows", {}),
        "variables": [],
    }
