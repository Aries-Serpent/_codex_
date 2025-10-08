"""Utility to smoke-test that important Codex ML modules import cleanly."""

from __future__ import annotations

import argparse
import importlib
from typing import Iterable, List

_DEFAULT_MODULES = [
    "codex_ml",
    "codex_ml.training.unified_training",
    "codex_ml.tracking.guards",
    "codex_ml.metrics.api",
    "codex_ml.tokenization.api",
]


def check_modules(modules: Iterable[str]) -> List[tuple[str, bool, str | None]]:
    results: List[tuple[str, bool, str | None]] = []
    for name in modules:
        try:
            importlib.import_module(name)
        except Exception as exc:
            results.append((name, False, f"{exc.__class__.__name__}: {exc}"))
        else:
            results.append((name, True, None))
    return results


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "modules",
        nargs="*",
        help="Optional dotted module paths to import. Defaults to a curated set.",
    )
    parser.add_argument(
        "--fail-fast",
        action="store_true",
        help="Return a non-zero exit code on the first failure.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    modules = args.modules or list(_DEFAULT_MODULES)
    failures = 0
    for name, ok, error in check_modules(modules):
        status = "ok" if ok else "error"
        if ok:
            print(f"{status}: {name}")
        else:
            print(f"{status}: {name} -> {error}")
            failures += 1
            if args.fail_fast:
                return 1
    return 0 if failures == 0 else 1


if __name__ == "__main__":  # pragma: no cover - CLI entry
    raise SystemExit(main())
