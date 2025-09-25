import contextlib
import importlib
import sys
import types
from pathlib import Path
from types import SimpleNamespace
from typing import Dict, Iterator, List, Tuple

import numpy as np
import pytest


def _ensure_real_torch() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    removed: List[Tuple[int, str]] = []
    for idx in range(len(sys.path) - 1, -1, -1):
        entry = sys.path[idx]
        try:
            resolved = Path(entry or ".").resolve()
        except Exception:
            continue
        if resolved == repo_root:
            removed.append((idx, entry))
            del sys.path[idx]
    try:
        sys.modules.pop("torch", None)
        importlib.import_module("torch")
    finally:
        for idx, entry in sorted(removed):
            sys.path.insert(idx, entry)


_ensure_real_torch()
torch = pytest.importorskip("torch")


class _TinyTokenizer:
    """Tokenizer stub that emits deterministic integer tensors."""

    def __init__(self, seq_len: int = 4) -> None:
        self.seq_len = seq_len
        self.pad_token = None
        self.eos_token = 0
        self.pad_token_id = 0

    def __call__(
        self,
        texts: List[str],
        *,
        padding: str = "max_length",
        truncation: bool = True,
        max_length: int = 4,
        return_tensors: str = "pt",
    ) -> Dict[str, torch.Tensor]:
        batch = list(texts)
        size = len(batch)
        length = max_length or self.seq_len
        vocab = max(1, self.seq_len)
        base = torch.arange(size * length, dtype=torch.long).reshape(size, length)
        ids = base % vocab
        mask = torch.ones_like(ids)
        return {"input_ids": ids, "attention_mask": mask}


class _TinyModel(torch.nn.Module):
    """Very small Torch model that exposes the interface the trainer expects."""

    def __init__(self, seq_len: int = 4) -> None:
        super().__init__()
        self.linear = torch.nn.Linear(seq_len, seq_len)
        self.config = SimpleNamespace(vocab_size=seq_len)

    def forward(self, input_ids, labels=None, **_ignored):  # type: ignore[override]
        inputs = input_ids.float()
        targets = inputs if labels is None else labels.float()
        logits_flat = self.linear(inputs)
        logits = logits_flat.unsqueeze(-1).expand(-1, -1, self.config.vocab_size)
        loss = (logits_flat - targets).pow(2).mean()
        return SimpleNamespace(loss=loss, logits=logits)


def _dummy_batch(seq_len: int = 4) -> Dict[str, torch.Tensor]:
    ids = torch.arange(seq_len, dtype=torch.long) % seq_len
    mask = torch.ones(seq_len, dtype=torch.long)
    return {
        "input_ids": ids.clone(),
        "labels": ids.clone(),
        "attention_mask": mask,
    }


