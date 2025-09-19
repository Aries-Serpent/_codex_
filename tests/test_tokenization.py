import pytest

pytest.importorskip("transformers")
pytest.importorskip("sentencepiece")

from codex_ml.tokenization import (
    BOS_TOKEN,
    EOS_TOKEN,
    PAD_TOKEN,
    UNK_TOKEN,
    load_tokenizer,
)


@pytest.fixture(scope="module")
def tok():
    return load_tokenizer("gpt2")


def test_round_trip(tok):
    text = "hello world"
    ids = tok.encode(text)
    assert tok.decode(ids).strip() == text


def test_special_token_ids(tok):
    ids = [tok.encode(t)[0] for t in [BOS_TOKEN, EOS_TOKEN, PAD_TOKEN, UNK_TOKEN]]
    assert len(ids) == 4
    assert len(set(ids)) == 4


def test_deterministic(tok, tmp_path):
    text = "determinism matters"
    ids1 = tok.encode(text)
    tok.save(tmp_path / "tok.json")
    tok2 = load_tokenizer(path=str(tmp_path / "tok.json"))
    ids2 = tok2.encode(text)
    assert ids1 == ids2
