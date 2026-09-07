"""Compatibility shim for repo-root deploy modules.

`pytest.ini` keeps imports src-first, but the live deploy scripts still live under
repo-root `deploy/`. Expose that package here so `import deploy.*` remains stable
without changing the canonical project layout.
"""

from __future__ import annotations

from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
_ROOT_DEPLOY = _ROOT / "deploy"
if _ROOT_DEPLOY.exists():
    __path__ = [str(Path(__file__).resolve().parent), str(_ROOT_DEPLOY)]

__all__: list[str] = []
