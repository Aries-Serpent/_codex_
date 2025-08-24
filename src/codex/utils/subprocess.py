"""Safe wrappers around :mod:`subprocess` calls."""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Sequence


def run(
    cmd: Sequence[str],
    *,
    cwd: Path | None = None,
    capture_output: bool = False,
    text: bool = True,
    check: bool = True,
) -> subprocess.CompletedProcess[str]:
    """Run *cmd* securely.

    Parameters mirror :func:`subprocess.run` but ``shell`` is always ``False`` and
    ``check`` defaults to ``True`` to ensure errors are surfaced.
    """
    return subprocess.run(  # nosec B603
        list(cmd),
        cwd=cwd,
        capture_output=capture_output,
        text=text,
        check=check,
        shell=False,
    )
