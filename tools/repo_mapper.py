#!/usr/bin/env python3
"""Generate a JSON repository map for selected file extensions."""

from __future__ import annotations

import json
import subprocess
from collections.abc import Iterable, Iterator
from pathlib import Path

# Extensions to include in the repository map
EXTENSIONS: tuple[str, ...] = (
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

OUTPUT_FILE_NAME = "_codex_repo_map.json"

# Directory names to exclude anywhere in the path
EXCLUDED_DIRS: tuple[str, ...] = (
    ".git",
    "__pycache__",
    "build",
    "dist",
    ".venv",
)

# Specific filenames to exclude
EXCLUDED_FILENAMES: tuple[str, ...] = (OUTPUT_FILE_NAME,)


def should_skip(path: Path) -> bool:
    """Return True if the path should be excluded from the map."""

    if path.name in EXCLUDED_FILENAMES:
        return True

    return any(part in EXCLUDED_DIRS for part in path.parts)


def iter_repo_files(root_dir: Path) -> Iterator[Path]:
    """Yield repository files, respecting .gitignore when possible."""

    git_dir = root_dir / ".git"
    if git_dir.exists():
        try:
            completed = subprocess.run(
                [
                    "git",
                    "ls-files",
                    "--cached",
                    "--others",
                    "--exclude-standard",
                    "-z",
                ],
                check=True,
                capture_output=True,
                cwd=root_dir,
            )
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass
        else:
            for relative_path in completed.stdout.decode("utf-8").split("\0"):
                if not relative_path:
                    continue
                path = root_dir / relative_path
                if not path.is_file():
                    continue
                if should_skip(path):
                    continue
                yield path
            return

    # Fallback: walk the directory tree if git is unavailable
    for path in root_dir.rglob("*"):
        if not path.is_file():
            continue
        if should_skip(path):
            continue
        yield path


def map_repo(root_dir: Path) -> dict[str, list[dict[str, int]]]:
    """Return a mapping of file extensions to metadata for repository files."""

    files_by_extension: dict[str, list[dict[str, int]]] = {}

    for path in iter_repo_files(root_dir):
        extension = path.suffix
        if extension not in EXTENSIONS:
            continue

        relative_path = path.relative_to(root_dir).as_posix()
        file_info = {"path": relative_path, "size": path.stat().st_size}

        files_by_extension.setdefault(extension, []).append(file_info)

    # Ensure deterministic ordering for easier diffing and readability
    ordered_map: dict[str, list[dict[str, int]]] = {}
    for extension in sorted(files_by_extension):
        ordered_map[extension] = sorted(
            files_by_extension[extension], key=lambda entry: entry["path"]
        )

    return ordered_map


def write_repo_map(root_dir: Path, data: dict[str, list[dict[str, int]]]) -> Path:
    """Write the repository map JSON file to the root directory."""
    output_path = root_dir / OUTPUT_FILE_NAME
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
