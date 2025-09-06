import pytest

from training.datasets import to_hf_dataset


def test_hf_dataset_factory():
    pytest.importorskip("transformers")
    pytest.importorskip("datasets")
    from transformers import AutoTokenizer

    tok = AutoTokenizer.from_pretrained("hf-internal-testing/llama-tokenizer")
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    texts = ["a", "b"]
    ds = to_hf_dataset(texts, tok, max_length=8)
    assert set(ds.column_names) == {"input_ids", "attention_mask", "labels"}
    assert len(ds) == 2
    first = ds[0]
    assert isinstance(first["input_ids"][0], int)
