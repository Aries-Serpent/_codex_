from __future__ import annotations

import builtins
import os
import random
import sys

import pytest

try:
    import numpy as np
except Exception:  # pragma: no cover - numpy optional
    np = None  # type: ignore[assignment]

try:
    import torch
except Exception:  # pragma: no cover - torch optional
    torch = None  # type: ignore[assignment]


def pytest_configure(config: pytest.Config) -> None:  # pragma: no cover - setup
    seed = 123
    random.seed(seed)
    os.environ.setdefault("PYTHONHASHSEED", str(seed))
    if np is not None:
        np.random.seed(seed)
    if torch is not None:
        torch.manual_seed(seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(seed)


def pytest_addoption(parser: pytest.Parser) -> None:  # pragma: no cover - option wiring
    parser.addoption("--runslow", action="store_true", default=False, help="run slow tests")


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    if not config.getoption("--runslow"):
        skip_slow = pytest.mark.skip(reason="need --runslow to run")
    else:
        skip_slow = None
    has_cuda = bool(torch and torch.cuda.is_available())
    skip_gpu = pytest.mark.skip(reason="CUDA required")
    for item in items:
        if skip_slow and "slow" in item.keywords:
            item.add_marker(skip_slow)
        if "gpu" in item.keywords and not has_cuda:
            item.add_marker(skip_gpu)


@pytest.fixture(autouse=True)
def _isolate_env(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("HOME", str(tmp_path))
    yield


@pytest.fixture
def no_sentencepiece(monkeypatch):
    orig_import = builtins.__import__

    def fake_import(name, *a, **k):
        if name == "sentencepiece":
            raise ImportError("sentencepiece missing")
        return orig_import(name, *a, **k)

    monkeypatch.setattr(builtins, "__import__", fake_import)
    monkeypatch.delitem(sys.modules, "sentencepiece", raising=False)
    yield
