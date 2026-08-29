"""List Codex ML plugins with structured logging and safe fallbacks."""

from __future__ import annotations

import argparse
import contextlib
import io
import json
import logging
import sys
import warnings

logger = logging.getLogger(__name__)

from collections.abc import Iterable, Sequence
from typing import Any, Optional

from codex.logging.structured_logger import logger

_JSON_EPILOG = (
    "JSON schema:\n"
    "{\n"
    '  "programmatic": {"discovered": [<str>...], "names": [<str>...]},\n'
    '  "legacy": {"models": [<str>...], "tokenizers": [<str>...], "datasets": [<str>...] }\n'
    "}\n"
)


def _json_mode_requested(args: Sequence[str]) -> bool:
    """Return ``True`` when ``args`` explicitly request ``--format json``."""

    for index, arg in enumerate(args):
        if arg == "--format" and index + 1 < len(args) and args[index + 1] == "json":
            return True
        if arg == "--format=json":
            return True
    return False


def _list_models_safe() -> list[str]:
    try:
        from codex_ml.registry import list_models
    except (ImportError, AttributeError):
        logger.warning("Exception occurred", exc_info=True)
        return []
    try:
        return sorted({str(model) for model in list_models()})
    except (ImportError, AttributeError):
        logger.warning("Exception occurred", exc_info=True)
        return []


def _list_tokenizers_safe() -> list[str]:
    try:
        from codex_ml.registry import list_tokenizers
    except (ImportError, AttributeError):
        logger.warning("Exception occurred", exc_info=True)
        return []
    try:
        return sorted({str(tokenizer) for tokenizer in list_tokenizers()})
    except (ImportError, AttributeError):
        logger.warning("Exception occurred", exc_info=True)
        return []


def _list_datasets_safe() -> list[str]:
    try:
        from codex_ml.data.registry import list_datasets
    except (ImportError, AttributeError):
        logger.warning("Exception occurred", exc_info=True)
        return []
    try:
        return sorted({str(dataset) for dataset in list_datasets()})
    except (ValueError, TypeError, RuntimeError):
        logger.warning("Exception occurred", exc_info=True)
        return []


def _programmatic_registry_snapshot(*, discover: bool = True) -> dict[str, Any]:
    snapshot: dict[str, Any] = {"names": [], "discovered": []}
    try:
        from codex_ml.plugins import programmatic
    except (ImportError, AttributeError):
        logger.warning("Exception occurred", exc_info=True)
        return snapshot

    try:
        registry = programmatic.registry()
    except (ValueError, TypeError, RuntimeError):
        logger.warning("Exception occurred", exc_info=True)
        return snapshot

    discovered_items: list[str] = []
    if discover:
        try:
            discovered = registry.discover()
        except (ValueError, TypeError, RuntimeError):
            logger.warning("Exception occurred", exc_info=True)
            discovered_items = []
        else:
            if isinstance(discovered, dict):
                discovered_items = [f"{key}={value}" for key, value in discovered.items()]
            elif isinstance(discovered, (list, tuple, set)):
                discovered_items = [str(item) for item in discovered]
            elif discovered not in (None, False):
                discovered_items = [str(discovered)]
    snapshot["discovered"] = sorted({item for item in discovered_items if item})

    try:
        if hasattr(registry, "names"):
            iterable = registry.names()
        else:
            iterable = [plugin.name() for plugin in registry.all()]
    except (ValueError, TypeError, RuntimeError):
        logger.warning("Exception occurred", exc_info=True)
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
    logger.info(header)
    printed = False
    for item in items:
        logger.info(f"  - {item}")
        printed = True
    if not printed:
        logger.info("  (none)")


def _print_programmatic(snapshot: dict[str, Any]) -> None:
    names = snapshot.get("names", []) or []
    discovered = snapshot.get("discovered", []) or []
    _print_lines("Programmatic", names)
    if discovered:
        logger.info("  discovered:")
        for item in discovered:
            logger.info(f"    - {item}")


def _build_parser():
    from codex_ml.codex_structured_logging import ArgparseJSONParser

    return ArgparseJSONParser(
        description="List Codex ML plugin registries",
        epilog=_JSON_EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )


def main(argv: Optional[Sequence[str]] = None) -> int:
    arg_list = list(argv) if argv is not None else sys.argv[1:]
    if _json_mode_requested(arg_list):
        logging.disable(logging.CRITICAL)
        warnings.filterwarnings(
            "ignore",
            message="env_file not supported when pydantic_settings unavailable",
            category=UserWarning,
        )

    from codex_ml.codex_structured_logging import capture_exceptions, init_json_logging, log_event

    @capture_exceptions
    def _run(parsed_args: Sequence[str]) -> int:
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

        args = parser.parse_args(list(parsed_args))
        emit_logs = args.format != "json"
        if not emit_logs:
            root_logger = logging.getLogger()
            root_logger.setLevel(logging.CRITICAL + 1)

        if emit_logs:
            log_event(logger, "cli.start", prog=parser.prog, args=list(parsed_args))

        include_models = args.format == "json" or args.section in {"models", "all"}
        include_tokenizers = args.format == "json" or args.section in {"tokenizers", "all"}
        include_datasets = args.format == "json" or args.section in {"datasets", "all"}
        include_programmatic = args.format == "json" or args.section in {
            "programmatic",
            "all",
        }

        with contextlib.ExitStack() as stack:
            if not emit_logs:
                stack.enter_context(contextlib.redirect_stderr(io.StringIO()))
                stack.enter_context(warnings.catch_warnings())
                warnings.simplefilter("ignore")

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
            "programmatic": (len(programmatic.get("names", [])) if include_programmatic else None),
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
            logger.info(json.dumps(payload, indent=2))
            if emit_logs:
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
                logger.info(name)
            if emit_logs:
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

        if emit_logs:
            log_event(logger, "cli.finish", prog=parser.prog, status="ok", summary=summary)
        return 0

    return _run(arg_list)


if __name__ == "__main__":  # pragma: no cover - CLI entry
    raise SystemExit(main())
