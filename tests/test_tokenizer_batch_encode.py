import pytest
from transformers import AutoTokenizer

from codex_ml.tokenization.hf_tokenizer import HFTokenizerAdapter


@pytest.fixture(scope="session")
def hf_tok():
    return AutoTokenizer.from_pretrained("hf-internal-testing/tiny-random-gpt2")


def test_batch_encode_masks_and_lengths(hf_tok):
    adp = HFTokenizerAdapter(hf_tok)
    enc = adp.batch_encode(["a", "longer sentence"], max_length=8, return_dict=True)
    assert enc["input_ids"].shape == enc["attention_mask"].shape
    assert enc["input_ids"].shape[0] == 2
    # ensure padding applied
    assert enc["attention_mask"].tolist()[0][-1] in {0, 1}


def test_batch_encode_truncation(hf_tok):
    adp = HFTokenizerAdapter(hf_tok)
    enc = adp.batch_encode(["one two three four five"], max_length=3, return_dict=True)
    assert enc["input_ids"].shape[-1] == 3


def test_batch_encode_respects_string_padding(hf_tok):
    adp = HFTokenizerAdapter(hf_tok)
    texts = ["a", "longer sentence"]
    max_len = max(len(hf_tok.encode(t)) for t in texts)

    enc_longest = adp.batch_encode(texts, padding="longest", return_dict=True)
    assert enc_longest["input_ids"].shape[-1] == max_len

    enc_no_pad = adp.batch_encode(
        texts,
        padding="do_not_pad",
        return_tensors=None,
        return_dict=True,
    )
    lengths = [len(ids) for ids in enc_no_pad["input_ids"]]
    assert lengths == [len(hf_tok.encode(t)) for t in texts]
