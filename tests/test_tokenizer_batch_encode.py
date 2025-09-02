import pytest

from codex_ml.tokenization.hf_tokenizer import HFTokenizerAdapter


@pytest.fixture(scope="session")
def hf_tok():
    return HFTokenizerAdapter.load()


def test_batch_encode_masks_and_lengths(hf_tok):
    adp = hf_tok
    enc = adp.batch_encode(["a", "longer sentence"], max_length=8, return_dict=True)
    assert "input_ids" in enc and "attention_mask" in enc
    assert enc["input_ids"].shape == enc["attention_mask"].shape
    assert enc["input_ids"].shape[0] == 2
    assert enc["input_ids"].shape[1] == 8
    assert int(enc["attention_mask"][0].sum()) <= int(enc["attention_mask"][1].sum())
    enc2 = adp.batch_encode(["1234567890"], max_length=5, return_dict=True)
    assert enc2["input_ids"].shape[1] == 5
