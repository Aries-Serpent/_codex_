"""Helpers for reading legacy Zendesk App Framework (ZAF) bundles.

The legacy ZAF bundles are simple ZIP archives that mirror the `src/` tree in
modern CLI projects.  Historically we unpacked them straight into the output
folder which meant nested structures were flattened and assets with duplicate
filenames could overwrite one another.  The helpers in this module normalise
paths, create the `src/` staging directory, and ensure that binary assets are
never written through a text handle.
"""

from __future__ import annotations

import io
import json
import mimetypes
import os
from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path, PurePosixPath
from typing import Any, BinaryIO
from zipfile import ZipFile, ZipInfo

_TEXT_EXTENSIONS: frozenset[str] = frozenset(
    {
        ".css",
        ".hbs",
        ".handlebars",
        ".html",
        ".js",
        ".json",
        ".less",
        ".liquid",
        ".md",
        ".scss",
        ".txt",
        ".xml",
        ".yaml",
        ".yml",
    }
)


def extract_legacy_app(archive: Path | BinaryIO, out: Path) -> list[Path]:
    """Extract *archive* into ``out / "src"`` and return written file paths."""

    out_src = out / "src"
    out_src.mkdir(parents=True, exist_ok=True)

    written: list[Path] = []
    with _open_zip(archive) as bundle:
        for entry in bundle.infolist():
            relative = _normalise_entry_path(entry)
            if relative is None:
                continue

            destination = out_src / relative
            if entry.is_dir():
                destination.mkdir(parents=True, exist_ok=True)
                continue

            destination.parent.mkdir(parents=True, exist_ok=True)
            data = bundle.read(entry)
            _write_payload(destination, entry, data)
            written.append(destination)

    return written


class ZendeskAppPackageError(Exception):
    """Raised when a ZAF legacy package cannot be processed."""


def read_zaf(source: str | os.PathLike[str]) -> dict[str, Any]:
    """Read a legacy ZAF package and return manifest metadata."""

    path = Path(source)
    if not path.exists():  # pragma: no cover - defensive guard
        raise ZendeskAppPackageError(f"Package {path} does not exist")
    try:
        with ZipFile(path) as archive:
            manifest: dict[str, Any] = {}
            if "manifest.json" in archive.namelist():
                manifest = json.loads(archive.read("manifest.json"))
    except Exception as exc:  # pragma: no cover - defensive guard
        raise ZendeskAppPackageError(str(exc)) from exc
    return {"archive_path": path, "manifest": manifest}


def scaffold_template(package: dict[str, Any], out_dir: str | os.PathLike[str]) -> Path:
    """Create a project scaffold from a parsed ZAF legacy package."""

    destination = Path(out_dir)
    destination.mkdir(parents=True, exist_ok=True)
    archive = package.get("archive_path")
    if archive is not None:
        extract_legacy_app(Path(archive), destination)
    manifest = package.get("manifest", {})
    normalised = _normalise_manifest(manifest)
    (destination / "manifest.json").write_text(json.dumps(normalised, indent=2), encoding="utf-8")
    return destination


def _normalise_manifest(manifest: dict[str, Any]) -> dict[str, Any]:
    """Ensure the manifest contains required placeholder parameters."""

    copy = dict(manifest)
    parameters = list(copy.get("parameters", []))
    if not any(param.get("name") == "API_BASE" for param in parameters):
        parameters.append(
            {
                "name": "API_BASE",
                "type": "text",  # minimal hint for downstream scaffolds
                "default": "https://example.zendesk.com/api/v2",
            }
        )
    copy["parameters"] = parameters
    return copy


@contextmanager
def _open_zip(archive: Path | BinaryIO) -> Generator[ZipFile, None, None]:
    if isinstance(archive, str | os.PathLike):
        with ZipFile(archive) as zf:
            yield zf
        return

    data = archive.read()
    if hasattr(archive, "seek"):
        archive.seek(0)
    with ZipFile(io.BytesIO(data)) as zf:
        yield zf


def _normalise_entry_path(entry: ZipInfo) -> Path | None:
    raw_path = entry.filename
    pure = PurePosixPath(raw_path)
    parts: list[str] = []
    for part in pure.parts:
        if part in ("", "."):
            continue
        if part == "..":
            raise ValueError(f"Refusing to extract path that escapes archive root: {raw_path!r}")
        parts.append(part)

    if not parts:
        return None

    return Path(*parts)


def _write_payload(destination: Path, entry: ZipInfo, data: bytes) -> None:
    is_text_hint = _is_probably_text(entry.filename)
    if is_text_hint:
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError:
            destination.write_bytes(data)
            return
        destination.write_text(text, encoding="utf-8")
        return

    destination.write_bytes(data)


def _is_probably_text(filename: str) -> bool:
    suffix = Path(filename).suffix.lower()
    if suffix in _TEXT_EXTENSIONS:
        return True

    mime, _ = mimetypes.guess_type(filename)
    return bool(mime and mime.startswith("text/"))
