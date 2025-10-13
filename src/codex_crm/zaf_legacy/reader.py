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
import mimetypes
import os
from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path, PurePosixPath
from typing import BinaryIO
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
