from __future__ import annotations

from typing import Dict, Iterable, List

from codex_ml.registry.tokenizers import encode_cached


class _RoundTripTokenizer:
    pad_token_id = 0
    eos_token_id = 1
    name_or_path = "roundtrip"

    def __init__(self) -> None:
        self._vocab: Dict[str, int] = {"<pad>": self.pad_token_id, "<eos>": self.eos_token_id}
        self._inv: Dict[int, str] = {self.pad_token_id: "<pad>", self.eos_token_id: "<eos>"}
        self.calls: Dict[str, int] = {}

    def _lookup(self, token: str) -> int:
        if token not in self._vocab:
            idx = len(self._vocab)
            self._vocab[token] = idx
            self._inv[idx] = token
        return self._vocab[token]

    def __call__(
        self,
        text: str,
        *,
        padding: bool | str | None = False,
        truncation: bool | None = False,
        max_length: int | None = None,
        add_special_tokens: bool | None = True,
        return_attention_mask: bool = True,
    ) -> Dict[str, List[int]]:
        self.calls[text] = self.calls.get(text, 0) + 1
        parts = text.split()
        tokens = [self._lookup(p) for p in parts]
        if add_special_tokens:
            tokens.append(self.eos_token_id)
        if truncation and max_length is not None:
            tokens = tokens[:max_length]
        mask = [1] * len(tokens)
        if padding and max_length is not None:
            while len(tokens) < max_length:
                tokens.append(self.pad_token_id)
                mask.append(0)
        payload: Dict[str, List[int]] = {"input_ids": tokens}
        if return_attention_mask:
            payload["attention_mask"] = mask
        return payload

    def decode(self, token_ids: Iterable[int], skip_special_tokens: bool = True) -> str:
        pieces: List[str] = []
        for tid in token_ids:
            if skip_special_tokens and tid in {self.pad_token_id, self.eos_token_id}:
                continue
            pieces.append(self._inv.get(tid, ""))
        return " ".join(pieces).strip()


def test_encode_decode_roundtrip_padding() -> None:
    tokenizer = _RoundTripTokenizer()
    text = "cache me twice"
    encoding = encode_cached(
        tokenizer,
        text,
        padding=True,
        truncation=False,
        max_length=8,
    )

    assert "input_ids" in encoding
    assert "attention_mask" in encoding
    assert len(encoding["input_ids"]) == 8
    assert len(encoding["attention_mask"]) == 8

    decoded = tokenizer.decode(encoding["input_ids"])
    assert decoded == text

    cached = encode_cached(
        tokenizer,
        text,
        padding=True,
        truncation=False,
        max_length=8,
    )
    assert tokenizer.calls[text] == 1  # ensure cache hit
    assert cached == encoding
