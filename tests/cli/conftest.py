import importlib.util

import pytest

pytest.importorskip("yaml")
pytest.importorskip("omegaconf")
pytest.importorskip("hydra")

spec = importlib.util.find_spec("torch")
if spec is None:
    pytest.skip("torch not installed", allow_module_level=True)

try:
    import torch  # noqa: F401  # ensure torch import succeeds
    from torch.utils.data import Dataset  # noqa: F401
except Exception:  # pragma: no cover - incomplete builds
    pytest.skip(
        "incomplete torch build (missing torch.utils dependencies)",
        allow_module_level=True,
    )
