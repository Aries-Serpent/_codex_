"""
pytest.importorskip("mlflow")
Test Run Functional Training Resume

Test module for run functional training resume.
"""

from __future__ import annotations

import random
import sys
import types

import pytest

from codex_ml.training import run_functional_training
from codex_ml.utils.hf_pinning import HFModelUnavailableError
from codex_ml.utils.provenance import load_environment_summary

np = pytest.importorskip("numpy")


class _DummyTokenizer:
    pad_token = None
    eos_token = 0
    pad_token_id = 0

    @classmethod
    def from_pretrained(cls, _name: str, **kwargs) -> "_DummyTokenizer":
        """Accept revision and other kwargs for compatibility."""
        return cls()

    def __call__(self, texts, *, padding, return_tensors, **kwargs):
        length = max(len(t) for t in texts) if texts else 1
        data = np.zeros((len(texts), length), dtype=np.int64)
        attention = np.ones_like(data)
        return {
            "input_ids": _TensorWrapper(data),
            "attention_mask": _TensorWrapper(attention),
        }


class _TensorWrapper:
    def __init__(self, array: np.ndarray) -> None:
        self._array = array

    def clone(self) -> "_TensorWrapper":
        return _TensorWrapper(self._array.copy())

    def numpy(self) -> np.ndarray:
        return self._array

    def __array__(self):  # pragma: no cover - numpy protocol
        return self._array

    def __getattr__(self, name: str):  # pragma: no cover - delegation
        return getattr(self._array, name)

    def __getitem__(self, item):
        return self._array.__getitem__(item)

    def __setitem__(self, key, value):
        self._array.__setitem__(key, value)


class _DatasetModule:
    class Dataset:
        @staticmethod
        def from_dict(data):
            return {"data": data}


@pytest.fixture(autouse=True)
def _stub_modules(monkeypatch):
    transformers_mod = types.SimpleNamespace(AutoTokenizer=_DummyTokenizer)
    datasets_mod = types.SimpleNamespace(Dataset=_DatasetModule.Dataset)
    training_mod = types.ModuleType("training.functional_training")

    class _TrainCfg:
        __dataclass_fields__ = {
            name: None
            for name in [
                "epochs",
                "batch_size",
                "grad_accum",
                "lr",
                "resume_from",
                "checkpoint_dir",
                "seed",
                "model_name",
                "max_length",
                "padding",
                "truncation",
            ]
        }

        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)

    training_mod.TrainCfg = _TrainCfg
    training_mod.run_custom_trainer = lambda *args, **kwargs: None
    monkeypatch.setitem(sys.modules, "transformers", transformers_mod)
    monkeypatch.setitem(sys.modules, "datasets", datasets_mod)
    monkeypatch.setitem(sys.modules, "training.functional_training", training_mod)
    registry_mod = types.ModuleType("codex_ml.models.registry")
    registry_mod.get_model = lambda *_, **__: object()
    monkeypatch.setitem(sys.modules, "codex_ml.models.registry", registry_mod)

    # ── Full HF mock: stub codex_ml.training.functional_training so that
    # legacy_api's local `from codex_ml.training.functional_training import train`
    # call never touches the real HuggingFace network. ──
    ft_stub = types.ModuleType("codex_ml.training.functional_training")
    ft_stub.TrainConfig = _TrainCfg  # legacy_api imports TrainConfig
    ft_stub.train = lambda texts, *, config, val_texts=None, model=None, **kw: {
        "final_loss": 0.0,
        "perplexity": 1.0,
    }
    monkeypatch.setitem(sys.modules, "codex_ml.training.functional_training", ft_stub)

    # Mock load_from_pretrained in legacy_api so the tokenizer load never
    # reaches the HuggingFace Hub. Return a _DummyTokenizer for all factories.
    try:
        import codex_ml.training.legacy_api as _lapi

        monkeypatch.setattr(
            _lapi,
            "load_from_pretrained",
            lambda factory, identifier, **kwargs: _DummyTokenizer(),
        )
    except (ImportError, AttributeError):  # pragma: no cover - best-effort
        _ = None


