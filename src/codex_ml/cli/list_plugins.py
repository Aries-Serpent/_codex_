"""Utility to list registered Codex ML plugins."""

from __future__ import annotations

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
from codex_ml.data.registry import list_datasets
from codex_ml.registry import list_models, list_tokenizers

_ = run_cmd


def _print_lines(header: str, items: Iterable[str]) -> None:
    print(f"{header}:")
    for item in sorted(set(items)):
        print(f"  - {item}")


def _programmatic_registry_snapshot() -> dict[str, Any] | None:
    try:
        from codex_ml.plugins import registry as programmatic_registry  # type: ignore[attr-defined]
    except Exception:
        return None
    try:
        registry = programmatic_registry()
    except Exception:
        return None

    snapshot: dict[str, Any] = {"names": [], "discovered": []}
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
    parser = ArgparseJSONParser(description="List Codex ML plugin registries")
    parser.add_argument(
        "--section",
        choices=["models", "tokenizers", "datasets", "programmatic", "all"],
        default="all",
    )
    arg_list: list[str] = list(argv) if argv is not None else sys.argv[1:]

    with capture_exceptions(logger):
        args = parser.parse_args(arg_list)
        log_event(logger, "cli.start", prog=parser.prog, args=arg_list)

        summary: dict[str, Any] = {"section": args.section}

        models: list[str] | None = None
        if args.section in {"models", "all"}:
            models = list(list_models())
            _print_lines("Models", models)
        summary["models"] = len(models) if models is not None else None

        tokenizers: list[str] | None = None
        if args.section in {"tokenizers", "all"}:
            tokenizers = list(list_tokenizers())
            _print_lines("Tokenizers", tokenizers)
        summary["tokenizers"] = len(tokenizers) if tokenizers is not None else None

        datasets: list[str] | None = None
        if args.section in {"datasets", "all"}:
            datasets = list(list_datasets())
            _print_lines("Datasets", datasets)
        summary["datasets"] = len(datasets) if datasets is not None else None

        programmatic_snapshot = None
        if args.section in {"programmatic", "all"}:
            programmatic_snapshot = _programmatic_registry_snapshot()
            _print_programmatic(programmatic_snapshot)
        summary["programmatic"] = (
            len(programmatic_snapshot.get("names", [])) if programmatic_snapshot else None
        )

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
