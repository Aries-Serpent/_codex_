from __future__ import annotations

import builtins
import importlib.util
import os
import pathlib
import random
import sys

import pytest

from codex_ml.utils.torch_checks import REINSTALL_COMMAND, inspect_torch
from tests.helpers.optional_dependencies import OPTIONAL_DEPENDENCY_REASONS

try:
    import numpy as np
except Exception:  # pragma: no cover - numpy optional
    np = None  # type: ignore[assignment]

TORCH_STATUS = None
TORCH_SKIP_REASON = ""

try:
    import torch as _torch
except Exception as exc:  # pragma: no cover - torch optional
    torch = None  # type: ignore[assignment]
    TORCH_SKIP_REASON = f"torch import failed: {exc!r}"
else:
    status = inspect_torch(_torch)
    TORCH_STATUS = status
    if status.ok:
        torch = _torch  # type: ignore[assignment]
    else:  # pragma: no cover - guard for stub installs
        TORCH_SKIP_REASON = (
            f"{status.detail}. Reinstall via: {status.reinstall_hint or REINSTALL_COMMAND}"
        )
        # Treat the stub as missing so pytest.importorskip("torch") will skip
        # affected tests instead of failing mid-import.
        sys.stderr.write(f"[tests] {TORCH_SKIP_REASON}\n")
        sys.modules["torch"] = None
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


def pytest_report_header(config: pytest.Config) -> list[str]:  # pragma: no cover - summary
    header: list[str] = []
    if TORCH_SKIP_REASON:
        header.append(f"PyTorch unavailable: {TORCH_SKIP_REASON}")
    elif TORCH_STATUS is not None and TORCH_STATUS.ok:
        details = TORCH_STATUS.summary()
        header.append(f"PyTorch detected: {details}")
    return header


def pytest_addoption(parser: pytest.Parser) -> None:  # pragma: no cover - option wiring
    parser.addoption("--runslow", action="store_true", default=False, help="run slow tests")


OPTIONAL_TEST_GROUPS: dict[str, tuple[str, ...]] = {
    "tests.checkpointing.test_schema_v2": (),
    "tests.checkpointing.test_canonical_json": (),
    "tests.checkpointing": ("torch",),
    "tests.cli": ("yaml", "omegaconf", "torch"),
    "tests.config": ("yaml", "omegaconf"),
    "tests.data.test_cache_flush_threshold": ("numpy",),
    "tests.data.test_load_dataset": ("omegaconf",),
    "tests.data.test_safety_filter": ("omegaconf",),
    "tests.eval": ("torch",),
    "tests.gates": ("omegaconf", "torch"),
    "tests.interfaces": ("omegaconf", "torch"),
    "tests.modeling": ("torch", "transformers"),
    "tests.models": ("torch", "transformers"),
    "tests.monitoring": ("omegaconf",),
    "tests.multilingual": ("transformers", "sentencepiece"),
    "tests.pipeline": ("omegaconf", "yaml", "torch"),
    "tests.privacy": ("torch",),
    "tests.smoke": ("omegaconf", "yaml"),
    "tests.tokenization": ("transformers", "sentencepiece"),
    "tests.training": ("torch", "omegaconf", "yaml"),
    "tests.test_checkpoint": ("torch",),
    "tests.test_engine_hf_trainer": ("torch", "transformers"),
    "tests.test_engine_hf_trainer_grad_accum": ("torch", "transformers"),
    "tests.test_engine_hf_trainer_lora": ("torch", "transformers", "peft"),
    "tests.test_metric_curves": ("torch",),
    "tests.test_metrics_logging": ("torch",),
    "tests.test_metrics_tb": ("torch",),
    "tests.test_modeling": ("torch",),
    "tests.test_pipeline_smoke": ("omegaconf", "yaml", "torch"),
    "tests.test_symbolic_pipeline": ("torch", "omegaconf"),
    "tests.test_tokenization": ("transformers", "sentencepiece"),
    "tests.test_tokenizer_batch_encode": ("transformers", "sentencepiece"),
    "tests.test_tokenizer_ids": ("transformers", "sentencepiece"),
    "tests.test_training_arguments_flags": ("torch", "transformers"),
}


