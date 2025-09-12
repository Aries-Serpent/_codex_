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
    for item in items:
        if skip_slow and "slow" in item.keywords:
            item.add_marker(skip_slow)


def _gpu_available() -> bool:
    try:
        import torch  # noqa: F401
        import torch.cuda as _cuda  # noqa: F401

        return hasattr(_cuda, "is_available") and _cuda.is_available()
    except Exception:
        return False


@pytest.hookimpl(tryfirst=True)
def pytest_runtest_setup(item: pytest.Item) -> None:
    """
    Policy:
      - GPU tests are *skipped by default* (Codex has no GPU).
      - Set RUN_GPU_TESTS=1 to opt-in.
      - If RUN_GPU_TESTS=1 but no GPU is actually present, print a friendly message and skip.
      - Network tests are skipped by default; opt-in with RUN_NET_TESTS=1.
    """
    if "gpu" in item.keywords:
        want_gpu = os.getenv("RUN_GPU_TESTS", "0") == "1"
        have_gpu = _gpu_available()
        if not want_gpu:
            item.add_marker(
                pytest.mark.skip(
                    reason="GPU test skipped by default (RUN_GPU_TESTS!=1). Codex has no GPU."
                )
            )
            return
        if not have_gpu:
            print(
                "\n[tests] You set RUN_GPU_TESTS=1, but no CUDA GPU is available in this environment. "
                "Skipping GPU-marked test gracefully."
            )
            item.add_marker(pytest.mark.skip(reason="RUN_GPU_TESTS=1 but no CUDA GPU available."))
            return

    if "net" in item.keywords:
        want_net = os.getenv("RUN_NET_TESTS", "0") == "1"
        if not want_net:
            item.add_marker(
                pytest.mark.skip(reason="Network test skipped by default (RUN_NET_TESTS!=1).")
            )


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
