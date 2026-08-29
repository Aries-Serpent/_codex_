from codex_ml.tokenization._protocols import TokenizerAdapter


def test_protocol_exists():
    assert TokenizerAdapter is not None, "TokenizerAdapter must be initialized"


def test_tokenizer_protocol_interface():
    # Verify the protocol defines required methods
    assert hasattr(TokenizerAdapter, "encode")
    assert hasattr(TokenizerAdapter, "decode")
    assert hasattr(TokenizerAdapter, "train")
