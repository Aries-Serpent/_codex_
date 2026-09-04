#!/usr/bin/env python3
"""Validate repository agent registry entries and GitHub agent profiles.

GitHub Markdown profiles and repository registry entries are deliberately
validated against separate schemas. Parse failures are emitted as ordinary
validation failures so malformed or missing frontmatter cannot disappear from
the report.

Usage:
    python scripts/validate_agent_specs.py [--report] [--strict]
"""

from __future__ import annotations

import argparse
import json
import logging
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import jsonschema

    HAS_JSONSCHEMA = True
except ImportError:
    jsonschema = None  # type: ignore[assignment]
    HAS_JSONSCHEMA = False

try:
    import yaml

    HAS_YAML = True
except ImportError:
    yaml = None  # type: ignore[assignment]
    HAS_YAML = False

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parent.parent
AGENTS_DIR = REPO_ROOT / ".github" / "agents"
REGISTRY_PATH = AGENTS_DIR / "AGENT_REGISTRY.yaml"
SCHEMA_PATH = REPO_ROOT / "configs" / "schemas" / "agent_spec.schema.json"
FRONTMATTER_SCHEMA_PATH = REPO_ROOT / "configs" / "schemas" / "github_agent_frontmatter.schema.json"
OUTPUT_REPORT = REPO_ROOT / ".codex" / "qa_walkthrough" / "agent_validation_report.json"

_FRONTMATTER_RE = re.compile(
    r"\A---[ \t]*\r?\n(?P<yaml>.*?)\r?\n---[ \t]*(?:\r?\n|\Z)",
    re.DOTALL,
)
_IGNORED_MARKDOWN_NAMES = {
    "agents.md",
    "agent_registry.md",
    "agent_registry_generated.md",
    "agent_consolidation.md",
    "readme.md",
    ".template_cognitive_agent.md",
    ".template",
    "template.md",
}


class SpecParseError(ValueError):
    """Raised when an agent definition cannot be parsed as a specification."""


