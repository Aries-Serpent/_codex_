#!/usr/bin/env python3
"""Generate a JSON repository map for selected file extensions."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

# Extensions to include in the repository map
EXTENSIONS: Tuple[str, ...] = (
    ".py",
    ".md",
    ".yaml",
    ".yml",
    ".json",
    ".toml",
    ".ini",
    ".txt",
    ".ipynb",
)

# Directory names to exclude anywhere in the path
EXCLUDED_DIRS: Tuple[str, ...] = (
    ".git",
    "__pycache__",
    "build",
    "dist",
)


def should_skip(path: Path) -> bool:
    """Return True if the path is inside an excluded directory."""
    return any(part in EXCLUDED_DIRS for part in path.parts)


def map_repo(root_dir: Path) -> Dict[str, List[Dict[str, int]]]:
    """Walk the repository and build a mapping of extensions to file info."""
    results: Dict[str, List[Dict[str, int]]] = {}

    for path in root_dir.rglob("*"):
        if not path.is_file():
            continue
        if should_skip(path):
            continue

        ext = path.suffix.lower()
        if ext not in EXTENSIONS:
            continue

        rel_path = path.relative_to(root_dir).as_posix()
        size = path.stat().st_size
        results.setdefault(ext, []).append({"path": rel_path, "size": size})

    for file_list in results.values():
        file_list.sort(key=lambda entry: entry["path"])

    sorted_results = {ext: results[ext] for ext in sorted(results)}
    return sorted_results


def write_repo_map(root_dir: Path, data: Dict[str, List[Dict[str, int]]]) -> Path:
    """Write the repository map JSON file to the root directory."""
    output_path = root_dir / "_codex_repo_map.json"
    output_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return output_path


def log_summary(total_files: int, extension_count: int, output_path: Path) -> None:
    """Print a summary of the work performed."""
    print(f"Processed {total_files} files across {extension_count} extensions.")
    print(f"Repository map written to: {output_path}")


def main(argv: Iterable[str] | None = None) -> int:
    root = Path(".").resolve()
    repo_map = map_repo(root)
    output_path = write_repo_map(root, repo_map)
    total_files = sum(len(files) for files in repo_map.values())
    log_summary(total_files, len(repo_map), output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
