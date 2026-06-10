import pytest
from codex_ml.tokenization._protocols import TokenizerAdapter

def test_protocol_exists():
    assert TokenizerAdapter is not None
