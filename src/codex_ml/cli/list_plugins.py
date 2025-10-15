"""Utility to list registered Codex ML plugins."""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Iterable, Sequence
from contextlib import suppress
from typing import Any

from codex_ml.codex_structured_logging import (
    ArgparseJSONParser,
    capture_exceptions,
    init_json_logging,
    log_event,
    run_cmd,
)

_ = run_cmd

_JSON_EPILOG = (
    "JSON schema:\n"
    "{\n"
    '  "programmatic": {"discovered": [<str>...], "names": [<str>...]},\n'
    '  "legacy": {"models": [<str>...], "tokenizers": [<str>...], "datasets": [<str>...] }\n'
    "}\n"
)


def _list_models_safe() -> list[str]:
    try:
        from codex_ml.registry import list_models  # type: ignore
    except Exception:
        return []
    try:
        return sorted(str(name) for name in list_models())
    except Exception:
        return []


def _list_tokenizers_safe() -> list[str]:
    try:
        from codex_ml.registry import list_tokenizers  # type: ignore
    except Exception:
        return []
    try:
        return sorted(str(name) for name in list_tokenizers())
    except Exception:
        return []


def _list_datasets_safe() -> list[str]:
    try:
        from codex_ml.data.registry import list_datasets  # type: ignore
    except Exception:
        return []
    try:
        return sorted(str(name) for name in list_datasets())
    except Exception:
        return []


def _print_lines(header: str, items: Iterable[str]) -> None:
    print(f"{header}:")
    for item in sorted(set(items)):
        print(f"  - {item}")


def _programmatic_registry_snapshot(*, discover: bool = True) -> dict[str, Any] | None:
    try:
        from codex_ml.plugins import registry as programmatic_registry  # type: ignore[attr-defined]
    except Exception:
        return None
    try:
        registry = programmatic_registry()
    except Exception:
        return None

    snapshot: dict[str, Any] = {"names": [], "discovered": []}
    if discover:
        try:
            discovered = registry.discover()
        except Exception:
            discovered = []
        else:
            if isinstance(discovered, dict):
                snapshot["discovered"] = sorted(str(key) for key in discovered)
            elif isinstance(discovered, (list | tuple | set)):
                snapshot["discovered"] = sorted(str(item) for item in discovered)
            elif discovered:
                snapshot["discovered"] = [str(discovered)]

    names: list[str] = []
    try:
        for plugin in registry.all():  # type: ignore[attr-defined]
            with suppress(Exception):
                if hasattr(plugin, "name") and callable(plugin.name):  # type: ignore[attr-defined]
                    names.append(str(plugin.name()))
                elif hasattr(plugin, "__name__"):
                    names.append(str(plugin.__name__))
                else:
                    names.append(str(plugin))
    except Exception:
        names = []
    snapshot["names"] = sorted({*names})
    return snapshot


def _print_programmatic(snapshot: dict[str, Any] | None) -> None:
    print("Programmatic registry:")
    if not snapshot:
        print("  - (unavailable)")
        return
    names = snapshot.get("names", [])
    if names:
        for name in names:
            print(f"  - {name}")
    else:
        print("  - (none)")
    discovered = snapshot.get("discovered", [])
    if discovered:
        print(f"  discovered entry-points: {', '.join(discovered)}")


def main(argv: Sequence[str] | None = None) -> int:
    logger = init_json_logging()
    parser = ArgparseJSONParser(
        description="List Codex ML plugin registries",
        epilog=_JSON_EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--section",
        choices=["models", "tokenizers", "datasets", "programmatic", "all"],
        default="all",
    )
    parser.add_argument("--format", choices=["text", "json"], default="text", help="Output format")
    parser.add_argument(
        "--names-only",
        action="store_true",
        help="Print only programmatic plugin names (text mode)",
    )
    parser.add_argument(
        "--no-discover",
        action="store_true",
        help="Skip entry-point discovery for speed",
    )
    arg_list: list[str] = list(argv) if argv is not None else sys.argv[1:]

    with capture_exceptions(logger):
        args = parser.parse_args(arg_list)
        log_event(logger, "cli.start", prog=parser.prog, args=arg_list)

        summary: dict[str, Any] = {
            "section": args.section,
            "format": args.format,
            "names_only": args.names_only,
            "discover": not args.no_discover,
        }

        models: list[str] | None = None
        tokenizers: list[str] | None = None
        datasets: list[str] | None = None
        programmatic_snapshot = None

        include_programmatic = (
            args.section in {"programmatic", "all"} or args.names_only or args.format == "json"
        )
        include_models = args.section in {"models", "all"} or args.format == "json"
        include_tokenizers = args.section in {"tokenizers", "all"} or args.format == "json"
        include_datasets = args.section in {"datasets", "all"} or args.format == "json"

        if include_models:
            models = _list_models_safe()
        if include_tokenizers:
            tokenizers = _list_tokenizers_safe()
        if include_datasets:
            datasets = _list_datasets_safe()
        if include_programmatic:
            programmatic_snapshot = _programmatic_registry_snapshot(discover=not args.no_discover)

        summary.update(
            {
                "models": len(models) if models is not None else None,
                "tokenizers": len(tokenizers) if tokenizers is not None else None,
                "datasets": len(datasets) if datasets is not None else None,
                "programmatic": (
                    len(programmatic_snapshot.get("names", [])) if programmatic_snapshot else None
                ),
            }
        )

        if args.format == "json":
            payload = {
                "programmatic": programmatic_snapshot or {"names": [], "discovered": []},
                "legacy": {
                    "models": sorted(models or []),
                    "tokenizers": sorted(tokenizers or []),
                    "datasets": sorted(datasets or []),
                },
            }
            print(json.dumps(payload, indent=2))
        else:
            if args.names_only:
                names = (programmatic_snapshot or {}).get("names", [])
                print("\n".join(names))
            else:
                if include_models and models is not None:
                    _print_lines("Models", models)
                if include_tokenizers and tokenizers is not None:
                    _print_lines("Tokenizers", tokenizers)
                if include_datasets and datasets is not None:
                    _print_lines("Datasets", datasets)
                if include_programmatic:
                    _print_programmatic(programmatic_snapshot)

        log_event(
            logger,
            "cli.finish",
            prog=parser.prog,
            status="ok",
            section=args.section,
            summary=summary,
        )
        return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
