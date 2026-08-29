"""Configure sys.path so that 'services.msp_gateway.*' is importable.

The top-level `services` package is found in `src/services` (because pytest adds
`src` first). We extend its `__path__` to include the repo-root `services/`
directory so that `services.msp_gateway` resolves correctly.
"""

from __future__ import annotations

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]
_ROOT_SERVICES = str(_REPO_ROOT / "services")

# Ensure repo root is on sys.path
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

# Also extend the services package __path__ so sub-packages from BOTH
# src/services/ and services/ are discoverable under the `services` namespace.
try:
    import services as _svc_pkg

    if hasattr(_svc_pkg, "__path__") and _ROOT_SERVICES not in _svc_pkg.__path__:
        _svc_pkg.__path__.append(_ROOT_SERVICES)
except ImportError:
    # Some focused test runs may not have the namespace package importable yet.
    pass
