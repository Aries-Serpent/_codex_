from codex_ml.tokenization.offline_vocab import TinyVocabTokenizer


def test_encode_decode_roundtrip():
    tok = TinyVocabTokenizer({"<unk>": 0, "hello": 1, "world": 2})
    text = "hello world hello"
    ids = tok.encode(text)
    assert ids == [1, 2, 1]
    assert tok.decode(ids) == text


def test_batch_encode_uses_unknown_token():
    tok = TinyVocabTokenizer({"<unk>": 0, "token": 1})
    encoded = tok.batch_encode(["token token", "missing token"])
    assert encoded[0] == [1, 1]
    assert encoded[1] == [0, 1]
