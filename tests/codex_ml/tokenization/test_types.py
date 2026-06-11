from codex_ml.tokenization._types import (
    BOS_TOKEN,
    EOS_TOKEN,
    PAD_TOKEN,
    UNK_TOKEN,
)


def test_types_constants():
    assert BOS_TOKEN == "<s>"
    assert EOS_TOKEN == "</s>"
    assert PAD_TOKEN == "<pad>"
    assert UNK_TOKEN == "<unk>"
