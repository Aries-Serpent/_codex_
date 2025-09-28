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
        self.vocab = {
            "<pad>": 0,
            "<eos>": 1,
            "0": 2,
            "1": 3,
            "2": 4,
            "3": 5,
            "4": 6,
            "5": 7,
        }

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
    def __init__(self, vocab_size: int, hidden_size: int = 8) -> None:
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


def _run_training(
    *,
    texts: list[str],
    model: torch.nn.Module,
    tmp_path: Path,
    batch_size: int,
    grad_accum: int,
) -> None:
    cfg = TrainConfig(
        model_name="stub",
        epochs=1,
        batch_size=batch_size,
        lr=5e-3,
        seed=42,
        gradient_accumulation_steps=grad_accum,
        tensorboard=False,
        tensorboard_dir=str(tmp_path / "tb"),
        mlflow_enable=False,
        metrics_out=str(tmp_path / f"metrics_b{batch_size}_g{grad_accum}.ndjson"),
        checkpoint_dir=None,
        max_length=4,
    )
    train(texts, config=cfg, model=model)


def test_gradient_accumulation_matches_large_batch(
    tokenizer_stub: _FakeTokenizer, tmp_path: Path
) -> None:
    texts = ["0 1 2", "1 2 3", "2 3 4", "3 4 5"]
    vocab_size = len(tokenizer_stub.vocab)

    torch.manual_seed(0)
    base_model = _TinyLM(vocab_size)
    torch.manual_seed(0)
    accum_model = _TinyLM(vocab_size)

    _run_training(
        texts=texts,
        model=base_model,
        tmp_path=tmp_path,
        batch_size=4,
        grad_accum=1,
    )

    _run_training(
        texts=texts,
        model=accum_model,
        tmp_path=tmp_path,
        batch_size=2,
        grad_accum=2,
    )

    for p_large, p_accum in zip(base_model.parameters(), accum_model.parameters()):
        torch.testing.assert_close(p_large, p_accum, atol=1e-5, rtol=1e-4)
