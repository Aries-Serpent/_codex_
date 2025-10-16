from __future__ import annotations

import argparse
import json
import os
import platform
import runpy
import sys
from importlib import import_module
from typing import Any, NoReturn

try:  # pragma: no cover - structured logging is optional offline
    from codex_ml.codex_structured_logging import (
        ArgparseJSONParser,
        capture_exceptions,
        init_json_logging,
        log_event,
    )
except Exception:  # pragma: no cover - degrade gracefully without structured logging
    ArgparseJSONParser = None  # type: ignore[assignment]

    def init_json_logging():  # type: ignore[override]
        class _NullLogger:
            def info(self, *_a: object, **_k: object) -> None:
                return None

            def warning(self, *_a: object, **_k: object) -> None:
                return None

            def error(self, *_a: object, **_k: object) -> None:
                return None

        return _NullLogger()

    def log_event(*_a: object, **_k: object) -> None:  # type: ignore[override]
        return None

    class _CaptureContext:
        def __enter__(self) -> None:  # pragma: no cover - trivial branch
            return None

        def __exit__(self, *_exc: object) -> bool:  # pragma: no cover - trivial branch
            return False

    def capture_exceptions(logger=None, **_kwargs):  # type: ignore[override]
        if callable(logger) and not isinstance(logger, type):
            return logger
        return _CaptureContext()


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


def _probe_payload() -> dict[str, Any]:
    return {
        "ok": True,
        "component": "codex-eval",
        "python": ".".join(map(str, sys.version_info[:3])),
        "platform": platform.platform(),
        "details": {
            "env_override": bool(os.environ.get("CODEX_EVAL_ENTRY")),
        },
    }


def eval_main() -> int:
    """Evaluation CLI entrypoint bridging to available evaluation modules."""
    parser_cls = ArgparseJSONParser if ArgparseJSONParser is not None else argparse.ArgumentParser
    parser = parser_cls(
        prog="codex-eval",
        description="Codex ML Evaluation CLI (delegates to in-repo evaluation modules)",
        add_help=True,
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Parse CLI and exit 0 (smoke test without running evaluation)",
    )
    parser.add_argument(
        "--probe-json",
        action="store_true",
        help=argparse.SUPPRESS,
    )

    logger = init_json_logging()
    with capture_exceptions(logger):
        log_event(logger, "cli.start", prog=parser.prog, args=sys.argv[1:])
        namespace, _unknown = parser.parse_known_args()
        if namespace.dry_run:
            log_event(
                logger,
                "cli.finish",
                prog=parser.prog,
                status="ok",
                mode="dry-run",
                rc=0,
            )
            return 0
        if namespace.probe_json:
            print(json.dumps(_probe_payload()))
            log_event(
                logger,
                "cli.finish",
                prog=parser.prog,
                status="ok",
                mode="probe-json",
                rc=0,
            )
            return 0
        override = os.environ.get("CODEX_EVAL_ENTRY")
        override_failed = False
        override_error: str | None = None
        if override:
            try:
                rc = _dispatch_from_spec(override)
                log_event(
                    logger,
                    "cli.finish",
                    prog=parser.prog,
                    status="ok" if rc == 0 else "error",
                    override=True,
                    rc=rc,
                )
                return rc
            except SystemExit as exc:  # Allow module-level exits to propagate cleanly
                rc = int(getattr(exc, "code", 0) or 0)
                log_event(
                    logger,
                    "cli.finish",
                    prog=parser.prog,
                    status="ok" if rc == 0 else "error",
                    override=True,
                    rc=rc,
                )
                return rc
            except Exception as exc:
                sys.stderr.write(f"[codex-eval] env override failed ({override}): {exc}\n")
                override_failed = True
                override_error = str(exc)
        try:
            rc = _eval_dispatch(namespace)
        except SystemExit as exc:
            rc = int(getattr(exc, "code", 0) or 0)
            payload = {
                "prog": parser.prog,
                "status": "ok" if rc == 0 else "error",
                "rc": rc,
            }
            if override:
                payload["override"] = True
            if override_failed:
                payload["override_failed"] = True
                if override_error:
                    payload["override_error"] = override_error
            log_event(logger, "cli.finish", **payload)
            raise
        payload = {
            "prog": parser.prog,
            "status": "ok" if rc == 0 else "error",
            "rc": rc,
        }
        if override:
            payload["override"] = True
        if override_failed:
            payload["override_failed"] = True
            if override_error:
                payload["override_error"] = override_error
        log_event(logger, "cli.finish", **payload)
        return rc
