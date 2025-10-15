from __future__ import annotations

import argparse
import os
import runpy
import sys
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


def _load_main(module_path: str, failures: list[str]) -> int | None:
    """Attempt to import *module_path* and call its ``main`` attribute if present."""

    try:
        module = import_module(module_path)
    except Exception as exc:  # pragma: no cover - import failures are rare
        failures.append(f"{module_path}: import failed ({exc})")
        return None

    main_fn = getattr(module, "main", None)
    if not callable(main_fn):
        return None

    try:
        result = main_fn()
    except SystemExit:
        raise
    except Exception as exc:
        failures.append(f"{module_path}.main() raised {exc!r}")
        return None

    try:
        return int(result)  # type: ignore[arg-type]
    except Exception as exc:
        failures.append(f"{module_path}.main() returned non-int value ({exc})")
        return None


def _run_module(module_path: str, failures: list[str]) -> bool:
    """Execute a module via ``runpy`` and return True on success."""

    try:
        runpy.run_module(module_path, run_name="__main__")
        return True
    except SystemExit:
        raise
    except Exception as exc:
        failures.append(f"{module_path}: execution failed ({exc})")
        return False


def _dispatch_from_spec(spec: str) -> int:
    """Load and execute ``module[:callable]`` targets."""

    module_path, _, attr = spec.partition(":")
    if not module_path:
        raise ValueError("CODEX_EVAL_ENTRY is missing a module path")

    if attr:
        module = import_module(module_path)
        target = getattr(module, attr, None)
        if not callable(target):
            raise RuntimeError(f"{spec} is not callable")
        result = target()
        return int(result) if result is not None else 0

    runpy.run_module(module_path, run_name="__main__")
    return 0


def _eval_dispatch(_namespace: argparse.Namespace) -> int:
    """Best-effort evaluation dispatcher bridging legacy modules.

    Attempts, in order:
    1. ``codex_ml.training.eval:main``
    2. ``python -m codex_ml.training.eval``
    3. ``codex_ml.eval.evaluator:main``
    4. ``python -m codex_ml.eval.evaluator``
    """

    failures: list[str] = []

    direct = _load_main("codex_ml.training.eval", failures)
    if direct is not None:
        return direct

    if _run_module("codex_ml.training.eval", failures):
        return 0

    fallback = _load_main("codex_ml.eval.evaluator", failures)
    if fallback is not None:
        return fallback

    if _run_module("codex_ml.eval.evaluator", failures):
        return 0

    detail = "; ".join(failures) if failures else "no candidate modules resolved"
    _die(f"[codex-eval] no evaluation entrypoint found or failed to run ({detail}).")
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
    override = os.environ.get("CODEX_EVAL_ENTRY")
    if override:
        try:
            return _dispatch_from_spec(override)
        except SystemExit as exc:  # Allow module-level exits to propagate cleanly
            return int(getattr(exc, "code", 0) or 0)
        except Exception as exc:
            sys.stderr.write(f"[codex-eval] env override failed ({override}): {exc}\n")
    return _eval_dispatch(namespace)
