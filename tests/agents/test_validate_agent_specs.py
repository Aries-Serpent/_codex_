"""Regression coverage for strict custom-agent specification validation."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

from scripts import validate_agent_specs as validator


@pytest.fixture
def schemas() -> tuple[dict, dict]:
    return (
        validator.load_schema(validator.SCHEMA_PATH),
        validator.load_schema(validator.FRONTMATTER_SCHEMA_PATH),
    )


def _write_profile(
    path: Path,
    *,
    name: str = "Example Agent",
    description: str | None = "Valid agent description",
    extra: dict | None = None,
    body: str = "Follow the repository instructions.",
) -> None:
    frontmatter = {"name": name}
    if description is not None:
        frontmatter["description"] = description
    frontmatter.update(extra or {})
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f"---\n{yaml.safe_dump(frontmatter, sort_keys=False)}---\n\n{body}\n",
        encoding="utf-8",
    )


def _write_registry(path: Path, entries: list[dict]) -> None:
    path.write_text(yaml.safe_dump({"agents": entries}, sort_keys=False), encoding="utf-8")


def _registry_entry(
    identifier: str,
    name: str,
    file: str,
    *,
    description: str = "Valid registry description",
    **extra: object,
) -> dict:
    return {
        "id": identifier,
        "name": name,
        "description": description,
        "file": file,
        "status": "active",
        "maturity": "production",
        **extra,
    }


def test_discovers_root_and_nested_markdown_agents(tmp_path: Path) -> None:
    agents_dir = tmp_path / ".github" / "agents"
    _write_profile(agents_dir / "pattern-discovery-skill.md")
    _write_profile(agents_dir / "nested" / "reviewer-agent.md")
    _write_profile(agents_dir / "nested" / "specialist.agent.md")
    _write_profile(agents_dir / "README.md")

    discovered = {
        path.relative_to(agents_dir).as_posix() for path in validator.find_agent_specs(agents_dir)
    }

    assert discovered == {
        "nested/reviewer-agent.md",
        "nested/specialist.agent.md",
        "pattern-discovery-skill.md",
    }


@pytest.mark.parametrize(
    ("content", "expected_error"),
    [
        ("# Missing frontmatter\n", "missing YAML frontmatter"),
        ("---\nname: [broken\n---\nPrompt\n", "malformed YAML frontmatter"),
        ("---\nname: Mapping only\n---\n", "prompt is empty"),
    ],
)
def test_parse_failures_are_explicit(
    tmp_path: Path,
    content: str,
    expected_error: str,
) -> None:
    profile = tmp_path / "broken-agent.md"
    profile.write_text(content, encoding="utf-8")

    with pytest.raises(validator.SpecParseError, match=expected_error):
        validator.parse_agent_spec(profile)


@pytest.mark.parametrize("description", [None, "", "   \t"])
def test_description_is_required_and_nonblank(
    tmp_path: Path,
    schemas: tuple[dict, dict],
    description: str | None,
) -> None:
    _, frontmatter_schema = schemas
    profile = tmp_path / "description-agent.md"
    _write_profile(profile, description=description)

    errors = validator.validate_spec(validator.parse_agent_spec(profile), frontmatter_schema)

    assert errors
    assert any("description" in error for error in errors)


def test_parse_failure_is_reported_in_repository_results(
    tmp_path: Path,
    schemas: tuple[dict, dict],
) -> None:
    registry_schema, frontmatter_schema = schemas
    agents_dir = tmp_path / ".github" / "agents"
    agents_dir.mkdir(parents=True)
    (agents_dir / "broken-agent.md").write_text("# No frontmatter\n", encoding="utf-8")
    _write_registry(agents_dir / "AGENT_REGISTRY.yaml", [])

    results = validator.validate_repository(
        repo_root=tmp_path,
        agents_dir=agents_dir,
        registry_schema=registry_schema,
        frontmatter_schema=frontmatter_schema,
    )

    broken = next(result for result in results if result["path"].endswith("broken-agent.md"))
    assert broken["valid"] is False
    assert broken["errors"] == ["missing YAML frontmatter"]


def test_registry_ignores_readme_false_positives(tmp_path: Path, schemas: tuple[dict, dict]) -> None:
    registry_schema, frontmatter_schema = schemas
    agents_dir = tmp_path / ".github" / "agents"
    legacy_readme = agents_dir / "legacy" / "README.md"
    legacy_readme.parent.mkdir(parents=True, exist_ok=True)
    legacy_readme.write_text("# Legacy docs only\n", encoding="utf-8")
    profile = agents_dir / "actual-agent.md"
    _write_profile(profile, name="Actual Agent", extra={"id": "actual-agent"})
    _write_registry(
        agents_dir / "AGENT_REGISTRY.yaml",
        [
            _registry_entry("legacy-agent", "Legacy Agent", "legacy/README.md"),
            _registry_entry("actual-agent", "Actual Agent", "actual-agent.md"),
        ],
    )

    results = validator.validate_repository(
        repo_root=tmp_path,
        agents_dir=agents_dir,
        registry_schema=registry_schema,
        frontmatter_schema=frontmatter_schema,
    )

    messages = "\n".join(error for result in results for error in result["errors"])
    assert "referenced Markdown file is not a valid agent profile" not in messages
    assert all(result["valid"] for result in results), results


def test_profile_id_handles_agent_yaml_suffix() -> None:
    assert validator._profile_id(Path("nested/example.agent.yml")) == "example"
    assert validator._profile_id(Path("nested/example.agent.yaml")) == "example"


def test_profile_id_preserves_agent_and_skill_slugs() -> None:
    assert validator._profile_id(Path("nested/example-agent.md")) == "example-agent"
    assert validator._profile_id(Path("nested/example-skill.md")) == "example-skill"


def test_registry_description_is_required_and_nonblank(schemas: tuple[dict, dict]) -> None:
    registry_schema, _ = schemas
    entry = _registry_entry("example-agent", "Example Agent", "example-agent.md")
    entry["description"] = " \t"

    errors = validator.validate_spec(entry, registry_schema)

    assert any("description" in error for error in errors)


def test_registry_file_and_identity_mismatches_fail(
    tmp_path: Path,
    schemas: tuple[dict, dict],
) -> None:
    registry_schema, frontmatter_schema = schemas
    agents_dir = tmp_path / ".github" / "agents"
    profile = agents_dir / "example-agent.md"
    _write_profile(
        profile,
        name="Profile Name",
        extra={"id": "profile-id"},
    )
    _write_registry(
        agents_dir / "AGENT_REGISTRY.yaml",
        [
            _registry_entry("registry-id", "Registry Name", profile.name),
            _registry_entry("missing-agent", "Missing Agent", "missing-agent.md"),
        ],
    )

    results = validator.validate_repository(
        repo_root=tmp_path,
        agents_dir=agents_dir,
        registry_schema=registry_schema,
        frontmatter_schema=frontmatter_schema,
    )
    messages = "\n".join(error for result in results for error in result["errors"])

    assert "registry/file id mismatch" in messages
    assert "registry/file name mismatch" in messages
    assert "referenced agent file does not exist" in messages


def test_registry_discovers_profile_with_generic_filename(
    tmp_path: Path,
    schemas: tuple[dict, dict],
) -> None:
    registry_schema, frontmatter_schema = schemas
    agents_dir = tmp_path / ".github" / "agents"
    profile = agents_dir / "nested" / "reviewer.md"
    _write_profile(profile, name="Reviewer")
    _write_registry(
        agents_dir / "AGENT_REGISTRY.yaml",
        [_registry_entry("reviewer", "Reviewer", "nested/reviewer.md")],
    )

    results = validator.validate_repository(
        repo_root=tmp_path,
        agents_dir=agents_dir,
        registry_schema=registry_schema,
        frontmatter_schema=frontmatter_schema,
    )

    assert any(result["path"].endswith("nested/reviewer.md") for result in results)
    assert all(result["valid"] for result in results), results


def test_duplicate_registry_identifiers_and_names_fail(
    tmp_path: Path,
    schemas: tuple[dict, dict],
) -> None:
    registry_schema, frontmatter_schema = schemas
    agents_dir = tmp_path / ".github" / "agents"
    agents_dir.mkdir(parents=True)
    _write_registry(
        agents_dir / "AGENT_REGISTRY.yaml",
        [
            _registry_entry("duplicate-agent", "Duplicate Agent", "one-agent.md"),
            _registry_entry("duplicate-agent", "Duplicate Agent", "two-agent.md"),
        ],
    )

    results = validator.validate_repository(
        repo_root=tmp_path,
        agents_dir=agents_dir,
        registry_schema=registry_schema,
        frontmatter_schema=frontmatter_schema,
    )
    messages = "\n".join(error for result in results for error in result["errors"])

    assert "duplicate registry identifier" in messages
    assert "duplicate registry name" in messages


def test_duplicate_registry_file_references_fail(
    tmp_path: Path,
    schemas: tuple[dict, dict],
) -> None:
    registry_schema, frontmatter_schema = schemas
    agents_dir = tmp_path / ".github" / "agents"
    profile = agents_dir / "shared-agent.md"
    _write_profile(profile)
    _write_registry(
        agents_dir / "AGENT_REGISTRY.yaml",
        [
            _registry_entry("shared-agent", "Example Agent", profile.name),
            _registry_entry("second-agent", "Second Agent", profile.name),
        ],
    )

    results = validator.validate_repository(
        repo_root=tmp_path,
        agents_dir=agents_dir,
        registry_schema=registry_schema,
        frontmatter_schema=frontmatter_schema,
    )
    messages = "\n".join(error for result in results for error in result["errors"])

    assert "duplicate registry file reference" in messages


def test_handler_manifest_and_selectable_references_are_checked(
    tmp_path: Path,
    schemas: tuple[dict, dict],
) -> None:
    registry_schema, frontmatter_schema = schemas
    agents_dir = tmp_path / ".github" / "agents"
    profile = agents_dir / "example-agent.md"
    _write_profile(profile, extra={"user-invocable": False})
    _write_registry(
        agents_dir / "AGENT_REGISTRY.yaml",
        [
            _registry_entry(
                "example-agent",
                "Example Agent",
                profile.name,
                handler="missing.module:run",
                manifest="missing/manifest.yaml",
                selectable=True,
            )
        ],
    )

    results = validator.validate_repository(
        repo_root=tmp_path,
        agents_dir=agents_dir,
        registry_schema=registry_schema,
        frontmatter_schema=frontmatter_schema,
    )
    messages = "\n".join(error for result in results for error in result["errors"])

    assert "referenced handler does not exist" in messages
    assert "referenced manifest does not exist" in messages
    assert "selectable status mismatch" in messages


@pytest.mark.parametrize(
    ("filename", "identifier", "name", "description"),
    [
        (
            "pattern-discovery-skill.md",
            "pattern-discovery-skill",
            "Pattern Discovery Skill",
            "Extracts and classifies patterns, scores confidence, tags improvement "
            "areas, and recommends promotion.",
        ),
        (
            "memory-sync-consolidation-skill.md",
            "memory-sync-consolidation-skill",
            "Memory Sync Consolidation Skill",
            "Consolidates STM into LTM with duplicate detection, fuzzy matching, "
            "retention policies, and pattern promotion.",
        ),
    ],
)
def test_affected_skill_profiles_are_valid_regressions(
    tmp_path: Path,
    schemas: tuple[dict, dict],
    filename: str,
    identifier: str,
    name: str,
    description: str,
) -> None:
    registry_schema, frontmatter_schema = schemas
    agents_dir = tmp_path / ".github" / "agents"
    profile = agents_dir / filename
    _write_profile(profile, name=name, description=description)
    _write_registry(
        agents_dir / "AGENT_REGISTRY.yaml",
        [_registry_entry(identifier, name, filename, description=description)],
    )

    results = validator.validate_repository(
        repo_root=tmp_path,
        agents_dir=agents_dir,
        registry_schema=registry_schema,
        frontmatter_schema=frontmatter_schema,
    )

    assert results
    assert all(result["valid"] for result in results), results


def test_strict_cli_generates_machine_readable_report(tmp_path: Path) -> None:
    agents_dir = tmp_path / "agents"
    profile = agents_dir / "example-agent.md"
    report_path = tmp_path / "report.json"
    _write_profile(profile)
    _write_registry(
        agents_dir / "AGENT_REGISTRY.yaml",
        [_registry_entry("example-agent", "Example Agent", profile.name)],
    )

    exit_code = validator.main(
        [
            "--agents-dir",
            str(agents_dir),
            "--strict",
            "--report",
            "--report-path",
            str(report_path),
        ]
    )
    report = json.loads(report_path.read_text(encoding="utf-8"))

    assert exit_code == 0
    assert report["summary"]["non_compliant"] == 0
    assert report["metadata"]["total_records"] == 2
