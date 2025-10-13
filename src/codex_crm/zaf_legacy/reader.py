"""Utilities for working with legacy Zendesk App Framework (ZAF) bundles."""

from __future__ import annotations

import json
import zipfile
from pathlib import Path
from typing import Any

__all__ = [
    "ZendeskAppPackageError",
    "read_zaf",
    "scaffold_template",
]


class ZendeskAppPackageError(RuntimeError):
    """Raised when a Zendesk App Framework bundle is malformed."""


_MANIFEST_FILENAME = "manifest.json"
_SCAFFOLD_FOLDERS = ("assets", "src", "translations")


def _decode_if_text(payload: bytes) -> str | bytes:
    """Attempt to decode *payload* as UTF-8, falling back to bytes."""

    try:
        return payload.decode("utf-8")
    except UnicodeDecodeError:  # pragma: no cover - depends on binary test data
        return payload


def read_zaf(zip_path: str | Path) -> dict[str, Any]:
    """Read the ZIP file at *zip_path* and return its manifest and files."""

    path = Path(zip_path)
    if not path.exists():
        raise FileNotFoundError(path)

    try:
        with zipfile.ZipFile(path) as archive:
            manifest = json.loads(archive.read(_MANIFEST_FILENAME).decode("utf-8"))
            files: dict[str, str | bytes] = {}
            for name in archive.namelist():
                if name.endswith("/"):
                    continue
                if name == _MANIFEST_FILENAME:
                    continue
                files[name] = _decode_if_text(archive.read(name))
    except KeyError as exc:  # pragma: no cover - defensive guard
        raise ZendeskAppPackageError("Bundle is missing manifest.json") from exc
    except json.JSONDecodeError as exc:  # pragma: no cover - defensive guard
        raise ZendeskAppPackageError("manifest.json is not valid JSON") from exc
    except zipfile.BadZipFile as exc:  # pragma: no cover - defensive guard
        raise ZendeskAppPackageError(f"File '{path}' is not a valid ZIP archive") from exc

    return {"manifest": manifest, "files": files}


def scaffold_template(zaf: dict[str, Any], out_dir: str | Path) -> list[Path]:
    """Write a normalised scaffold for a ZAF application bundle."""

    output_root = Path(out_dir)
    output_root.mkdir(parents=True, exist_ok=True)

    created_files: list[Path] = []

    manifest_path = output_root / _MANIFEST_FILENAME
    manifest_path.write_text(json.dumps(zaf.get("manifest", {}), indent=2, sort_keys=True) + "\n")
    created_files.append(manifest_path)

    for folder in _SCAFFOLD_FOLDERS:
        (output_root / folder).mkdir(parents=True, exist_ok=True)

    for name, content in zaf.get("files", {}).items():
        destination = output_root / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(content, bytes):
            destination.write_bytes(content)
        else:
            destination.write_text(content, encoding="utf-8")
        created_files.append(destination)

    readme_path = output_root / "README.md"
    if not readme_path.exists():
        readme_path.write_text(
            "# Zendesk App Template\n\n"
            "This directory was generated from a legacy ZAF package. "
            "Update the assets and source files before publishing.\n",
            encoding="utf-8",
        )
        created_files.append(readme_path)

    return created_files