OPTIONAL_MARKERS: dict[str, str] = {
    "requires_transformers": "transformers",
    "requires_torch": "torch",
    "requires_sentencepiece": "sentencepiece",
}


def _module_available(name: str) -> bool:
    if name == "torch" and TORCH_SKIP_REASON:
        return False
    try:
        spec = importlib.util.find_spec(name)
    except (ImportError, ValueError):
        return name in sys.modules
    return spec is not None


def _missing_modules(names: tuple[str, ...]) -> list[str]:
    missing: list[str] = []
    for name in names:
        if name == "torch" and TORCH_SKIP_REASON:
            missing.append(f"torch ({TORCH_SKIP_REASON})")
            continue
        try:
            __import__(name)
        except Exception:
            reason = OPTIONAL_DEPENDENCY_REASONS.get(name)
            if reason:
                missing.append(f"{name} ({reason})")
            else:
                missing.append(name)
    return missing


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    if not config.getoption("--runslow"):
        skip_slow = pytest.mark.skip(reason="need --runslow to run")
    else:
        skip_slow = None
    run_deferred = os.getenv("RUN_DEFERRED_TESTS", "0") == "1"
    skip_deferred = (
        None
        if run_deferred
        else pytest.mark.skip(reason="deferred module (set RUN_DEFERRED_TESTS=1 to enable)")
    )
    for item in items:
        if skip_deferred and "deferred" in item.keywords:
            item.add_marker(skip_deferred)
            continue
        if skip_slow and "slow" in item.keywords:
            item.add_marker(skip_slow)
        for marker_name, module_name in OPTIONAL_MARKERS.items():
            if item.get_closest_marker(marker_name) and not _module_available(module_name):
                reason = module_name
                if module_name == "torch" and TORCH_SKIP_REASON:
                    reason = f"torch ({TORCH_SKIP_REASON})"
                elif module_name in OPTIONAL_DEPENDENCY_REASONS:
                    reason = f"{module_name} ({OPTIONAL_DEPENDENCY_REASONS[module_name]})"
                item.add_marker(pytest.mark.skip(reason=f"optional dependency missing: {reason}"))
                break
        module_name = getattr(item.module, "__name__", "")
        for prefix, deps in OPTIONAL_TEST_GROUPS.items():
            if module_name.startswith(prefix):
                missing = _missing_modules(deps)
                if missing:
                    reason = f"optional dependency missing: {', '.join(sorted(set(missing)))}"
                    item.add_marker(pytest.mark.skip(reason=reason))
                break


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


_OPTIONAL_DEPS = [
    "zstandard",
    "pandas",
    "duckdb",
    "datasets",
    "fastapi",
    "httpx",
    "sentencepiece",
    "sklearn",
    "h5py",
]


def pytest_ignore_collect(collection_path: pathlib.Path, config: pytest.Config) -> bool:
    if not collection_path.is_file():
        return False
    try:
        text = collection_path.read_text(encoding="utf-8")
    except Exception:
        return False
    for name in _OPTIONAL_DEPS:
        if name in text:
            try:
                __import__(name)
            except Exception:
                return True
    return False


@pytest.fixture
def no_sentencepiece(monkeypatch):
    orig_import = builtins.__import__

    def fake_import(name, *a, **k):
        if name == "sentencepiece":
            raise ImportError("sentencepiece missing")
        return orig_import(name, *a, **k)

    monkeypatch.setattr(builtins, "__import__", fake_import)
    monkeypatch.delitem(sys.modules, "sentencepiece", raising=False)
    monkeypatch.delitem(sys.modules, "codex_ml.tokenization.sentencepiece_adapter", raising=False)
    yield
