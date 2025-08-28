from codex_ml.tokenization.hf_tokenizer import HFTokenizerAdapter


def test_tokenizer_pad_eos_ids():
    tok = HFTokenizerAdapter.load()
    assert isinstance(tok.pad_id, int)
    assert isinstance(tok.eos_id, int)
