from __future__ import annotations

import subprocess
import sys

SCRIPT = """
import sys
from codex_ml.codex_structured_logging import capture_exceptions, configure_cli_logging

configure_cli_logging(quiet=True)

@capture_exceptions
def main():
    raise SystemExit(0)

if __name__ == "__main__":
    sys.exit(main())
"""


def test_capture_exceptions_handles_system_exit_zero() -> None:
    proc = subprocess.run([sys.executable, "-c", SCRIPT], capture_output=True, text=True)
    assert proc.returncode == 0
    assert "Unhandled exception" not in proc.stderr
