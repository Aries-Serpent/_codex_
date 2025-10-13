"""Utilities for semantic versioning of Codex artifacts."""

from __future__ import annotations

import datetime
import json
from pathlib import Path


class SemanticVersion:
    """Simple semantic version representation and manipulator."""

    def __init__(self, version: str):
        parts = version.split(".")
        self.major = int(parts[0]) if parts and parts[0].isdigit() else 0
        self.minor = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 0
        self.patch = int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else 0

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"

    def bump(self, level: str = "patch") -> None:
        if level == "major":
            self.major += 1
            self.minor = 0
            self.patch = 0
        elif level == "minor":
            self.minor += 1
            self.patch = 0
        else:
            self.patch += 1


def determine_bump(diff_entries: list[dict]) -> str:
    """Determine the semantic version bump level based on diff operations."""

    level = "patch"
    for entry in diff_entries:
        op = entry.get("op") or entry.get("action")
        if op in ("remove", "delete"):
            return "major"
        if op in ("add", "create") and level != "major":
            level = "minor"
    return level


def update_artifact_version(
    artifact_name: str,
    diff: list[dict],
    version_file: Path = Path("artifact_versions.json"),
    changelog_file: Path = Path("CHANGELOG.md"),
) -> None:
    """Update the version file and changelog for a given artifact based on diff operations."""

    bump_level = determine_bump(diff)
    versions: dict[str, str] = {}
    if version_file.exists():
        try:
            versions = json.loads(version_file.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            versions = {}

    current_version = versions.get(artifact_name, "0.0.0")
    semver = SemanticVersion(current_version)
    semver.bump(bump_level)
    new_version = str(semver)
    versions[artifact_name] = new_version
    version_file.write_text(json.dumps(versions, indent=2), encoding="utf-8")

    timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%SZ")
    log_entry = f"{timestamp} - {artifact_name} updated to v{new_version} ({bump_level} change)\n"
    with changelog_file.open("a", encoding="utf-8") as chf:
        chf.write(log_entry)
