"""List Codex ML plugins with deterministic stdout/stderr contract."""

from __future__ import annotations

import argparse
import json
import logging
import sys
from collections.abc import Iterable, Sequence
from typing import Any

from codex_ml.codex_structured_logging import capture_exceptions, configure_cli_logging

LOGGER = logging.getLogger(__name__)


def _collect_legacy() -> dict[str, list[str]]:
    """Return legacy registries as a mapping of {group: [names]}.

    Missing registries yield empty lists to keep the output schema stable.
    """

    try:
        from codex_ml.plugins import registries  # type: ignore[attr-defined]
    except Exception:  # pragma: no cover - optional dependency not available
        return {
            "tokenizers": [],
            "models": [],
            "datasets": [],
            "metrics": [],
            "trainers": [],
            "reward_models": [],
            "rl_agents": [],
        }

    groups = (
        "tokenizers",
        "models",
        "datasets",
        "metrics",
        "trainers",
        "reward_models",
        "rl_agents",
    )
    result: dict[str, list[str]] = {}
    for name in groups:
        registry = getattr(registries, name, None)
        items: list[str]
        if registry is None:
            items = []
        else:
            try:
                raw = registry.names()  # type: ignore[attr-defined]
            except Exception:
                items = []
            else:
                items = sorted(str(item) for item in raw)
        result[name] = items
    return result


def _collect_programmatic(*, discover: bool = True) -> dict[str, Any]:
    """Return the programmatic plugin registry snapshot."""

    result: dict[str, Any] = {"discovered": 0, "names": []}
    try:
        from codex_ml.plugins import programmatic  # type: ignore[attr-defined]
    except Exception:  # pragma: no cover - optional dependency not available
        return result

    try:
        reg = programmatic.registry()
    except Exception:
        return result

    if discover:
        try:
            discovered = reg.discover()
        except Exception as error:
            LOGGER.debug("Programmatic discovery failed", exc_info=error)
            result["discovered"] = 0
        else:
            try:
                result["discovered"] = int(discovered)
            except Exception:
                result["discovered"] = 0

    try:
        names = [plugin.name() for plugin in reg.all()]  # type: ignore[attr-defined]
    except Exception:
        names = []
    result["names"] = sorted({str(name) for name in names})
    return result


def _unique(iterables: Iterable[Iterable[str]]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for items in iterables:
        for item in items:
            if item not in seen:
                seen.add(item)
                ordered.append(item)
    return ordered


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="List Codex ML plugin registries",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "JSON schema:\n"
            "{\n"
            '  "programmatic": {"discovered": <int>, "names": [<str>...]},\n'
            '  "legacy": {"tokenizers": [<str>...], "models": [<str>...], ...},\n'
            '  "options": {"discover": <bool>, "names_only": <bool>, "format": "json"}\n'
            "}\n"
        ),
    )
    parser.add_argument("--format", choices=["text", "json"], default="text", help="Output format")
    parser.add_argument("--no-discover", action="store_true", help="Disable programmatic discovery")
    parser.add_argument(
        "--names-only", action="store_true", help="Emit only plugin names (text mode)"
    )
    return parser


@capture_exceptions
def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)

    quiet = args.format == "json" or args.names_only
    configure_cli_logging(stream=sys.stderr, quiet=quiet)

    programmatic = _collect_programmatic(discover=not args.no_discover)
    legacy = _collect_legacy()

    if args.format == "json":
        payload = {
            "programmatic": programmatic,
            "legacy": legacy,
            "options": {
                "discover": not args.no_discover,
                "names_only": args.names_only,
                "format": "json",
            },
        }
        print(json.dumps(payload, indent=2))
        return 0

    if args.names_only:
        names = _unique([programmatic.get("names", []), *legacy.values()])
        if not names:
            print("(none)")
            return 0
        for name in names:
            print(name)
        return 0

    prog_names = programmatic.get("names", [])
    print(f"programmatic: {', '.join(prog_names) if prog_names else '(none)'}")
    for section in sorted(legacy.keys()):
        items = legacy[section]
        print(f"{section}: {', '.join(items) if items else '(none)'}")

    if not quiet:
        LOGGER.info("Listed plugins successfully")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
