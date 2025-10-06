import math
from pathlib import Path
from typing import Any, Iterable, Sequence

import pytest

from codex_ml.tokenization.hf_tokenizer import HFTokenizerAdapter


class _TensorList(list):
    def tolist(self) -> list[list[int]]:  # pragma: no cover - parity helper
        return [list(row) for row in self]


class _Batch:
    def __init__(self, input_ids: Sequence[Sequence[int]]) -> None:
        self._data = [_TensorList(row) for row in input_ids]

    def __getitem__(self, key: str) -> _TensorList:
        if key != "input_ids":  # pragma: no cover - defensive guard
            raise KeyError(key)
        return _TensorList([list(row) for row in self._data])


class DummyTokenizer:
    """Minimal tokenizer emulating the ``transformers`` API required by the adapter."""

    def __init__(self) -> None:
        vocab = {
            "<pad>": 0,
            "hello": 1,
            "world": 2,
            "</s>": 3,
            "<unk>": 4,
        }
        self.vocab = dict(vocab)
        self.ids_to_tokens = {idx: tok for tok, idx in vocab.items()}
        self.pad_token_id = vocab["<pad>"]
        self.pad_token = "<pad>"
        self.eos_token_id = vocab["</s>"]
        self.eos_token = "</s>"
        self.name_or_path = "dummy-tokenizer"
        self.vocab_size = len(self.vocab)

    # ``transformers`` encoders accept many keyword arguments – only the ones
    # exercised by :class:`HFTokenizerAdapter` are implemented here.
    def encode(
        self,
        text: str,
        *,
        add_special_tokens: bool = False,
        padding: bool | str = False,
        truncation: bool = False,
        max_length: int | None = None,
    ) -> list[int]:
        tokens = [self.vocab.get(part, self.vocab["<unk>"]) for part in text.split()]
        if add_special_tokens:
            tokens = [self.eos_token_id] + tokens + [self.eos_token_id]
        if truncation and max_length is not None:
            tokens = tokens[: max_length]
        if padding == "max_length" and max_length is not None:
            padding_needed = max(0, max_length - len(tokens))
            tokens = tokens + [self.pad_token_id] * padding_needed
        return tokens

    def decode(self, ids: Iterable[int], *, clean_up_tokenization_spaces: bool = False) -> str:
        parts = [self.ids_to_tokens.get(idx, "<unk>") for idx in ids if idx != self.pad_token_id]
        return " ".join(parts)

    def add_special_tokens(self, mapping: dict[str, Any]) -> dict[str, int]:
        added: dict[str, int] = {}
        if "pad_token" in mapping:
            token = mapping["pad_token"]
            self.vocab[token] = self.pad_token_id
            self.ids_to_tokens[self.pad_token_id] = token
            self.pad_token = token
        for token in mapping.get("additional_special_tokens", []) or []:
            if token not in self.vocab:
                new_id = len(self.vocab)
                self.vocab[token] = new_id
                self.ids_to_tokens[new_id] = token
            added[token] = self.vocab[token]
        return added

    def convert_tokens_to_ids(self, token: str) -> int:
        return int(self.vocab[token])

    def save_pretrained(self, path: str | Path) -> None:  # pragma: no cover - helper only
        Path(path).mkdir(parents=True, exist_ok=True)

    def __call__(
        self,
        texts: Sequence[str],
        *,
        padding: bool | str = True,
        truncation: bool = True,
        max_length: int | None = None,
        return_tensors: str | None = "pt",
    ) -> _Batch:
        pad_opt = "max_length" if padding in {True, "max_length"} else False
        encoded = [
            self.encode(text, padding=pad_opt, truncation=truncation, max_length=max_length)
            for text in texts
        ]
        return _Batch(encoded)


@pytest.fixture()
def adapter() -> HFTokenizerAdapter:
    return HFTokenizerAdapter(tokenizer=DummyTokenizer())


def test_roundtrip_padding_and_truncation(adapter: HFTokenizerAdapter) -> None:
    encoded = adapter.encode("hello world", pad_to_max=True, max_length=4)
    # Expect padding to fill the sequence and no information loss on decode.
    assert encoded == [1, 2, 0, 0]
    decoded = adapter.decode(encoded)
    assert decoded == "hello world"

    truncated = adapter.encode("hello world world", pad_to_max=False, max_length=2)
    assert truncated == [1, 2]
    assert adapter.decode(truncated) == "hello world"


def test_special_token_registration(adapter: HFTokenizerAdapter) -> None:
    mapping = adapter.add_special_tokens(["<extra>"])
    assert mapping == {"<extra>": 5}
    assert adapter.tokenizer.vocab["<extra>"] == 5
    assert adapter.tokenizer.ids_to_tokens[5] == "<extra>"


def test_batch_encode_adapter_returns_dense_rows(adapter: HFTokenizerAdapter) -> None:
    batch = adapter.batch_encode(["hello world", "hello"], max_length=3, padding=True)
    assert batch == [[1, 2, 0], [1, 0, 0]]
    # Ensure the synthetic Batch object supports dictionary-style access.
    batch_dict = adapter.batch_encode(
        ["hello world"], max_length=3, padding=True, return_dict=True, return_tensors="pt"
    )
    assert batch_dict["input_ids"] == [[1, 2, 0]]
