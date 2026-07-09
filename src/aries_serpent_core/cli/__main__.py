"""Make the codex.cli package executable with python -m codex.cli"""

from __future__ import annotations

# Import the Click CLI from src/codex/cli.py and run it
from aries_serpent_core.cli import cli

if __name__ == "__main__":
    cli()
