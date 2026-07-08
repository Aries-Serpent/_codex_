pytest.importorskip("tensorboard")
"""
Test Cache Roundtrip

Test module for cache roundtrip.
"""

import pytest

np = pytest.importorskip("numpy")
pytest.importorskip("transformers")

from codex_ml.utils.hf_pinning import load_from_pretrained
from src.training.cache import TokenCache
from src.training.datasets import TextDataset


def test_cache_roundtrip(tmp_path):
    from codex_ml.utils.hf_pinning import HFModelUnavailableError
    from transformers import AutoTokenizer

    # Load tokenizer without invalid revision parameter
    try:
        tok = load_from_pretrained(AutoTokenizer, "hf-internal-testing/llama-tokenizer")
    except HFModelUnavailableError:
        pytest.skip("HF model unavailable in CI (no network access)")
    else:
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
        assert len(batches) == 1, "Batches must not be empty"
        reloaded = batches[0]
        for key in batch:
            assert np.array_equal(batch[key], reloaded[key])
