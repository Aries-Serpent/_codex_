#!/usr/bin/env python3
"""Validate Hydra configuration files against JSON/YAML schemas."""

from __future__ import annotations

import argparse
import json
import sys
import time
from collections import Counter
from pathlib import Path
from typing import Any, Dict, Iterable, Iterator, List, Sequence, Tuple

try:  # pragma: no cover - optional dependency guard
    import yaml
except Exception:  # pragma: no cover - fallback when PyYAML missing
    yaml = None  # type: ignore[assignment]

try:  # pragma: no cover - optional dependency guard
    from jsonschema import Draft7Validator, Draft202012Validator
except Exception:  # pragma: no cover
    Draft202012Validator = None  # type: ignore[assignment]
    Draft7Validator = None  # type: ignore[assignment]

DEFAULT_GROUPS: Dict[str, Tuple[Tuple[Path, Path], ...]] = {
    "training": (
        (Path("configs/training/base.yaml"), Path("configs/schemas/training.schema.yaml")),
        (
            Path("configs/training/profiles/default.yaml"),
            Path("configs/schemas/training_profile.schema.json"),
        ),
    ),
    "evaluation": (
        (Path("configs/evaluation/default.yaml"), Path("configs/schemas/evaluation.schema.json")),
    ),
    "logging": (
        (Path("configs/base/logging/base.yaml"), Path("configs/schemas/logging.schema.yaml")),
    ),
    "tracking": (
        (Path("configs/tracking/base.yaml"), Path("configs/schemas/tracking.schema.yaml")),
        (Path("configs/tracking/offline.yaml"), Path("configs/schemas/tracking.schema.yaml")),
    ),
    "deployment": (
        (Path("configs/deployment/interfaces.yaml"), Path("configs/schemas/deployment_interfaces.schema.yaml")),
        (Path("configs/deploy/reasoning_pod.yaml"), Path("configs/schemas/deployment_reasoning_pod.schema.yaml")),
    ),
    "monitoring": (
        (
            Path("configs/deployment/hhg_logistics/monitor/default.yaml"),
            Path("configs/schemas/monitoring.schema.yaml"),
        ),
    ),
}


def iter_yaml_files(root: Path) -> Iterable[Path]:
    for path in root.rglob("*.yaml"):
        yield path


def _flatten_groups(groups: Sequence[str]) -> Tuple[Tuple[Path, Path], ...]:
    if not groups or "all" in groups:
        selected = list(DEFAULT_GROUPS)
    else:
        selected = list(groups)

    unknown = set(selected) - set(DEFAULT_GROUPS)
    if unknown:
        raise SystemExit(f"unknown group(s): {sorted(unknown)}")

    flattened: List[Tuple[Path, Path]] = []
    for group in selected:
        flattened.extend(DEFAULT_GROUPS[group])
    return tuple(flattened)


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


def _build_report(
    results: List[Dict[str, Any]], *, started_at: str, duration_seconds: float, exit_code: int
) -> Dict[str, Any]:
    counts = Counter(result["status"] for result in results)
    return {
        "total": len(results),
        "counts": dict(counts),
        "results": results,
        "started_at": started_at,
        "duration_seconds": round(duration_seconds, 3),
        "exit_code": exit_code,
    }


def _write_report(path: Path, report: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2), encoding="utf-8")


def _append_log(path: Path, report: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as log_file:
        log_file.write(json.dumps(report) + "\n")


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
    return _flatten_groups(args.group)


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate Codex configuration files")
    parser.add_argument("--config", help="Path to config file", default=None)
    parser.add_argument("--schema", help="Path to schema file", default=None)
    parser.add_argument("--root", help="Validate all YAML configs under this directory", default=None)
    parser.add_argument(
        "--group",
        action="append",
        choices=sorted(list(DEFAULT_GROUPS) + ["all"]),
        help="Named config groups to validate (default: all groups)",
    )
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
    parser.add_argument(
        "--report",
        help="Optional path to write a JSON summary report",
        default=None,
    )
    parser.add_argument(
        "--log",
        help="Optional JSONL path to append summary records for observability",
        default=None,
    )
    parsed = parser.parse_args(list(argv) if argv is not None else None)

    allow_partial = bool(parsed.allow_partial or (parsed.root and not parsed.strict))
    exit_code = 0
    results: List[Dict[str, Any]] = []
    start_ts = time.time()

    for config_path, schema_path in _resolve_targets(parsed):
        status = "ok"
        filtered_errors: List[str] = []

        if not config_path.exists():
            status = "missing_config"
            filtered_errors = [f"config missing: {config_path}"]
            print(f"skip: {config_path} (missing)")
        elif not schema_path.exists():
            status = "missing_schema"
            filtered_errors = [f"schema missing: {schema_path}"]
            print(f"skip: {schema_path} (missing)")
        else:
            raw_errors = validate_pair(config_path, schema_path)
            filtered_errors = _filter_errors(raw_errors, allow_partial=allow_partial)
            if raw_errors and not filtered_errors and allow_partial:
                status = "partial"
                if not parsed.quiet:
                    print(f"SKIP {config_path} (partial config allowed)")
            elif filtered_errors:
                status = "fail"
                exit_code = 1
                print(f"FAIL {config_path} -> {schema_path}")
                for error in filtered_errors:
                    print(f"  - {error}")
            elif not parsed.quiet:
                print(f"OK   {config_path}")

        results.append(
            {
                "config": str(config_path),
                "schema": str(schema_path),
                "status": status,
                "errors": filtered_errors,
            }
        )

    ended = time.time()
    report = _build_report(
        results,
        started_at=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(start_ts)),
        duration_seconds=ended - start_ts,
        exit_code=exit_code,
    )

    if parsed.report:
        _write_report(Path(parsed.report), report)
    if parsed.log:
        _append_log(Path(parsed.log), report)

    return exit_code


if __name__ == "__main__":  # pragma: no cover - CLI entrypoint
    sys.exit(main())
