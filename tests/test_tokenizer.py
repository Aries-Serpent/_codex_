"""Tests for tokenizer utilities."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

if "transformers" not in sys.modules:

    class _TokenizerStub:
        pad_token_id = 0
        eos_token_id = 0
        pad_token = "<pad>"
        eos_token = "<eos>"
        vocab_size = 1
        name_or_path = "stub-tokenizer"

        def encode(self, text, **kwargs):
            return [0]

        def decode(self, ids, **kwargs):
            return ""

        def add_special_tokens(self, *args, **kwargs):
            return None

        def save_pretrained(self, *args, **kwargs):
            return None

        def __call__(self, inputs, **kwargs):
            length = len(inputs)
            return {"input_ids": [[0] for _ in range(length)]}

    class _AutoTokenizer:
        @staticmethod
        def from_pretrained(*args, **kwargs):
            return _TokenizerStub()

    transformers_stub = SimpleNamespace(
        AutoTokenizer=_AutoTokenizer,
        PreTrainedTokenizerBase=_TokenizerStub,
        IS_CODEX_STUB=True,
    )
    sys.modules["transformers"] = transformers_stub

from codex_ml.tokenization.adapter import HFTokenizerAdapter, WhitespaceTokenizer


@pytest.mark.tokenizer
def test_encode_decode_round_trip():
    """Round-trip encode/decode using the Hugging Face adapter."""

    transformers = pytest.importorskip("transformers", reason="transformers not installed")
    if getattr(transformers, "IS_CODEX_STUB", False):
        pytest.skip("transformers not installed")
    tok = HFTokenizerAdapter("bert-base-uncased")
    text = "Hello world!"
    ids = tok.encode(text)
    assert isinstance(ids, list) and ids
    decoded = tok.decode(ids)
    assert "hello" in decoded.lower()


@pytest.mark.tokenizer
def test_tokenizer_basic(tmp_path):
    """Train a tiny tokenizer and ensure it can encode text."""

    transformers = pytest.importorskip("transformers", reason="transformers not installed")
    if getattr(transformers, "IS_CODEX_STUB", False):
        pytest.skip("transformers not installed")
    pytest.importorskip("sentencepiece", reason="sentencepiece not installed")
    pytest.importorskip("tokenizers", reason="tokenizers not installed")
    from codex_ml.interfaces.tokenizer import HFTokenizer
    from tokenization.train_tokenizer import TrainTokenizerConfig, train

    corpus = tmp_path / "corpus.txt"
    corpus.write_text("Run pre-commit --all-files now.\n", encoding="utf-8")
    cfg = TrainTokenizerConfig(corpus_glob=str(corpus), vocab_size=20, out_dir=str(tmp_path))
    out = train(cfg)
    tk = HFTokenizer(name_or_path=None, artifacts_dir=str(out))
    toks = tk.encode("Run pre-commit --all-files now.")
    assert isinstance(toks, list)
    assert len(toks) > 0


def test_whitespace_tokenizer_deterministic():
    """Whitespace tokenizer should produce stable ids across invocations."""

    tokenizer = WhitespaceTokenizer()
    text = "deterministic hashing is important"
    tokens_first = tokenizer.encode(text)
    tokens_second = tokenizer.encode(text)
    assert tokens_first == tokens_second

    src_root = Path(__file__).resolve().parent.parent / "src"
    script = (
        "import json, sys, types; "
        f"sys.path.insert(0, {str(src_root)!r}); "
        "\nif 'transformers' not in sys.modules: "
        "\n    class _TokenizerStub: "
        "\n        pad_token_id = 0"
        "\n        eos_token_id = 0"
        "\n        pad_token = '<pad>'"
        "\n        eos_token = '<eos>'"
        "\n        vocab_size = 1"
        "\n        name_or_path = 'stub-tokenizer'"
        "\n        def encode(self, text, **kwargs):"
        "\n            return [0]"
        "\n        def decode(self, ids, **kwargs):"
        "\n            return ''"
        "\n        def add_special_tokens(self, *args, **kwargs):"
        "\n            return None"
        "\n        def save_pretrained(self, *args, **kwargs):"
        "\n            return None"
        "\n        def __call__(self, inputs, **kwargs):"
        "\n            length = len(inputs)"
        "\n            return {'input_ids': [[0] for _ in range(length)]}"
        "\n    class _AutoTokenizer:"
        "\n        @staticmethod"
        "\n        def from_pretrained(*args, **kwargs):"
        "\n            return _TokenizerStub()"
        "\n    stub = types.SimpleNamespace("
        "AutoTokenizer=_AutoTokenizer, PreTrainedTokenizerBase=_TokenizerStub)"
        "\n    stub.IS_CODEX_STUB = True"
        "\n    sys.modules['transformers'] = stub"
        "\nfrom codex_ml.tokenization.adapter import WhitespaceTokenizer; "
        f"text = {text!r}; "
        "tok = WhitespaceTokenizer(); "
        "print(json.dumps(tok.encode(text)))"
    )
    result = subprocess.run(
        [sys.executable, "-c", script], capture_output=True, check=True, text=True
    )
    stdout = result.stdout.strip()
    assert stdout, "subprocess should emit encoded tokens"
    tokens_subprocess = json.loads(stdout)
    assert tokens_first == tokens_subprocess
