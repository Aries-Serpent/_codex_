from codex_ml.tokenization.hf_tokenizer import HFTokenizerAdapter


def test_multilingual_tokenizer_roundtrip():
    tok = HFTokenizerAdapter.load("bert-base-multilingual-cased")
    texts = ["Hello world", "Hola mundo", "你好，世界"]
    ids = [tok.encode(t) for t in texts]
    decoded = [tok.decode(i) for i in ids]
    assert len(ids) == len(decoded)
