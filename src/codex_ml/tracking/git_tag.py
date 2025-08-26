# BEGIN: CODEX_GIT_TAG
from __future__ import annotations

import subprocess


def current_commit() -> str | None:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    except Exception:
        return None


# END: CODEX_GIT_TAG
