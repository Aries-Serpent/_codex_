"""Configure imports for services.ita test package."""

from __future__ import annotations

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]
_ROOT_SERVICES = str(_REPO_ROOT / "services")

if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

try:
    import services as _services

    if hasattr(_services, "__path__") and _ROOT_SERVICES not in _services.__path__:
        _services.__path__.append(_ROOT_SERVICES)
except ImportError:
    # Some focused test runs may not have the namespace package importable yet.
    pass
