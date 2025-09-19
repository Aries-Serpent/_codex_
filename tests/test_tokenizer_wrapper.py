from __future__ import annotations

import pytest

pytest.importorskip("transformers")
pytest.importorskip("sentencepiece")

from codex_ml.interfaces.tokenizer import HFTokenizer


def test_padding_truncation_shapes():
    tk = HFTokenizer(
        "hf-internal-testing/tiny-random-bert",
        max_length=8,
        padding="max_length",
        truncation=True,
    )

    # Backward-compatible check: return_dict=True provides HF-style mapping
    out_dict = tk.batch_encode(["hello", "this is a longer sentence"], return_dict=True)
    ids_dict = out_dict["input_ids"]
    assert all(len(seq) == 8 for seq in ids_dict)
    assert "attention_mask" in out_dict and all(len(m) == 8 for m in out_dict["attention_mask"])

    # New-style adapter default: list-of-lists
    out_list = tk.batch_encode(["hello", "this is a longer sentence"])
    assert all(len(ids) == 8 for ids in out_list)
