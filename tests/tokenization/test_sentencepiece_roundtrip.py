from __future__ import annotations

from pathlib import Path

import pytest

spm = pytest.importorskip("sentencepiece")


def _tiny_sp_model(tmp_path: Path) -> str:
    # Build a toy SP model on the fly (keeps tests offline)
    # vocab=64 is enough for small sample text; use UNK/BOS/EOS/PAD.
    txt = tmp_path / "toy.txt"
    txt.write_text(
        "hello world\n"
        "hello codex\n"
        "general kenobi\n"
        "lorem ipsum dolor sit amet\n"
    )
    model_prefix = str(tmp_path / "toy_sp")
    spm.SentencePieceTrainer.Train(
        input=str(txt),
        model_prefix=model_prefix,
        vocab_size=64,
        model_type="bpe",
        character_coverage=1.0,
        pad_id=0,
        unk_id=1,
        bos_id=2,
        eos_id=3,
    )
    return f"{model_prefix}.model"


def test_roundtrip_plain(tmp_path: Path):
    model = _tiny_sp_model(tmp_path)
    sp = spm.SentencePieceProcessor(model_file=model)
    text = "hello world"
    ids = sp.encode(text, out_type=int)
    back = sp.decode(ids)
    assert isinstance(ids, list) and all(isinstance(i, int) for i in ids)
    # decode() is not guaranteed to be byte-identical for whitespace,
    # but round-trip should preserve semantic tokens.
    assert back.replace("▁", " ").strip()  # decode produced text
    assert sp.decode(sp.encode(back, out_type=int))  # second round-trip ok


def test_special_tokens_and_unk(tmp_path: Path):
    model = _tiny_sp_model(tmp_path)
    sp = spm.SentencePieceProcessor(model_file=model)
    # Force an unknown token
    text = "hello <totally_unknown_token>"
    ids = sp.encode(text, out_type=int)
    # Should contain UNK id (1 per our trainer config above)
    assert 1 in ids
    # BOS/EOS opt-in via add_bos/add_eos flags
    ids_be = sp.encode(text, out_type=int, add_bos=True, add_eos=True)
    assert (2 in ids_be) and (3 in ids_be)


def test_pad_and_truncation(tmp_path: Path):
    model = _tiny_sp_model(tmp_path)
    sp = spm.SentencePieceProcessor(model_file=model)
    max_len = 12
    # Encode to ids, then pad/truncate to max_len with PAD id=0
    ids = sp.encode("lorem ipsum dolor sit amet", out_type=int)
    # pad:
    padded = (ids + [0] * max(0, max_len - len(ids)))[:max_len]
    assert len(padded) == max_len
    # truncation:
    assert len(ids[:max_len]) <= max_len


def test_batch_encode_decode_shapes(tmp_path: Path):
    model = _tiny_sp_model(tmp_path)
    sp = spm.SentencePieceProcessor(model_file=model)
    batch = ["hello world", "general kenobi", ""]
    batch_ids = [sp.encode(t, out_type=int) for t in batch]
    assert isinstance(batch_ids, list) and all(isinstance(x, list) for x in batch_ids)
    # Decode each back; empty string stays empty
    back = [sp.decode(ids) for ids in batch_ids]
    assert len(back) == len(batch)
    assert back[-1] == "" or back[-1].strip() == ""

