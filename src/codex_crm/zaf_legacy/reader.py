"""Readers and scaffold helpers for legacy Zendesk App Framework packages."""

from __future__ import annotations

import json
import zipfile
from pathlib import Path
from typing import Any, cast


class ZAFParseError(Exception):
    """Raised when a Zendesk App Framework package cannot be parsed."""


def read_zaf(zip_path: str | Path) -> dict[str, object]:
    """Read a ZAF ZIP package and return manifest/files contents."""

    try:
        with zipfile.ZipFile(zip_path) as archive:
            manifest = json.loads(archive.read("manifest.json"))
            files = {
                name: archive.read(name).decode("utf-8", "ignore")
                for name in archive.namelist()
                if not name.endswith("/")
            }
    except Exception as exc:
        raise ZAFParseError(str(exc)) from exc
    return {"manifest": manifest, "files": files}


def scaffold_template(zaf: dict[str, object], out_dir: str | Path) -> None:
    """Normalise a legacy ZAF package into a reusable scaffold."""

    output = Path(out_dir)
    (output / "src").mkdir(parents=True, exist_ok=True)

    raw_manifest = cast(dict[str, object], zaf.get("manifest", {}))
    manifest = _normalise_manifest(raw_manifest)
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    files = cast(dict[str, str], zaf.get("files", {}))
    for path, content in files.items():
        if path.endswith((".js", ".css", ".hbs", ".json")) and "manifest.json" not in path:
            destination = output / "src" / Path(path).name
            destination.write_text(content, encoding="utf-8")


def _normalise_manifest(manifest: dict[str, object]) -> dict[str, object]:
    name = manifest.get("name") or "codex_app_template"
    raw_parameters = manifest.get("parameters", [])

    parameters: list[dict[str, Any]] = []
    if isinstance(raw_parameters, list):
        for entry in raw_parameters:
            if isinstance(entry, dict):
                parameters.append(dict(entry))

    if not any(param.get("name") == "API_BASE" for param in parameters):
        parameters.append({"name": "API_BASE", "type": "text", "required": False})

    manifest["name"] = name
    manifest["parameters"] = parameters
    return manifest
