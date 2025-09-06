import pytest

from training.cache import TokenCache
from training.datasets import TextDataset


def test_cache_roundtrip(tmp_path):
    np = pytest.importorskip("numpy")
    pytest.importorskip("transformers")
    from transformers import AutoTokenizer

    tok = AutoTokenizer.from_pretrained("hf-internal-testing/llama-tokenizer")
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    texts = ["hello world", "goodbye"]
    ds = TextDataset(texts, tok, max_length=8)
    batch = {
        key: np.stack([sample[key] for sample in ds])
        for key in ["input_ids", "attention_mask", "labels"]
    }
    cache = TokenCache(tmp_path, rows_per_shard=4)
    cache.add_batch(batch)
    cache.finalize()
    batches = list(TokenCache.iter_batches(tmp_path))
    assert len(batches) == 1
    reloaded = batches[0]
    for key in batch:
        assert np.array_equal(batch[key], reloaded[key])
