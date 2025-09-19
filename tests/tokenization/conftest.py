import os
import sys
import types
from pathlib import Path

import pytest

_TRANSFORMERS_STUB = os.getenv("CODEX_TEST_TRANSFORMERS_STUB", "").strip() == "1"
_SPM_STUB_FLAG = os.getenv("CODEX_TEST_SPM_STUB", "").strip() == "1"
_TOKENIZERS_STUB_FLAG = os.getenv("CODEX_TEST_TOKENIZERS_STUB", "").strip() == "1"

if _TRANSFORMERS_STUB:
    sys.modules.setdefault("transformers", types.SimpleNamespace(__version__="0.0"))

if _TOKENIZERS_STUB_FLAG:

    class _StubSentencePieceUnigramTokenizer:
        pass

    class _StubTokenizer:
        def __init__(self, *args: object, **kwargs: object) -> None:
            pass

        @classmethod
        def from_file(cls, path: str):  # pragma: no cover - stub
            raise RuntimeError("tokenizers stub active; real package required")

        def get_vocab_size(self) -> int:  # pragma: no cover - stub
            return 0

        def get_special_tokens(self) -> list[str]:  # pragma: no cover - stub
            return []

    class _StubBPE:
        def __init__(self, *args: object, **kwargs: object) -> None:
            pass

    fake_tokenizers = types.SimpleNamespace(
        __version__="0.0",
        SentencePieceUnigramTokenizer=_StubSentencePieceUnigramTokenizer,
        Tokenizer=_StubTokenizer,
        models=types.SimpleNamespace(BPE=_StubBPE),
        normalizers=types.SimpleNamespace(NFKC=lambda: None),
        pre_tokenizers=types.SimpleNamespace(ByteLevel=lambda: None),
        trainers=types.SimpleNamespace(BpeTrainer=lambda **_: None),
    )
    sys.modules.setdefault("tokenizers", fake_tokenizers)

_SPM_STUB: types.SimpleNamespace | None = None
if _SPM_STUB_FLAG:

    def _fake_train(**kwargs):
        model_prefix = Path(kwargs["model_prefix"])
        model_prefix.with_suffix(".model").write_text("model", encoding="utf-8")
        model_prefix.with_suffix(".vocab").write_text("vocab", encoding="utf-8")

    _SPM_STUB = types.SimpleNamespace(
        SentencePieceTrainer=types.SimpleNamespace(Train=_fake_train),
        SentencePieceProcessor=lambda: types.SimpleNamespace(Load=lambda _path: None),
    )
    sys.modules.setdefault("sentencepiece", _SPM_STUB)

pytest.importorskip("transformers")
pytest.importorskip("sentencepiece")


if _SPM_STUB_FLAG and _SPM_STUB is not None:

    @pytest.fixture(autouse=True)
    def _stub_sentencepiece(monkeypatch, tmp_path):
        """Stub SentencePiece training for deterministic unit tests."""
        try:
            from tokenization import train_tokenizer as train_module
        except ModuleNotFoundError:
            yield
            return

        if train_module is None:
            yield
            return

        monkeypatch.setattr(train_module, "spm", _SPM_STUB, raising=False)
        yield
