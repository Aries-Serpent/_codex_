import importlib.util
import os
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
if (repo_str := str(REPO_ROOT)) in sys.path:
    sys.path.remove(repo_str)
    sys.path.append(repo_str)


def _is_stub_spec(spec: importlib.machinery.ModuleSpec | None, name: str) -> bool:
    if spec is None:
        return False
    origin = getattr(spec, "origin", None)
    if not origin:
        return False
    try:
        return Path(origin).resolve().is_relative_to(REPO_ROOT / name)
    except OSError:
        return False


if os.environ.get("CODEX_CLI_LIGHTWEIGHT", "0") != "1":
    required = ("yaml", "omegaconf", "hydra")
    missing = [
        name
        for name in required
        if (spec := importlib.util.find_spec(name)) is None or _is_stub_spec(spec, name)
    ]
    if missing:
        raise SystemExit(0)

    spec = importlib.util.find_spec("torch")
    if spec is None or _is_stub_spec(spec, "torch"):
        raise SystemExit(0)
