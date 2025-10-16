"""List Codex ML plugins with structured logging and safe fallbacks."""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Iterable, Sequence
from typing import Any

from codex_ml.codex_structured_logging import (
    ArgparseJSONParser,
    capture_exceptions,
    init_json_logging,
    log_event,
    run_cmd,
)

_ = run_cmd  # imported for side-effect documentation (structured logging helpers)

_JSON_EPILOG = (
    "JSON schema:\n"
    "{\n"
    '  "programmatic": {"discovered": [<str>...], "names": [<str>...]},\n'
    '  "legacy": {"models": [<str>...], "tokenizers": [<str>...], "datasets": [<str>...] }\n'
    "}\n"
)


def _list_models_safe() -> list[str]:
    try:
        from codex_ml.registry import list_models  # type: ignore[attr-defined]
    except Exception:
        return []
    try:
        return sorted({str(model) for model in list_models()})
    except Exception:
        return []


def _list_tokenizers_safe() -> list[str]:
    try:
        from codex_ml.registry import list_tokenizers  # type: ignore[attr-defined]
    except Exception:
        return []
    try:
        return sorted({str(tokenizer) for tokenizer in list_tokenizers()})
    except Exception:
        return []


def _list_datasets_safe() -> list[str]:
    try:
        from codex_ml.data.registry import list_datasets  # type: ignore[attr-defined]
    except Exception:
        return []
    try:
        return sorted({str(dataset) for dataset in list_datasets()})
    except Exception:
        return []


def _programmatic_registry_snapshot(*, discover: bool = True) -> dict[str, Any]:
    snapshot: dict[str, Any] = {"names": [], "discovered": []}
    try:
        from codex_ml.plugins import programmatic  # type: ignore[attr-defined]
    except Exception:
        return snapshot

    try:
        registry = programmatic.registry()
    except Exception:
        return snapshot

    discovered_items: list[str] = []
    if discover:
        try:
            discovered = registry.discover()
        except Exception:
            discovered_items = []
        else:
            if isinstance(discovered, dict):
                discovered_items = [f"{key}={value}" for key, value in discovered.items()]
            elif isinstance(discovered, list | tuple | set):
                discovered_items = [str(item) for item in discovered]
            elif discovered not in (None, False):
                discovered_items = [str(discovered)]
    snapshot["discovered"] = sorted({item for item in discovered_items if item})

    try:
        if hasattr(registry, "names"):
            iterable = registry.names()
        else:
            iterable = [plugin.name() for plugin in registry.all()]
    except Exception:
        iterable = []
    snapshot["names"] = sorted({str(item) for item in iterable if item})
    return snapshot


def _unique(iterables: Iterable[Iterable[str]]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for items in iterables:
        for item in items:
            if item in seen:
                continue
            seen.add(item)
            ordered.append(item)
    return ordered


def _print_lines(title: str, items: Iterable[str]) -> None:
    header = f"{title}:"
    print(header)
    printed = False
    for item in items:
        print(f"  - {item}")
        printed = True
    if not printed:
        print("  (none)")


def _print_programmatic(snapshot: dict[str, Any]) -> None:
    names = snapshot.get("names", []) or []
    discovered = snapshot.get("discovered", []) or []
    _print_lines("Programmatic", names)
    if discovered:
        print("  discovered:")
        for item in discovered:
            print(f"    - {item}")


def _build_parser() -> ArgparseJSONParser:
    return ArgparseJSONParser(
        description="List Codex ML plugin registries",
        epilog=_JSON_EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )


@capture_exceptions
def main(argv: Sequence[str] | None = None) -> int:
    logger = init_json_logging()
    parser = _build_parser()
    parser.add_argument(
        "--section",
        choices=["models", "tokenizers", "datasets", "programmatic", "all"],
        default="all",
        help="Limit output to a specific registry",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format",
    )
    parser.add_argument(
        "--names-only",
        action="store_true",
        help="Emit only plugin names (text format)",
    )
    parser.add_argument(
        "--no-discover",
        action="store_true",
        help="Skip entry-point discovery for programmatic registry",
    )

    arg_list = list(argv) if argv is not None else sys.argv[1:]
    args = parser.parse_args(arg_list)

    log_event(logger, "cli.start", prog=parser.prog, args=arg_list)

    include_models = args.format == "json" or args.section in {"models", "all"}
    include_tokenizers = args.format == "json" or args.section in {"tokenizers", "all"}
    include_datasets = args.format == "json" or args.section in {"datasets", "all"}
    include_programmatic = args.format == "json" or args.section in {"programmatic", "all"}

    models = _list_models_safe() if include_models else []
    tokenizers = _list_tokenizers_safe() if include_tokenizers else []
    datasets = _list_datasets_safe() if include_datasets else []
    programmatic = (
        _programmatic_registry_snapshot(discover=not args.no_discover)
        if include_programmatic
        else {"names": [], "discovered": []}
    )

    summary = {
        "section": args.section,
        "format": args.format,
        "names_only": bool(args.names_only),
        "discover": not args.no_discover,
        "models": len(models) if include_models else None,
        "tokenizers": len(tokenizers) if include_tokenizers else None,
        "datasets": len(datasets) if include_datasets else None,
        "programmatic": len(programmatic.get("names", [])) if include_programmatic else None,
    }

    if args.format == "json":
        payload = {
            "programmatic": programmatic,
            "legacy": {
                "models": models,
                "tokenizers": tokenizers,
                "datasets": datasets,
            },
            "options": {
                "discover": not args.no_discover,
                "names_only": bool(args.names_only),
                "section": args.section,
                "format": "json",
            },
        }
        print(json.dumps(payload, indent=2))
        log_event(logger, "cli.finish", prog=parser.prog, status="ok", summary=summary)
        return 0

    if args.names_only:
        sections: list[Iterable[str]] = []
        if include_programmatic:
            sections.append(programmatic.get("names", []))
        if include_models:
            sections.append(models)
        if include_tokenizers:
            sections.append(tokenizers)
        if include_datasets:
            sections.append(datasets)
        names = _unique(sections)
        for name in names:
            print(name)
        log_event(logger, "cli.finish", prog=parser.prog, status="ok", summary=summary)
        return 0

    if include_programmatic and args.section in {"programmatic", "all"}:
        _print_programmatic(programmatic)
    if include_models and args.section in {"models", "all"}:
        _print_lines("Models", models)
    if include_tokenizers and args.section in {"tokenizers", "all"}:
        _print_lines("Tokenizers", tokenizers)
    if include_datasets and args.section in {"datasets", "all"}:
        _print_lines("Datasets", datasets)

    log_event(logger, "cli.finish", prog=parser.prog, status="ok", summary=summary)
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entry
    raise SystemExit(main())