def test_train_uses_autocast_and_clip(monkeypatch):
    import codex_ml.training.functional_training as ft

    counters = {"autocast": 0, "clip": 0, "mlflow": 0}

    @contextlib.contextmanager
    def fake_autocast(*_args, **_kwargs) -> Iterator[None]:
        counters["autocast"] += 1
        yield

    def fake_clip(params, max_norm: float) -> None:
        assert pytest.approx(max_norm) == 0.5
        list(params)
        counters["clip"] += 1

    @contextlib.contextmanager
    def fake_mlflow_run(*_args, **_kwargs) -> Iterator[None]:
        counters["mlflow"] += 1
        yield

    class _FakeScaler:
        def scale(self, value):  # type: ignore[no-untyped-def]
            return value

        def unscale_(self, _optimizer):  # type: ignore[no-untyped-def]
            return None

        def step(self, optimizer):  # type: ignore[no-untyped-def]
            optimizer.step()

        def update(self) -> None:  # type: ignore[override]
            return None

    class _AutoTokenizer:  # sentinel types for load_from_pretrained routing
        pass

    class _AutoModel:  # sentinel types for load_from_pretrained routing
        pass

    tokenizer = _TinyTokenizer(seq_len=4)
    model = _TinyModel(seq_len=4)

    def fake_load_from_pretrained(cls, *args, **_kwargs):
        if cls is _AutoTokenizer:
            return tokenizer
        if cls is _AutoModel:
            return model
        raise AssertionError(f"Unexpected load target: {cls}")

    loader_ft = fake_load_from_pretrained

    monkeypatch.setattr(ft, "maybe_autocast", fake_autocast, raising=True)
    monkeypatch.setattr(ft, "clip_gradients", fake_clip, raising=True)
    monkeypatch.setattr(ft, "mlflow_run", fake_mlflow_run, raising=True)

    def _scaler_factory(_enabled: bool) -> _FakeScaler:
        return _FakeScaler()

    monkeypatch.setattr(ft, "get_amp_scaler", _scaler_factory, raising=True)
    monkeypatch.setattr(ft, "apply_lora_if_available", lambda m, **_: m, raising=False)
    monkeypatch.setattr(ft, "export_environment", lambda *a, **k: None, raising=False)
    monkeypatch.setattr(ft, "save_checkpoint", lambda *a, **k: None, raising=False)
    monkeypatch.setattr(ft, "set_reproducible", lambda *a, **k: None, raising=False)
    monkeypatch.setattr(ft, "_HAS_TRANSFORMERS", True, raising=False)
    monkeypatch.setattr(ft, "AutoTokenizer", _AutoTokenizer, raising=False)
    monkeypatch.setattr(ft, "AutoModelForCausalLM", _AutoModel, raising=False)
    monkeypatch.setattr(ft, "load_from_pretrained", loader_ft, raising=True)
    monkeypatch.setattr(ft, "get_hf_revision", lambda: "main", raising=False)

    metrics = ft.train(
        ["hello", "world", "foo", "bar"],
        config=ft.TrainConfig(
            epochs=1,
            batch_size=2,
            gradient_accumulation_steps=1,
            lr=0.1,
            tensorboard=False,
            mlflow_enable=True,
            amp_enable=True,
            amp_dtype="float16",
            grad_clip_norm=0.5,
            max_length=4,
        ),
    )

    assert counters["autocast"] >= 1
    assert counters["clip"] >= 1
    assert counters["mlflow"] == 1
    assert isinstance(metrics, dict)


def test_evaluate_model_uses_autocast(monkeypatch):
    import codex_ml.training.__init__ as tr

    counters = {"autocast": 0}

    @contextlib.contextmanager
    def fake_autocast(*_args, **_kwargs) -> Iterator[None]:
        counters["autocast"] += 1
        yield

    monkeypatch.setattr(tr, "maybe_autocast", fake_autocast, raising=True)

    eval_model = _TinyModel()
    eval_model.train(False)

    dataset = [_dummy_batch() for _ in range(2)]
    cfg = SimpleNamespace(amp_enable=True, amp_dtype="float16")

    result = tr._evaluate_model(eval_model, dataset, batch_size=1, cfg=cfg)  # type: ignore[attr-defined]

    assert counters["autocast"] >= 1
    assert "val_loss" in result


