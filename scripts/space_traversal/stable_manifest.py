#!/usr/bin/env python3
"""
Stable Manifest

Purpose:
    Command-line utility (see argument parser for details)

Usage:
    python scripts/space_traversal/stable_manifest.py [options]
    
    Examples:
    $ python scripts/space_traversal/stable_manifest.py --help

Arguments:
    [To be documented]

Environment Variables:
    [To be documented]

Dependencies:
    [To be documented]

Exit Codes:
    0: Success
    1: Error

Author: Codex Team
Last Updated: 2026-01-16
"""


"""
import logging
logger = logging.getLogger(__name__)
Produce a stable manifest JSON for a given output directory.

Features:
- Walks a given directory and produces a manifest of filenames with timestamp normalization.
- Also provides stable, deterministic JSON dump for objects/lists if used as a module.
"""
from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path
from typing import Any

TIMESTAMP_RE = re.compile(r"_(?:20\d{6}_\d{6}|\d{8}_\d{6})")

__all__ = [
    "normalize_name",
    "manifest_for_dir",
    "normalize_payload",
    "stable_dumps",
    "write_stable_json",
]


def normalize_name(name: str) -> str:
    """
    Normalize filename by replacing timestamp patterns (used for stable manifests).
    """
    return TIMESTAMP_RE.sub("_TIMESTAMP", name)


def manifest_for_dir(dirpath: str | Path) -> list[str]:
    """
    Walk directory and produce manifest with timestamp normalization.
    """
    dirpath = str(dirpath)
    entries = []
    for root, _, files in os.walk(dirpath):
        for f in sorted(files):
            rel = os.path.relpath(os.path.join(root, f), dirpath)
            entries.append(normalize_name(rel))
    return entries


def _stable_list(values: list[Any]) -> list[Any]:
    normalized: list[Any] = []
    for item in values:
        if isinstance(item, dict):
            normalized.append(_stable_dict(item))
        elif isinstance(item, list):
            normalized.append(_stable_list(item))
        else:
            normalized.append(item)
    try:
        return sorted(normalized, key=lambda value: json.dumps(value, sort_keys=True))
    except TypeError as e:
        logger.debug(f"TypeError: {e}")
        return normalized


def _stable_dict(value: dict[str, Any]) -> dict[str, Any]:
    stable: dict[str, Any] = {}
    for key in sorted(value):
        entry = value[key]
        if isinstance(entry, dict):
            stable[key] = _stable_dict(entry)
        elif isinstance(entry, list):
            stable[key] = _stable_list(entry)
        else:
            stable[key] = entry
    return stable


def normalize_payload(payload: Any) -> Any:
    """
    Recursively sort and normalize dictionaries/lists for deterministic output.
    """
    if isinstance(payload, dict):
        return _stable_dict(payload)
    if isinstance(payload, list):
        return _stable_list(payload)
    return payload


def stable_dumps(payload: Any) -> str:
    """
    Dump normalized payload to deterministic JSON string.
    """
    normalized = normalize_payload(payload)
    return json.dumps(normalized, indent=2, sort_keys=True, ensure_ascii=False)


def write_stable_json(payload: Any, destination: Path | str) -> Path:
    """
    Write deterministic JSON to path, creating directories as needed.
    """
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(stable_dumps(payload), encoding="utf-8")
    return destination


def main(argv=None):
    """
    CLI entrypoint: walk directory and dump normalized manifest of files.
    """
    p = argparse.ArgumentParser(description="Produce stable manifest for directory")
    p.add_argument("--dir", required=True, help="directory to manifest")
    p.add_argument("--out", required=True, help="output json manifest")
    args = p.parse_args(argv)

    entries = manifest_for_dir(args.dir)
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(entries, fh, indent=2)
    print(f"Wrote manifest to {args.out}")


if __name__ == "__main__":
    main()
