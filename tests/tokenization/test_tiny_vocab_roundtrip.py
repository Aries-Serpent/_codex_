from pathlib import Path

import pytest


def _vocab_path() -> Path:
    # Resolve relative to repository root to avoid cwd differences.
    here = Path(__file__).resolve()
    repo = here.parents[2]
    return repo / "artifacts" / "models" / "tiny_tokenizer" / "vocab.json"


@pytest.mark.skipif(not _vocab_path().exists(), reason="tiny vocab fixture missing")
def test_tiny_vocab_roundtrip_and_padding():
    from codex_ml.tokenization.offline_vocab import TinyVocabTokenizer

    vocab_path = _vocab_path()
    tok = TinyVocabTokenizer.from_vocab_file(vocab_path)

    text = "hello world"
    ids = tok.encode(text)
    assert ids == [2, 4]  # hello, world per fixture vocab
    dec = tok.decode(ids)
    assert dec == text

    # Pad manually to length 5 using pad id from vocab (0)
    pad_id = tok.vocab.get("<pad>")
    assert pad_id == 0
    padded = ids + [pad_id] * (5 - len(ids))
    assert len(padded) == 5
    # Decoding includes pad tokens verbatim (implementation choice)
    dec_padded = tok.decode(padded)
    assert dec_padded.endswith("<pad> <pad> <pad>")
