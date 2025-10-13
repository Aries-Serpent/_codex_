"""Utilities for ingesting legacy Power Automate packages."""

from __future__ import annotations

import json
import zipfile
from pathlib import Path
from typing import Any

__all__ = [
    "PowerAutomatePackageError",
    "read_pa_legacy",
    "to_template",
]


class PowerAutomatePackageError(RuntimeError):
    """Raised when a Power Automate package cannot be interpreted."""


_MANIFEST_FILENAME = "manifest.json"


def _load_json_from_zip(zf: zipfile.ZipFile, member: str) -> dict[str, Any]:
    """Load a JSON document from *member* within the provided ZIP archive."""

    try:
        raw = zf.read(member)
    except KeyError as exc:  # pragma: no cover - defensive guard
        raise PowerAutomatePackageError(f"Missing expected file '{member}' in package") from exc

    try:
        return json.loads(raw.decode("utf-8"))
    except json.JSONDecodeError as exc:  # pragma: no cover - defensive guard
        raise PowerAutomatePackageError(f"File '{member}' is not valid JSON") from exc


def read_pa_legacy(zip_path: str | Path) -> dict[str, Any]:
    """Read a legacy Power Automate export and normalise the structure."""

    path = Path(zip_path)
    if not path.exists():
        raise FileNotFoundError(path)

    try:
        with zipfile.ZipFile(path) as archive:
            manifest = _load_json_from_zip(archive, _MANIFEST_FILENAME)
            flows: dict[str, dict[str, Any]] = {}
            for name in archive.namelist():
                if not name.startswith("flows/") or not name.endswith(".json"):
                    continue
                flow_name = Path(name).stem
                flows[flow_name] = _load_json_from_zip(archive, name)
    except zipfile.BadZipFile as exc:  # pragma: no cover - defensive guard
        raise PowerAutomatePackageError(f"File '{path}' is not a valid ZIP archive") from exc

    if not flows:
        raise PowerAutomatePackageError("No flows were discovered in the package")

    return {"manifest": manifest, "flows": flows}


def _redact_connection_references(flow: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
    """Return a copy of *flow* with connection names redacted."""

    properties = flow.get("properties", {})
    connection_refs = properties.get("connectionReferences", {})
    if not connection_refs:
        return flow, []

    sanitized = json.loads(json.dumps(flow))  # deep copy via JSON round-trip
    sanitized_refs = sanitized.setdefault("properties", {}).setdefault("connectionReferences", {})
    discovered: list[str] = []

    for name, payload in list(sanitized_refs.items()):
        discovered.append(name)
        placeholder = f"{{{{{name.upper()}_CONNECTION}}}}"
        sanitized_refs[name] = {
            "displayName": payload.get("displayName", name),
            "connectionName": placeholder,
            "id": payload.get("id"),
        }

    return sanitized, sorted(discovered)


def to_template(pkg: dict[str, Any]) -> dict[str, Any]:
    """Convert a parsed Power Automate package into a templatized structure."""

    manifest = pkg.get("manifest", {})
    flows = pkg.get("flows", {})
    if not flows:
        raise PowerAutomatePackageError("Package does not contain any flow definitions")

    templated_flows: dict[str, dict[str, Any]] = {}
    connections: dict[str, list[str]] = {}

    for name, flow in flows.items():
        sanitized_flow, discovered = _redact_connection_references(flow)
        templated_flows[name] = sanitized_flow
        if discovered:
            connections[name] = discovered

    return {
        "manifest": manifest,
        "flows": templated_flows,
        "connections": connections,
        "variables": [],
    }
