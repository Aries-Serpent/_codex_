from __future__ import annotations

import runpy
import sys
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


def eval_main() -> int:
    """Placeholder for future evaluation CLI."""
    _die("[codex-eval] not yet implemented; use evaluation modules directly for now.")
