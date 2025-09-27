from __future__ import annotations

import types
from pathlib import Path

import pytest

from codex_ml.training.functional_training import TrainConfig, train

torch = pytest.importorskip("torch")


class _FakeTokenizer:
    def __init__(self) -> None:
        self.pad_token = "<pad>"
        self.eos_token = "<eos>"
        self.pad_token_id = 0
        self.vocab = {"<pad>": 0, "<eos>": 1, "a": 2, "b": 3, "c": 4, "d": 5, "e": 6}

    def __call__(
        self,
        texts: list[str],
        *,
        padding: str,
        truncation: bool,
        max_length: int,
        return_tensors: str,
    ) -> dict[str, torch.Tensor]:
        del padding, truncation, return_tensors
        encoded = []
        masks = []
        for text in texts:
            tokens = [self.vocab.get(piece, 0) for piece in text.split()[:max_length]]
            attn = [1] * len(tokens)
            while len(tokens) < max_length:
                tokens.append(self.pad_token_id)
                attn.append(0)
            encoded.append(tokens)
            masks.append(attn)
        return {
            "input_ids": torch.tensor(encoded, dtype=torch.long),
            "attention_mask": torch.tensor(masks, dtype=torch.long),
        }


class _TinyLM(torch.nn.Module):
    def __init__(self, vocab_size: int, hidden_size: int = 6) -> None:
        super().__init__()
        self.embed = torch.nn.Embedding(vocab_size, hidden_size)
        self.proj = torch.nn.Linear(hidden_size, vocab_size)
        self.loss_fn = torch.nn.CrossEntropyLoss(ignore_index=0)
        self.config = types.SimpleNamespace(vocab_size=vocab_size)

    def forward(
        self,
        input_ids: torch.Tensor,
        labels: torch.Tensor | None = None,
        attention_mask: torch.Tensor | None = None,
    ) -> types.SimpleNamespace:
        del attention_mask
        hidden = self.embed(input_ids)
        logits = self.proj(hidden)
        loss = None
        if labels is not None:
            loss = self.loss_fn(logits.view(-1, logits.size(-1)), labels.view(-1))
        return types.SimpleNamespace(logits=logits, loss=loss)


@pytest.fixture()
def tokenizer_stub(monkeypatch: pytest.MonkeyPatch) -> _FakeTokenizer:
    tokenizer = _FakeTokenizer()

    def fake_loader(cls, *args, **kwargs):  # type: ignore[no-untyped-def]
        del cls, args, kwargs
        return tokenizer

    monkeypatch.setattr(
        "codex_ml.training.functional_training.load_from_pretrained",
        fake_loader,
    )
    return tokenizer


@pytest.fixture(autouse=True)
def deterministic_shuffle(monkeypatch: pytest.MonkeyPatch) -> None:
    def _no_shuffle(seq):  # type: ignore[no-untyped-def]
        return None

    monkeypatch.setattr("codex_ml.training.functional_training.random.shuffle", _no_shuffle)


class _CountingAdamW(torch.optim.AdamW):
    last_instance: "_CountingAdamW | None" = None

    def __init__(self, *args, **kwargs) -> None:  # type: ignore[no-untyped-def]
        super().__init__(*args, **kwargs)
        self.step_calls = 0
        _CountingAdamW.last_instance = self

    def step(self, *args, **kwargs):  # type: ignore[no-untyped-def]
        self.step_calls += 1
        return super().step(*args, **kwargs)


@pytest.fixture(autouse=True)
def counting_optimizer(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("codex_ml.training.functional_training.torch.optim.AdamW", _CountingAdamW)
    _CountingAdamW.last_instance = None


def test_tail_flush_triggers_optimizer_step(tokenizer_stub: _FakeTokenizer, tmp_path: Path) -> None:
    texts = ["a b", "b c", "c d", "d e", "e a"]
    vocab_size = len(tokenizer_stub.vocab)

    torch.manual_seed(1)
    model = _TinyLM(vocab_size)

    cfg = TrainConfig(
        model_name="stub",
        epochs=1,
        batch_size=2,
        lr=1e-3,
        seed=123,
        gradient_accumulation_steps=4,
        tensorboard=False,
        tensorboard_dir=str(tmp_path / "tb"),
        mlflow_enable=False,
        metrics_out=str(tmp_path / "metrics_tail.ndjson"),
        checkpoint_dir=None,
        max_length=4,
    )

    train(texts, config=cfg, model=model)

    optimizer = _CountingAdamW.last_instance
    assert optimizer is not None, "expected optimizer instance to be created"
    assert optimizer.step_calls == 1
