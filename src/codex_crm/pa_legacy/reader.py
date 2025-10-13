from __future__ import annotations

import json
import pathlib
import zipfile
from typing import Any


class PowerAutomateParseError(Exception):
    """Raised when a Power Automate legacy package cannot be parsed."""


Package = dict[str, Any]


def read_pa_legacy(zip_path: str) -> Package:
    """Read a legacy Power Automate ZIP export into a Python structure."""

    try:
        with zipfile.ZipFile(zip_path) as archive:
            manifest = json.loads(archive.read("manifest.json"))
            flows: dict[str, Any] = {}
            for name in archive.namelist():
                path = pathlib.Path(name)
                if path.suffix == ".json" and path.parts[0] == "flows":
                    flows[path.stem] = json.loads(archive.read(name))
    except Exception as exc:  # pragma: no cover - wrapped for context
        raise PowerAutomateParseError(str(exc)) from exc

    return {"manifest": manifest, "flows": flows}


def to_template(package: Package) -> Package:
    """Redact secrets and emit placeholders for connections in the package."""

    connections = []
    for flow in package.get("flows", {}).values():
        definition = flow.get("definition") or {}
        resources = definition.get("resources", {})
        for name, resource in resources.items():
            connections.append(
                {
                    "name": name,
                    "type": resource.get("type"),
                    "placeholder": f"${{CONN_{name.upper()}}}",
                }
            )

    return {
        "manifest": package.get("manifest", {}),
        "flows": package.get("flows", {}),
        "connections": connections,
        "variables": [],
    }
