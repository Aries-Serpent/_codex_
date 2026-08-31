#!/usr/bin/env python3
"""Validate repo-level Dependabot config for schema and scoping regressions."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any, Iterable

try:
    import yaml
except ImportError as exc:  # pragma: no cover - environment guard
    raise SystemExit("PyYAML is required to validate Dependabot configuration.") from exc

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG_PATH = REPO_ROOT / ".github" / "dependabot.yml"


def iter_strings(value: Any) -> Iterable[str]:
    """Yield string leaf values from nested YAML structures."""
    if isinstance(value, str):
        yield value
        return
    if isinstance(value, list):
        for item in value:
            yield from iter_strings(item)
        return
    if isinstance(value, dict):
        for child in value.values():
            yield from iter_strings(child)


def normalize_directory(path: Any) -> str:
    """Normalize Dependabot directory strings to a canonical root form."""
    if path is None:
        return "/"
    text = str(path).strip()
    if not text:
        return "/"
    if not text.startswith("/"):
        text = f"/{text}"
    return text.rstrip("/") or "/"


def has_overlap(path_a: str, path_b: str) -> bool:
    """Return True when two Dependabot directories overlap."""
    left = normalize_directory(path_a)
    right = normalize_directory(path_b)
    if left == right:
        return True
    if left == "/" or right == "/":
        return True
    return left.startswith(f"{right}/") or right.startswith(f"{left}/")


def validate_dependabot_config(document: Any) -> list[str]:
    """Return a list of validation errors for the repo config."""
    errors: list[str] = []
    if not isinstance(document, dict):
        return ["Dependabot config root must be a mapping."]

    if document.get("version") != 2:
        errors.append("Dependabot config must set version: 2.")

    if "registries" in document and document.get("registries"):
        errors.append("Custom Dependabot registries are not allowed in the repo-level config.")

    updates = document.get("updates")
    if not isinstance(updates, list) or not updates:
        errors.append("Dependabot config requires a non-empty updates list.")
        return errors

    ecosystem_paths: dict[str, list[str]] = {}
    for index, update in enumerate(updates, start=1):
        if not isinstance(update, dict):
            errors.append(f"Update entry #{index} must be a mapping.")
            continue

        ecosystem = update.get("package-ecosystem")
        if not ecosystem:
            errors.append(f"Update entry #{index} is missing package-ecosystem.")
            continue

        if "registries" in update and update.get("registries"):
            errors.append(
                f"Update entry for {ecosystem} uses a custom registries block; remove it from the repo-level config."
            )

        if (update.get("groups") is None) or not isinstance(update.get("groups"), dict):
            errors.append(f"Update entry for {ecosystem} must define a groups block.")

        limit = update.get("open-pull-requests-limit")
        try:
            parsed_limit = int(limit)
        except (TypeError, ValueError):
            parsed_limit = -1
        if parsed_limit != 1:
            errors.append(f"Update entry for {ecosystem} must set open-pull-requests-limit: 1.")

        raw_directories: list[str] = []
        if "directories" in update:
            candidate = update.get("directories")
            if isinstance(candidate, str):
                raw_directories = [candidate]
            elif isinstance(candidate, list):
                raw_directories = [str(item) for item in candidate if isinstance(item, str) and item.strip()]
        elif "directory" in update:
            candidate = update.get("directory")
            if isinstance(candidate, str):
                raw_directories = [candidate]
            elif isinstance(candidate, list):
                raw_directories = [str(item) for item in candidate if isinstance(item, str) and item.strip()]
        if not raw_directories:
            errors.append(f"Update entry for {ecosystem} is missing a valid directory or directories list.")

        directories = [normalize_directory(item) for item in raw_directories]
        ecosystem_paths.setdefault(str(ecosystem), []).extend(directories)

        for value in iter_strings(update):
            if "${{" in value and "secret" in value.lower():
                errors.append(f"Update entry for {ecosystem} contains a secret expression: {value}")

    for ecosystem, directories in ecosystem_paths.items():
        for left_index, left in enumerate(directories):
            for right_index in range(left_index + 1, len(directories)):
                right = directories[right_index]
                if has_overlap(left, right):
                    errors.append(
                        f"Ecosystem '{ecosystem}' has overlapping directories: {left} and {right}."
                    )

    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--path",
        type=Path,
        default=DEFAULT_CONFIG_PATH,
        help="Path to the Dependabot config file to validate.",
    )
    args = parser.parse_args(argv)

    config_path = args.path.resolve()
    if not config_path.exists():
        print(f"Dependabot config not found: {config_path}", file=sys.stderr)
        return 2

    try:
        document = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as exc:
        print(f"YAML parse error in {config_path}: {exc}", file=sys.stderr)
        return 1

    errors = validate_dependabot_config(document)
    if errors:
        print(f"Dependabot config validation failed for {config_path}:")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"Dependabot config validation passed for {config_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
