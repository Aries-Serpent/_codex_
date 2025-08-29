"""Minimal CLI viewer using importlib.resources for path resolution."""
from __future__ import annotations

import argparse
import sys
try:  # Python >=3.9
    from importlib.resources import files
except Exception:  # pragma: no cover - Python<3.9
    from importlib_resources import files  # type: ignore


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Show a packaged text resource")
    ap.add_argument("--show", default="README.md")
    args = ap.parse_args(argv)
    try:
        pkg = files(__package__ or "scripts.cli")
        target = pkg.joinpath(args.show)
        data = target.read_text(encoding="utf-8")
        print(data[:2000])
        return 0
    except Exception as exc:  # pragma: no cover - path errors
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
