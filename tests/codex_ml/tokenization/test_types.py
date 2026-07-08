from codex_ml.tokenization._types import (
    BOS_TOKEN,
    EOS_TOKEN,
    PAD_TOKEN,
    UNK_TOKEN,
)


def test_types_constants():
    assert BOS_TOKEN == "<s>", "BOS_TOKEN is not valid"
    assert EOS_TOKEN == "</s>", "EOS_TOKEN is not valid"
    assert PAD_TOKEN == "<pad>", "PAD_TOKEN is not valid"
    assert UNK_TOKEN == "<unk>", "UNK_TOKEN is not valid"