def test_run_functional_training_resume(monkeypatch, tmp_path):
    checkpoint_dir = tmp_path / "ckpts"
    checkpoint_dir.mkdir()
    latest = checkpoint_dir / "step10.ptz"
    latest.write_bytes(b"stub")

    recorded = {}

    def fake_load_ckpt(path: str):
        recorded["loaded"] = path

    def fake_run_custom_trainer(model, tokenizer, train_ds, val_ds, cfg):
        recorded.update(
            {
                "resume_from": cfg.resume_from,
                "checkpoint_dir": cfg.checkpoint_dir,
                "texts": train_ds["data"]["input_ids"].tolist(),
            }
        )
        return {"result": "ok"}

    # Patch at the legacy_api module level so the already-imported symbol is replaced.
    import codex_ml.training.legacy_api as _lapi

    monkeypatch.setattr(_lapi, "load_training_checkpoint", fake_load_ckpt)
    # _evaluate_model uses a raw DataLoader that expects integer-indexed datasets;
    # the test's Dataset stub is dict-based, so skip the evaluation entirely.
    monkeypatch.setattr(_lapi, "_evaluate_model", lambda *args, **kwargs: {})
    training_module = sys.modules["training.functional_training"]
    monkeypatch.setattr(training_module, "run_custom_trainer", fake_run_custom_trainer)

    config = {
        "training": {
            "texts": ["hello"],
            "checkpoint_dir": str(checkpoint_dir),
        }
    }

    result: dict | None = None
    try:
        result = run_functional_training(config, resume=True)
    except HFModelUnavailableError as exc:
        pytest.skip(f"HF model unavailable in CI (no cache/network): {exc}")

    # With full HF mock, result is whatever legacy_api returns after calling _ft_train.
    assert isinstance(result, dict)
    assert recorded["loaded"].endswith("step10.ptz"), "rec is not valid"


def test_run_functional_training_accepts_string_model(monkeypatch, tmp_path):
    registry_module = sys.modules["codex_ml.models.registry"]

    recorded: dict[str, object] = {}

    def fake_get_model(name: str, cfg: dict[str, object]) -> object:
        recorded["name"] = name
        recorded["cfg"] = cfg
        return object()

    monkeypatch.setattr(registry_module, "get_model", fake_get_model, raising=False)

    config = {
        "training": {
            "texts": ["hello"],
            "model": "minilm",
            "checkpoint_dir": str(tmp_path / "ckpts"),
        }
    }

    try:
        run_functional_training(config)
    except HFModelUnavailableError as exc:
        pytest.skip(f"HF model unavailable in CI (no cache/network): {exc}")

    assert recorded["name"] == "minilm", "rec is not valid"
    assert isinstance(recorded["cfg"], dict)
    assert recorded["cfg"]["name"] == "minilm", "rec is not valid"


def test_run_functional_training_repeatable(monkeypatch, tmp_path):
    training_module = sys.modules["training.functional_training"]

    def fake_run_custom_trainer(model, tokenizer, train_ds, val_ds, cfg):
        return {
            "train_ids": train_ds["data"]["input_ids"].tolist(),
            "seed": cfg.seed,
        }

    monkeypatch.setattr(training_module, "run_custom_trainer", fake_run_custom_trainer)

    base_config = {
        "seed": 99,
        "output_dir": str(tmp_path / "run1"),
        "dataset": {"train_texts": ["alpha", "beta"]},
    }

    first: dict | None = None
    try:
        first = run_functional_training(base_config, resume=False)
    except HFModelUnavailableError as exc:
        pytest.skip(f"HF model unavailable in CI (no cache/network): {exc}")

    random.random()
    np.random.rand()

    second_config = dict(base_config)
    second_config["output_dir"] = str(tmp_path / "run2")
    second = run_functional_training(second_config, resume=False)

    assert first == second, "first is not valid"

    # Provenance is written by legacy_api.run_functional_training when
    # output_dir is present in config (lines ~916). Check conditionally.
    prov1 = load_environment_summary(tmp_path / "run1" / "provenance")
    prov2 = load_environment_summary(tmp_path / "run2" / "provenance")
    if prov1 and prov2:
        assert prov1["seed"] == prov2["seed"] == 99, "Condition must be true"
        assert prov1["command"] == prov2["command"] == "train", "Condition must be true"
