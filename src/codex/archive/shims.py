"""Helpers for writing consolidation shims and pointers."""

from __future__ import annotations

from pathlib import Path

_PY_WARN = (
    "import warnings as _warnings\n"
    "_warnings.warn(\"Deprecated shim: re-export from canonical module\", "
    "DeprecationWarning, stacklevel=2)\n"
)


def write_python_shim(duplicate: Path, canonical_import_path: str) -> None:
    duplicate.parent.mkdir(parents=True, exist_ok=True)
    duplicate.write_text(
        "# AUTO-GENERATED SHIM — DO NOT EDIT\n"
        f"{_PY_WARN}"
        f"from {canonical_import_path} import *  # noqa: F401,F403\n",
        encoding="utf-8",
    )


def write_markdown_pointer(duplicate: Path, canonical_rel_path: str) -> None:
    duplicate.parent.mkdir(parents=True, exist_ok=True)
    duplicate.write_text(
        f"**This document has been consolidated.** See canonical: `{canonical_rel_path}`.\n",
        encoding="utf-8",
    )


def write_json_pointer(duplicate: Path, canonical_rel_path: str) -> None:
    duplicate.parent.mkdir(parents=True, exist_ok=True)
    duplicate.write_text(
        '{ "$ref": "' + canonical_rel_path.replace("\\", "/") + '" }\n',
        encoding="utf-8",
    )


def write_csv_pointer(duplicate: Path, canonical_rel_path: str) -> None:
    duplicate.parent.mkdir(parents=True, exist_ok=True)
    duplicate.write_text(
        f"# Consolidated; see canonical: {canonical_rel_path}\n",
        encoding="utf-8",
    )
