from __future__ import annotations
import json
import sys
from typing import Iterable
from ..detectors.aggregate import scorecard
from ..detectors.unified_training import detector_unified_training


def _default_detectors() -> Iterable:
    return [detector_unified_training]


def run(argv: list[str] | None = None) -> int:
    sc = scorecard(_default_detectors(), weights=None)
    sys.stdout.write(json.dumps(sc) + "\n")
    return 0


def main(argv: list[str] | None = None) -> int:
    # Simple command shim: `python -m codex_ml.cli.detectors run`
    args = sys.argv[1:] if argv is None else argv
    if not args or args[0] == "run":
        return run(args[1:])
    sys.stdout.write("Usage: python -m codex_ml.cli.detectors run\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
