"""Module entrypoint for `python -m codex_ml`.

Provides a friendly pointer to the package-style CLI and exits 0.
This avoids coupling to any specific subcommand loader.
"""

from __future__ import annotations

import sys


BANNER = """
codex-ml
========
This package exposes a package-style CLI.

Usage:
  python -m codex_ml.cli --help
  python -m codex_ml.cli <subcommand> [args]
""".strip()


def main(argv: list[str] | None = None) -> int:
    print(BANNER)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
