from __future__ import annotations

import os
import stat
from pathlib import Path


def add_user_exec(path: str | os.PathLike[str]) -> None:
    target = Path(path)
    mode = target.stat().st_mode
    os.chmod(target, mode | stat.S_IXUSR)


__all__ = ["add_user_exec"]
