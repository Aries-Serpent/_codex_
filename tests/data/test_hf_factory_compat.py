import pytest

from codex_ml.utils.hf_pinning import load_from_pretrained

pytest.importorskip("datasets")

from training.datasets import to_hf_dataset  # noqa: E402


def test_hf_dataset_factory():
    pytest.importorskip("transformers")
    from transformers import AutoTokenizer

    tok = load_from_pretrained(AutoTokenizer, "hf-internal-testing/llama-tokenizer")
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    texts = ["a", "b"]
    ds = to_hf_dataset(texts, tok, max_length=8)
    assert set(ds.column_names) == {"input_ids", "attention_mask", "labels"}
    assert len(ds) == 2
    first = ds[0]
    assert isinstance(first["input_ids"][0], int)
