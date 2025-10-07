"""
Test helper to ensure ``src/`` is importable and configure offline MLflow defaults.
"""

from __future__ import annotations

import sys
from pathlib import Path

_root = Path(__file__).resolve().parent
_src = _root / "src"
if _src.exists():
    src_str = str(_src)
    if src_str not in sys.path:
        sys.path.insert(0, src_str)

try:  # Optional MLflow helpers depend on src/ being importable
    from codex_ml.utils.experiment_tracking_mlflow import ensure_local_tracking
except Exception:  # pragma: no cover - fallback when utilities unavailable

    def ensure_local_tracking() -> None:
        return None


try:  # pragma: no cover - optional pytest availability
    from _pytest.monkeypatch import MonkeyPatch, notset
except Exception:  # pragma: no cover - fallback when pytest unavailable
    MonkeyPatch = None  # type: ignore[assignment]
else:
    if MonkeyPatch is not None and not hasattr(MonkeyPatch.setitem, "__wrapped_patch__"):
        _orig_setitem = MonkeyPatch.setitem

        def _patched_setitem(self, dic, name, value, raising=True):  # type: ignore[override]
            prev = dic.get(name, notset)
            self._setitem.append((dic, name, prev))
            dic[name] = value  # type: ignore[index]

        _patched_setitem.__wrapped_patch__ = True  # type: ignore[attr-defined]
        MonkeyPatch.setitem = _patched_setitem  # type: ignore[assignment]

ensure_local_tracking()