def test_run_functional_training_uses_mlflow(monkeypatch, tmp_path):
    import codex_ml.training.__init__ as tr

    entered: List[str] = []

    @contextlib.contextmanager
    def fake_mlflow_run(*_args, **_kwargs):
        entered.append("entered")
        yield

    monkeypatch.setattr(tr, "mlflow_run", fake_mlflow_run, raising=True)
    monkeypatch.setattr(tr, "set_reproducible", lambda *a, **k: None, raising=False)
    monkeypatch.setattr(tr, "export_environment", lambda *a, **k: None, raising=False)

    def _sanitize(text, cfg):
        return {"text": text}

    def _identity(model, **_):
        return model

    monkeypatch.setattr(tr, "sanitize_prompt", _sanitize, raising=False)
    monkeypatch.setattr(tr, "apply_lora_if_available", _identity, raising=False)
    monkeypatch.setattr(tr, "load_jsonl", lambda *a, **k: ([], []), raising=False)

    fake_datasets = types.ModuleType("datasets")

    class _Dataset:
        def __init__(self, payload):
            self.payload = payload

        @classmethod
        def from_dict(cls, payload):
            return cls(payload)

        def __len__(self):
            first = next(iter(self.payload.values()))
            return len(first)

        def with_format(self, *_args, **_kwargs):  # pragma: no cover - not used in test
            return self

    fake_datasets.Dataset = _Dataset
    monkeypatch.setitem(sys.modules, "datasets", fake_datasets)

    fake_transformers = types.ModuleType("transformers")

    class _AutoTokenizer:
        pass

    fake_transformers.AutoTokenizer = _AutoTokenizer
    fake_transformers.AutoModelForCausalLM = type("_AutoModelForCausalLM", (), {})
    fake_transformers.AutoModelForMaskedLM = type("_AutoModelForMaskedLM", (), {})
    fake_transformers.PreTrainedModel = type("_PreTrainedModel", (), {})
    monkeypatch.setitem(sys.modules, "transformers", fake_transformers)

    class _ArrayWrapper(np.ndarray):
        def clone(self):  # type: ignore[override]
            return self.copy().view(_ArrayWrapper)

    class _StubTokenizer:
        pad_token = None
        eos_token = 0
        pad_token_id = 0

        def __call__(
            self,
            texts: List[str],
            *,
            padding: str = "max_length",
            truncation: bool = True,
            max_length: int = 4,
            return_tensors: str = "pt",
        ) -> Dict[str, np.ndarray]:
            length = max_length or 4
            data = []
            for idx, _ in enumerate(list(texts)):
                row = (np.arange(length) + idx) % length
                data.append(row)
            arr = np.array(data, dtype=np.int64).view(_ArrayWrapper)
            mask = np.ones_like(arr).view(_ArrayWrapper)
            return {"input_ids": arr, "attention_mask": mask}

    tokenizer = _StubTokenizer()
    stub_model = _TinyModel()

    def fake_load_from_pretrained(cls, *args, **_kwargs):
        if cls is _AutoTokenizer:
            return tokenizer
        return stub_model

    loader = fake_load_from_pretrained
    monkeypatch.setattr(tr, "load_from_pretrained", loader, raising=True)
    monkeypatch.setattr(tr, "get_hf_revision", lambda: "main", raising=True)

    fake_training = types.ModuleType("training.functional_training")

    class _TrainCfg:
        __annotations__ = {
            "epochs": int,
            "batch_size": int,
            "grad_accum": int,
            "lr": float,
            "weight_decay": float,
            "warmup_steps": int,
            "max_steps": object,
            "max_grad_norm": object,
            "dtype": str,
            "log_every": int,
            "save_every": int,
            "patience": int,
            "seed": int,
            "resume_from": object,
            "checkpoint_dir": str,
            "use_lora": bool,
            "lora_r": int,
            "lora_alpha": int,
            "lora_dropout": float,
            "device": object,
            "limit_train_batches": object,
            "limit_val_batches": object,
            "dp_enabled": bool,
            "dp_noise_multiplier": float,
            "dp_max_grad_norm": float,
            "dp_target_delta": float,
        }
        __dataclass_fields__ = {name: object() for name in __annotations__}

        epochs = 1
        batch_size = 8
        grad_accum = 1
        lr = 1e-3
        weight_decay = 0.0
        warmup_steps = 0
        max_steps = None
        max_grad_norm = 1.0
        dtype = "fp32"
        log_every = 50
        save_every = 500
        patience = 100
        seed = 42
        resume_from = None
        checkpoint_dir = "checkpoints"
        use_lora = False
        lora_r = 4
        lora_alpha = 16
        lora_dropout = 0.0
        device = None
        limit_train_batches = None
        limit_val_batches = None
        dp_enabled = False
        dp_noise_multiplier = 1.0
        dp_max_grad_norm = 1.0
        dp_target_delta = 1e-5

        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)

    run_calls: List[SimpleNamespace] = []

    def fake_run_custom_trainer(model, tokenizer, train_ds, val_ds, cfg):
        run_calls.append(SimpleNamespace(model=model, tokenizer=tokenizer, cfg=cfg))
        return {"ok": 1.0}

    fake_training.TrainCfg = _TrainCfg
    fake_training.run_custom_trainer = fake_run_custom_trainer
    monkeypatch.setitem(sys.modules, "training.functional_training", fake_training)

    cfg = tr.TrainingRunConfig(
        seed=0,
        dataset={
            "train_texts": ["hello", "world"],
            "eval_texts": [],
            "train_path": None,
            "eval_path": None,
            "format": "text",
        },
        mlflow_enable=True,
        amp_enable=False,
        grad_clip_norm=None,
        output_dir=str(tmp_path / "out"),
        checkpoint_dir=str(tmp_path / "out" / "checkpoints"),
    )
    cfg.safety = tr.SafetySettings(enabled=False)

    result = tr.run_functional_training(cfg)

    assert entered, "mlflow_run context was not entered"
    assert run_calls, "custom trainer was not invoked"
    assert result == {"ok": 1.0}