def load_schema(path: Path = SCHEMA_PATH) -> dict[str, Any]:
    """Load a JSON schema from *path*."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        logger.error("Failed to load schema %s (%s): %s", path, type(exc).__name__, exc)
        return {}
    return data if isinstance(data, dict) else {}


def _looks_like_agent_frontmatter(path: Path) -> bool:
    """Heuristic: treat generic markdown files as agent specs only with frontmatter."""
    try:
        content = path.read_text(encoding="utf-8")
    except OSError:
        return False
    stripped = content.lstrip("\ufeff")
    if not stripped.startswith("---"):
        return False
    match = _FRONTMATTER_RE.match(stripped)
    if match is None:
        return False
    if not HAS_YAML:
        return False
    try:
        data = yaml.safe_load(match.group("yaml"))
    except yaml.YAMLError:
        return False
    if not isinstance(data, dict):
        return False
    return (
        isinstance(data.get("id"), str)
        and isinstance(data.get("name"), str)
        and isinstance(data.get("description"), str)
    )


def _is_markdown_agent(path: Path) -> bool:
    name = path.name.lower()
    if name in _IGNORED_MARKDOWN_NAMES:
        return False
    if name == "agent.md":
        return False
    if name.endswith(".agent.md") or name.endswith("-agent.md") or name.endswith("-skill.md"):
        return _looks_like_agent_frontmatter(path)
    return _looks_like_agent_frontmatter(path)


def _is_yaml_agent(path: Path) -> bool:
    name = path.name.lower()
    if name in {"agent_registry.yaml", "agent_registry.yml"}:
        return False
    if name.endswith(".agent.yaml") or name.endswith(".agent.yml"):
        return True
    if any(part in {"config", "manifest", "settings"} for part in path.parts):
        return False
    if name in {"config.yaml", "config.yml", "manifest.yaml", "manifest.yml"}:
        return False
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) if HAS_YAML else None
    except (OSError, yaml.YAMLError):
        return False
    if not isinstance(data, dict):
        return False
    return (
        isinstance(data.get("id"), str)
        and isinstance(data.get("name"), str)
        and isinstance(data.get("description"), str)
    )


def _is_agent_definition(path: Path) -> bool:
    """Return True only for recognized custom-agent spec paths."""
    if not path.is_file():
        return False
    suffix = path.suffix.lower()
    if suffix == ".md":
        return _is_markdown_agent(path)
    if suffix in {".yaml", ".yml"}:
        return _is_yaml_agent(path)
    return False


def find_agent_specs(agents_dir: Path = AGENTS_DIR) -> list[Path]:
    """Find root-level and nested agent definitions deterministically."""
    if not agents_dir.is_dir():
        logger.warning("Agents directory not found: %s", agents_dir)
        return []

    specs = [
        path
        for path in agents_dir.rglob("*")
        if path.is_file() and _is_agent_definition(path)
    ]
    return sorted(specs, key=lambda path: path.as_posix().casefold())


def _parse_markdown(path: Path, content: str) -> dict[str, Any]:
    match = _FRONTMATTER_RE.match(content.lstrip("\ufeff"))
    if match is None:
        raise SpecParseError("missing YAML frontmatter")
    if not HAS_YAML:
        raise SpecParseError("PyYAML is required to parse Markdown frontmatter")

    try:
        data = yaml.safe_load(match.group("yaml"))
    except yaml.YAMLError as exc:
        raise SpecParseError(f"malformed YAML frontmatter: {exc}") from exc
    if not isinstance(data, dict):
        raise SpecParseError("frontmatter must be a YAML mapping")

    body = content.lstrip("\ufeff")[match.end() :].strip()
    if not body:
        raise SpecParseError("Markdown agent prompt is empty")
    return data


def parse_agent_spec(path: Path) -> dict[str, Any]:
    """Parse one agent definition or raise :class:`SpecParseError`."""
    try:
        content = path.read_text(encoding="utf-8")
        suffix = path.suffix.lower()
        if suffix == ".md":
            return _parse_markdown(path, content)
        if suffix in {".yaml", ".yml"}:
            if not HAS_YAML:
                raise SpecParseError("PyYAML is required to parse YAML agent definitions")
            data = yaml.safe_load(content)
        elif suffix == ".json":
            data = json.loads(content)
        else:
            raise SpecParseError(f"unsupported specification extension: {suffix}")
    except SpecParseError:
        raise
    except (OSError, json.JSONDecodeError, yaml.YAMLError if HAS_YAML else OSError) as exc:
        raise SpecParseError(f"{type(exc).__name__}: {exc}") from exc

    if not isinstance(data, dict):
        raise SpecParseError("agent specification must be a mapping")
    return data


def _basic_validate(spec: dict[str, Any], schema: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for field in schema.get("required", []):
        if field not in spec:
            errors.append(f"Missing required field: {field}")

    for key, value in spec.items():
        rules = schema.get("properties", {}).get(key)
        if not isinstance(rules, dict):
            continue
        expected = rules.get("type")
        valid_type = (
            (expected == "string" and isinstance(value, str))
            or (expected == "array" and isinstance(value, list))
            or (expected == "boolean" and isinstance(value, bool))
            or (expected == "object" and isinstance(value, dict))
            or (expected == "integer" and isinstance(value, int) and not isinstance(value, bool))
            or (expected == "number" and isinstance(value, (int, float)))
        )
        if expected and not valid_type:
            errors.append(f"Field '{key}' should be {expected}, got {type(value).__name__}")
            continue
        if isinstance(value, str):
            if len(value) < rules.get("minLength", 0):
                errors.append(f"Field '{key}' is too short")
            pattern = rules.get("pattern")
            if pattern and re.search(pattern, value) is None:
                errors.append(f"Field '{key}' does not match {pattern!r}")
        if "enum" in rules and value not in rules["enum"]:
            errors.append(f"Field '{key}' must be one of {rules['enum']!r}")
    return errors


def validate_spec(spec: dict[str, Any], schema: dict[str, Any]) -> list[str]:
    """Validate a specification against *schema* and return stable messages."""
    if not HAS_JSONSCHEMA:
        return _basic_validate(spec, schema)

    validator = jsonschema.Draft7Validator(schema)
    errors = [
        f"{error.json_path}: {error.message}"
        for error in sorted(validator.iter_errors(spec), key=lambda item: list(item.path))
    ]
    return errors


def _result(path: str, kind: str, errors: list[str]) -> dict[str, Any]:
    return {
        "path": path,
        "kind": kind,
        "valid": not errors,
        "errors": errors,
    }


def _profile_id(path: Path) -> str:
    name = path.name.lower()
    suffixes = (
        ".agent.md",
        ".agent.yaml",
        ".agent.yml",
    )
    for suffix in suffixes:
        if name.endswith(suffix):
            return path.name[: -len(suffix)]
    return path.stem


def _relative(path: Path, repo_root: Path) -> str:
    try:
        return path.resolve().relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def _resolve_file_reference(
    reference: str,
    *,
    repo_root: Path,
    agents_dir: Path,
) -> Path | None:
    candidate = Path(reference)
    if candidate.is_absolute():
        return None
    candidates = (
        repo_root / candidate,
        agents_dir / candidate,
    )
    allowed_roots = (repo_root.resolve(), agents_dir.resolve())
    for item in candidates:
        resolved = item.resolve()
        if not any(resolved == root or root in resolved.parents for root in allowed_roots):
            continue
        if resolved.is_file():
            return resolved
    return None


def _resolve_code_reference(reference: str, *, repo_root: Path) -> Path | None:
    target = reference.split(":", 1)[0]
    direct = Path(target)
    if direct.is_absolute():
        return None
    if direct.suffix or "/" in target or "\\" in target:
        candidates = [repo_root / direct]
    else:
        module_path = Path(*target.split("."))
        candidates = [
            repo_root / "src" / module_path.with_suffix(".py"),
            repo_root / "src" / module_path / "__init__.py",
            repo_root / module_path.with_suffix(".py"),
            repo_root / module_path / "__init__.py",
        ]
    for candidate in candidates:
        resolved = candidate.resolve()
        try:
            resolved.relative_to(repo_root.resolve())
        except ValueError:
            continue
        if resolved.is_file():
            return resolved
    return None


def _load_registry(path: Path) -> tuple[list[dict[str, Any]], list[str]]:
    if not path.exists():
        return [], [f"registry not found: {path}"]
    if not HAS_YAML:
        return [], ["PyYAML is required to parse the agent registry"]
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        return [], [f"{type(exc).__name__}: {exc}"]
    if not isinstance(data, dict):
        return [], ["registry root must be a mapping"]
    agents = data.get("agents")
    if not isinstance(agents, list):
        return [], ["registry field 'agents' must be a list"]
    malformed = [index for index, entry in enumerate(agents) if not isinstance(entry, dict)]
    if malformed:
        return [], [f"registry entries must be mappings (invalid indexes: {malformed})"]
    return agents, []


def _append_duplicate_errors(
    results_by_key: dict[str, dict[str, Any]],
    records: list[tuple[str, str, str]],
    field: str,
) -> None:
    grouped: dict[str, list[tuple[str, str]]] = {}
    for key, path, value in records:
        normalized = value.strip().casefold()
        if normalized:
            grouped.setdefault(normalized, []).append((key, path))
    for duplicates in grouped.values():
        if len(duplicates) < 2:
            continue
        paths = ", ".join(path for _, path in duplicates)
        for key, _ in duplicates:
            results_by_key[key]["errors"].append(f"duplicate {field}: {paths}")


def validate_repository(
    *,
    repo_root: Path = REPO_ROOT,
    agents_dir: Path = AGENTS_DIR,
    registry_path: Path | None = None,
    registry_schema: dict[str, Any] | None = None,
    frontmatter_schema: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """Validate discovered definitions, registry entries, and their references."""
    registry_path = registry_path or agents_dir / "AGENT_REGISTRY.yaml"
    registry_schema = registry_schema or load_schema(
        repo_root / "configs/schemas/agent_spec.schema.json"
    )
    frontmatter_schema = frontmatter_schema or load_schema(
        repo_root / "configs/schemas/github_agent_frontmatter.schema.json"
    )

    results: list[dict[str, Any]] = []
    results_by_key: dict[str, dict[str, Any]] = {}
    parsed_profiles: dict[Path, dict[str, Any]] = {}
    definition_ids: list[tuple[str, str, str]] = []
    definition_names: list[tuple[str, str, str]] = []

    entries, registry_errors = _load_registry(registry_path)
    spec_paths = set(find_agent_specs(agents_dir))
    registry_spec_paths: set[Path] = set()
    for entry in entries:
        file_reference = entry.get("file")
        if not isinstance(file_reference, str) or not file_reference.strip():
            continue
        resolved = _resolve_file_reference(
            file_reference,
            repo_root=repo_root,
            agents_dir=agents_dir,
        )
        if resolved is not None and _is_agent_definition(resolved):
            spec_paths.add(resolved)
            registry_spec_paths.add(resolved)

    for spec_path in sorted(spec_paths, key=lambda path: path.as_posix().casefold()):
        relative_path = _relative(spec_path, repo_root)
        key = f"definition:{relative_path}"
        try:
            spec = parse_agent_spec(spec_path)
            schema = frontmatter_schema if spec_path.suffix.lower() == ".md" else registry_schema
            errors = validate_spec(spec, schema)
            parsed_profiles[spec_path.resolve()] = spec
            identifier = str(spec.get("id") or _profile_id(spec_path))
            display_name = str(spec.get("name") or identifier)
            definition_ids.append((key, relative_path, identifier))
            definition_names.append((key, relative_path, display_name))
        except SpecParseError as exc:
            errors = [str(exc)]
        kind = "registry" if spec_path in registry_spec_paths else "github_profile"
        result = _result(relative_path, kind, errors)
        results.append(result)
        results_by_key[key] = result

    if registry_errors:
        relative_registry = _relative(registry_path, repo_root)
        key = f"registry:{relative_registry}"
        result = _result(relative_registry, "registry", registry_errors)
        results.append(result)
        results_by_key[key] = result
        entries = []

    registry_ids: list[tuple[str, str, str]] = []
    registry_names: list[tuple[str, str, str]] = []
    registry_files: list[tuple[str, str, str]] = []
    for index, entry in enumerate(entries):
        identifier = str(entry.get("id") or f"index-{index}")
        entry_path = f"{_relative(registry_path, repo_root)}#{identifier}"
        key = f"registry-entry:{index}"
        errors = validate_spec(entry, registry_schema)
        result = _result(entry_path, "registry_entry", errors)
        results.append(result)
        results_by_key[key] = result

        if isinstance(entry.get("id"), str):
            registry_ids.append((key, entry_path, entry["id"]))
        if isinstance(entry.get("name"), str):
            registry_names.append((key, entry_path, entry["name"]))

        file_reference = entry.get("file")
        if isinstance(file_reference, str) and file_reference.strip():
            registry_files.append((key, entry_path, file_reference))
            resolved = _resolve_file_reference(
                file_reference,
                repo_root=repo_root,
                agents_dir=agents_dir,
            )
            if resolved is None:
                errors.append(f"referenced agent file does not exist: {file_reference}")
            elif not _is_agent_definition(resolved):
                continue
            else:
                profile = parsed_profiles.get(resolved)
                if resolved.suffix.lower() == ".md" and profile is None:
                    errors.append(
                        f"referenced Markdown file is not a valid agent profile: {file_reference}"
                    )
                elif profile is not None:
                    profile_id = str(profile.get("id") or _profile_id(resolved))
                    if entry.get("id") and profile_id != entry["id"]:
                        errors.append(
                            f"registry/file id mismatch: {entry['id']!r} != {profile_id!r}"
                        )
                    profile_name = profile.get("name")
                    if (
                        profile_name
                        and entry.get("name")
                        and str(profile_name).strip().casefold()
                        != str(entry["name"]).strip().casefold()
                    ):
                        errors.append(
                            f"registry/file name mismatch: {entry['name']!r} != {profile_name!r}"
                        )
                    expected_selectable = entry.get("selectable")
                    profile_selectable = profile.get(
                        "user-invocable",
                        profile.get("selectable"),
                    )
                    if (
                        isinstance(expected_selectable, bool)
                        and isinstance(profile_selectable, bool)
                        and expected_selectable != profile_selectable
                    ):
                        errors.append(
                            "registry/file selectable status mismatch: "
                            f"{expected_selectable!r} != {profile_selectable!r}"
                        )

        for field in ("handler", "entrypoint"):
            reference = entry.get(field)
            if (
                isinstance(reference, str)
                and reference.strip()
                and _resolve_code_reference(reference, repo_root=repo_root) is None
            ):
                errors.append(f"referenced {field} does not exist: {reference}")
        manifest = entry.get("manifest")
        if (
            isinstance(manifest, str)
            and manifest.strip()
            and _resolve_file_reference(
                manifest,
                repo_root=repo_root,
                agents_dir=agents_dir,
            )
            is None
        ):
            errors.append(f"referenced manifest does not exist: {manifest}")

    _append_duplicate_errors(results_by_key, definition_ids, "definition identifier")
    _append_duplicate_errors(results_by_key, definition_names, "definition name")
    _append_duplicate_errors(results_by_key, registry_ids, "registry identifier")
    _append_duplicate_errors(results_by_key, registry_names, "registry name")
    _append_duplicate_errors(results_by_key, registry_files, "registry file reference")

    for result in results:
        result["errors"] = sorted(set(result["errors"]))
        result["valid"] = not result["errors"]
    return results


def generate_report(
    results: list[dict[str, Any]],
    *,
    schema_path: Path = SCHEMA_PATH,
    frontmatter_schema_path: Path = FRONTMATTER_SCHEMA_PATH,
) -> dict[str, Any]:
    """Generate a machine-readable validation report."""
    compliant = [result for result in results if result["valid"]]
    non_compliant = [result for result in results if not result["valid"]]
    return {
        "metadata": {
            "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "registry_schema_path": str(schema_path),
            "frontmatter_schema_path": str(frontmatter_schema_path),
            "total_records": len(results),
        },
        "summary": {
            "compliant": len(compliant),
            "non_compliant": len(non_compliant),
            "compliance_rate": f"{len(compliant) / max(len(results), 1) * 100:.1f}%",
        },
        "compliant_agents": [result["path"] for result in compliant],
        "non_compliant_agents": [
            {
                "path": result["path"],
                "kind": result["kind"],
                "errors": result["errors"],
            }
            for result in non_compliant
        ],
    }


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate agent specifications")
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Deprecated compatibility flag; validation never rewrites agent profiles",
    )
    parser.add_argument("--report", action="store_true", help="Generate a JSON report")
    parser.add_argument("--strict", action="store_true", help="Exit nonzero on any failure")
    parser.add_argument("--agents-dir", type=Path, default=AGENTS_DIR)
    parser.add_argument("--registry", type=Path, default=None)
    parser.add_argument("--report-path", type=Path, default=OUTPUT_REPORT)
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run repository agent validation."""
    args = _build_parser().parse_args(argv)
    if args.fix:
        logger.warning("--fix is deprecated; fix reported source definitions explicitly")

    registry_schema = load_schema(SCHEMA_PATH)
    frontmatter_schema = load_schema(FRONTMATTER_SCHEMA_PATH)
    if not registry_schema or not frontmatter_schema:
        return 1

    results = validate_repository(
        repo_root=REPO_ROOT,
        agents_dir=args.agents_dir,
        registry_path=args.registry,
        registry_schema=registry_schema,
        frontmatter_schema=frontmatter_schema,
    )
    if not results:
        results = [_result(_relative(args.agents_dir, REPO_ROOT), "discovery", ["no agents found"])]

    compliant = sum(1 for result in results if result["valid"])
    non_compliant = len(results) - compliant
    logger.info("Validation results: %d compliant, %d non-compliant", compliant, non_compliant)
    for result in results:
        if result["valid"]:
            continue
        logger.warning("%s:", result["path"])
        for error in result["errors"]:
            logger.warning("  - %s", error)

    if args.report:
        report = generate_report(results)
        args.report_path.parent.mkdir(parents=True, exist_ok=True)
        args.report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        logger.info("Report saved to: %s", args.report_path)

    return 1 if args.strict and non_compliant else 0


if __name__ == "__main__":
    sys.exit(main())
