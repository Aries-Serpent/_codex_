#!/usr/bin/env python3
"""Validate Hydra configuration files against JSON/YAML schemas."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Iterable, Iterator, List, Tuple

try:  # pragma: no cover - optional dependency guard
    import yaml
except Exception:  # pragma: no cover - fallback when PyYAML missing
    yaml = None  # type: ignore[assignment]

try:  # pragma: no cover - optional dependency guard
    from jsonschema import Draft7Validator, Draft202012Validator
except Exception:  # pragma: no cover
    Draft202012Validator = None  # type: ignore[assignment]
    Draft7Validator = None  # type: ignore[assignment]

DEFAULT_TARGETS: Tuple[Tuple[Path, Path], ...] = (
    (Path("configs/training/base.yaml"), Path("configs/schemas/training.schema.yaml")),
    (
        Path("configs/training/profiles/default.yaml"),
        Path("configs/schemas/training_profile.schema.json"),
    ),
    (Path("configs/evaluation/default.yaml"), Path("configs/schemas/evaluation.schema.json")),
)


def iter_yaml_files(root: Path) -> Iterable[Path]:
    for path in root.rglob("*.yaml"):
        yield path


def _load_yaml(path: Path) -> Any:
    if yaml is None:
        raise RuntimeError("PyYAML is required to load configuration files")
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _load_schema(path: Path) -> Any:
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() in {".yaml", ".yml"}:
        if yaml is None:
            raise RuntimeError("PyYAML is required to load YAML schemas")
        return yaml.safe_load(text)
    return json.loads(text)


def _iter_errors(instance: Any, schema: Any) -> Iterator[str]:
    if Draft202012Validator is not None:
        validator = Draft202012Validator(schema)
    elif Draft7Validator is not None:
        validator = Draft7Validator(schema)
    else:
        raise RuntimeError("jsonschema is required to validate configurations")
    for error in validator.iter_errors(instance):
        path = "/".join(str(elem) for elem in error.path)
        location = path or "<root>"
        yield f"{location}: {error.message}"


def _filter_errors(errors: List[str], *, allow_partial: bool) -> List[str]:
    if not allow_partial:
        return errors
    return [err for err in errors if "required property" not in err]


def validate_pair(config_path: Path, schema_path: Path) -> List[str]:
    try:
        instance = _load_yaml(config_path)
    except Exception as exc:
        return [f"failed to load config: {exc}"]
    try:
        schema = _load_schema(schema_path)
    except Exception as exc:
        return [f"failed to load schema: {exc}"]
    return list(_iter_errors(instance, schema))


def _resolve_targets(args: argparse.Namespace) -> Iterable[Tuple[Path, Path]]:
    if args.root:
        if args.config:
            raise SystemExit("--config cannot be used with --root; pick one mode")
        if not args.schema:
            raise SystemExit("--schema is required when using --root")
        root_path = Path(args.root)
        if not root_path.exists():
            raise SystemExit(f"config root not found: {root_path}")
        schema_path = Path(args.schema)
        return ((path, schema_path) for path in iter_yaml_files(root_path))
    if args.config and args.schema:
        return ((Path(args.config), Path(args.schema)),)
    if args.config or args.schema:
        raise SystemExit("--config and --schema must be provided together")
    return DEFAULT_TARGETS


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate Codex configuration files")
    parser.add_argument("--config", help="Path to config file", default=None)
    parser.add_argument("--schema", help="Path to schema file", default=None)
    parser.add_argument("--root", help="Validate all YAML configs under this directory", default=None)
    parser.add_argument(
        "--allow-partial",
        action="store_true",
        help="Permit partial configs by filtering missing required-field errors",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Fail on missing required fields when used with --root",
    )
    parser.add_argument("--quiet", action="store_true", help="Suppress OK messages")
    parsed = parser.parse_args(list(argv) if argv is not None else None)

    allow_partial = bool(parsed.allow_partial or (parsed.root and not parsed.strict))
    exit_code = 0
    for config_path, schema_path in _resolve_targets(parsed):
        if not config_path.exists():
            print(f"skip: {config_path} (missing)")
            continue
        if not schema_path.exists():
            print(f"skip: {schema_path} (missing)")
            continue
        raw_errors = validate_pair(config_path, schema_path)
        errors = _filter_errors(raw_errors, allow_partial=allow_partial)
        if raw_errors and not errors and allow_partial:
            if not parsed.quiet:
                print(f"SKIP {config_path} (partial config allowed)")
            continue
        if errors:
            exit_code = 1
            print(f"FAIL {config_path} -> {schema_path}")
            for error in errors:
                print(f"  - {error}")
        elif not parsed.quiet:
            print(f"OK   {config_path}")
    return exit_code


if __name__ == "__main__":  # pragma: no cover - CLI entrypoint
    sys.exit(main())
