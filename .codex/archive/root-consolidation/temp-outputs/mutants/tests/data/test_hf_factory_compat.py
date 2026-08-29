pytest.importorskip("tensorboard")
"""
Test Hf Factory Compat

Test module for hf factory compat.
"""

import pytest

from codex_ml.utils.hf_pinning import HFModelUnavailableError, load_from_pretrained

pytest.importorskip("datasets")
pytest.importorskip("torch")

from src.training.datasets import to_hf_dataset


@pytest.fixture(autouse=True)
def _clear_hf_revision_env(monkeypatch):
    """Clear HF_REVISION env vars so KNOWN_MODEL_REVISIONS is used instead of abcdef0."""
    for var in ("HF_REVISION", "CODEX_HF_REVISION", "HF_MODEL_REVISION"):
        monkeypatch.delenv(var, raising=False)


def test_hf_dataset_factory():
    pytest.importorskip("transformers")
    from transformers import AutoTokenizer

    try:
        tok = load_from_pretrained(AutoTokenizer, "hf-internal-testing/llama-tokenizer")
    except HFModelUnavailableError as exc:
        pytest.skip(f"Model unavailable (cache miss + network unreachable): {exc}")
    else:
        if tok.pad_token is None:
            tok.pad_token = tok.eos_token
        texts = ["a", "b"]
        ds = to_hf_dataset(texts, tok, max_length=8)
        assert set(ds.column_names) == {"input_ids", "attention_mask", "labels"}
        assert len(ds) == 2, "Ds must not be empty"
        first = ds[0]
        assert isinstance(first["input_ids"][0], int)
