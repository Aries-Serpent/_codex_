"""
  Main   Module

This module provides functionality for   main  .

Usage:
    from cli.__main__ import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

from codex_ml.cli import main as cli_main

if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(cli_main())  # type: ignore[operator]
