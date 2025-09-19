from __future__ import annotations

import pytest

pytest.importorskip("transformers")
pytest.importorskip("sentencepiece")

from codex_ml.interfaces.tokenizer import HFTokenizer


def test_encode_decode_roundtrip():
    tk = HFTokenizer("hf-internal-testing/tiny-random-bert", padding=False, truncation=False)
    text = "hello world"

    # Variant A: direct encode/decode
    encoded = tk.encode(text)
    decoded_direct = tk.decode(encoded)

    # Variant B: batch-based encode path for backward compatibility
    ids = tk.batch_encode([text])[0]
    decoded_batch = tk.decode(ids)

    # Accept exact round-trip with potential whitespace normalization
    assert text == decoded_direct.strip()
    assert text == decoded_batch.strip()

    # Properties and metadata
    assert tk.pad_token_id is None or isinstance(tk.pad_token_id, int)
    assert tk.vocab_size > 0
