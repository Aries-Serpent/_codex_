# conftest.py
# Make PyTorch 2.6+ behave like pre-2.6 for our test suite:
# https://pytorch.org/docs/stable/serialization.html#troubleshooting
import os as _os
import sys as _sys
from pathlib import Path as _Path

_SRC_DIR = _Path(__file__).resolve().parent / "src"
if _SRC_DIR.exists():
    # Ensure in-process imports see ``src`` modules without installing the package.
    _src = str(_SRC_DIR)
    if _src not in _sys.path:
        _sys.path.insert(0, _src)
    # Propagate to subprocesses invoked by tests (e.g., ``python -m tokenization.cli``).
    existing = _os.environ.get("PYTHONPATH")
    if existing:
        if _src not in existing.split(_os.pathsep):
            _os.environ["PYTHONPATH"] = _src + _os.pathsep + existing
    else:
        _os.environ["PYTHONPATH"] = _src

_os.environ.setdefault("TORCH_FORCE_NO_WEIGHTS_ONLY_LOAD", "1")


def _gpu_available() -> bool:
    try:
        import torch  # type: ignore

        return bool(getattr(torch, "cuda", None) and torch.cuda.is_available())
    except Exception:
        return False


def pytest_report_header(config):
    # If the user *forces* GPU tests (e.g., -m "gpu" or -m "gpu and ..."),
    # but there is no GPU/CUDA available, print a friendly heads-up.
    marker_expr = (config.getoption("-m") or "").strip()
    # Heuristic: "gpu" present and not explicitly negated.
    wants_gpu = ("gpu" in marker_expr) and ("not gpu" not in marker_expr)
    if wants_gpu and not _gpu_available():
        return (
            "⚠️  GPU tests were requested (-m 'gpu'), but no CUDA/GPU was detected.\n"
            "    Running with CPU-only torch; GPU tests may be skipped or slow.\n"
            "    Tip: on GPU runners, include `gpu` in CODEX_SYNC_GROUPS and install a CUDA wheel."
        )
    return None
