from __future__ import annotations

import argparse
import runpy
import sys
from contextlib import suppress
from importlib import import_module
from typing import NoReturn


def _die(msg: str, code: int = 2) -> NoReturn:
    sys.stderr.write(msg + "\n")
    raise SystemExit(code)


def train_main() -> int:
    """Delegate to the Hydra training entrypoint while staying import-safe."""
    try:
        from . import hydra_main
    except Exception as exc:  # pragma: no cover - defensive
        _die(f"[codex-train] hydra_main not available: {exc}")
    try:
        main = getattr(hydra_main, "main", None)  # type: ignore[name-defined]
        if callable(main):
            return int(main())
        runpy.run_module("codex_ml.cli.hydra_main", run_name="__main__")
        return 0
    except SystemExit as exc:  # propagate exit codes cleanly
        return int(getattr(exc, "code", 0) or 0)


def _load_main(module_path: str) -> int | None:
    """Attempt to import *module_path* and call its ``main`` attribute if present."""
    with suppress(Exception):
        module = import_module(module_path)
        main_fn = getattr(module, "main", None)
        if callable(main_fn):
            return int(main_fn())  # type: ignore[no-any-return]
    return None


def _run_module(module_path: str) -> bool:
    """Execute a module via ``runpy`` and return True on success."""
    with suppress(Exception):
        runpy.run_module(module_path, run_name="__main__")
        return True
    return False


def _eval_dispatch(_namespace: argparse.Namespace) -> int:
    """Best-effort evaluation dispatcher bridging legacy modules."""
    direct = _load_main("codex_ml.training.eval")
    if direct is not None:
        return direct

    if _run_module("codex_ml.training.eval"):
        return 0

    fallback = _load_main("codex_ml.eval.evaluator")
    if fallback is not None:
        return fallback

    if _run_module("codex_ml.eval.evaluator"):
        return 0

    _die("[codex-eval] no evaluation entrypoint found or failed to run.")
    return 2


def eval_main() -> int:
    """Evaluation CLI entrypoint bridging to available evaluation modules."""
    parser = argparse.ArgumentParser(
        prog="codex-eval",
        description="Codex ML Evaluation CLI (delegates to in-repo evaluation modules)",
        add_help=True,
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Parse CLI and exit 0 (smoke test without running evaluation)",
    )
    namespace, _unknown = parser.parse_known_args()
    if namespace.dry_run:
        return 0
    return _eval_dispatch(namespace)
