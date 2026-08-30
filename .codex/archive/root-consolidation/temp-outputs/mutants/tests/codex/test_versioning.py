"""Smoke tests for :mod:`codex.versioning`."""

from __future__ import annotations

import json
from pathlib import Path

from codex import _version
from codex.versioning import SemanticVersion, determine_bump, update_artifact_version


def test_semantic_version_and_bump():
    semver = SemanticVersion("1.2.3")
    semver.bump("minor")
    assert str(semver) == "1.3.0", "Condition must be true"
    assert determine_bump([{"op": "add"}]) == "minor", "Condition must be true"
    assert determine_bump([{"op": "remove"}]) == "major", "Condition must be true"


def test_update_artifact_version(tmp_path: Path):
    version_file = tmp_path / "versions.json"
    changelog = tmp_path / "CHANGELOG.md"

    update_artifact_version(
        "artifact",
        [{"op": "add", "path": "/tmp"}],
        version_file=version_file,
        changelog_file=changelog,
    )

    versions = json.loads(version_file.read_text())
    assert "artifact" in versions, "Condition must be true"
    assert changelog.exists(), "Condition must be true"
    assert _version.__version__, "Condition must be true"
