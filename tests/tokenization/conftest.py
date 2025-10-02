import importlib.machinery
import importlib.util
import json
import os
import sys
import types
from pathlib import Path
from typing import Iterable

import pytest

_TRANSFORMERS_STUB = os.getenv("CODEX_TEST_TRANSFORMERS_STUB", "").strip() == "1"
_SPM_STUB_FLAG = os.getenv("CODEX_TEST_SPM_STUB", "").strip() == "1"
_TOKENIZERS_STUB_FLAG = os.getenv("CODEX_TEST_TOKENIZERS_STUB", "").strip() == "1"

_transformers_spec = None
if not _TRANSFORMERS_STUB:
    try:
        _transformers_spec = importlib.util.find_spec("transformers")
    except ValueError:
        # Some environments register a namespace stub with __spec__ = None which
        # triggers importlib.util.find_spec to raise ValueError. Treat this the
        # same as the package being absent so the lightweight stub below is
        # installed and tests can proceed without an optional dependency.
        _transformers_spec = None

if _TRANSFORMERS_STUB or _transformers_spec is None:

    class _BaseStubHFTokenizer:
        """Shared stub functionality for HF tokenizers used in tests."""

        def __init__(self, identifier: str, **kwargs: object) -> None:
            self.identifier = identifier
            self.pad_token_id = 0
            self.pad_token = "[PAD]"
            self.eos_token_id = 1
            self.eos_token = "[EOS]"
            self.vocab_size = 256
            self._additional_special_tokens: list[str] = []
            self.is_fast = bool(kwargs.get("use_fast", True))

        def _normalise_tokens(
            self,
            tokens: list[int],
            *,
            padding: object,
            truncation: object,
            max_length: object,
        ) -> list[int]:
            max_len = max_length if isinstance(max_length, int) and max_length >= 0 else None
            if bool(truncation) and max_len is not None:
                tokens = tokens[:max_len]
            if (padding is True or padding == "max_length") and max_len is not None:
                if len(tokens) < max_len:
                    tokens = tokens + [self.pad_token_id] * (max_len - len(tokens))
            return tokens

        def encode(self, text: str, add_special_tokens: bool = True, **kwargs: object) -> list[int]:
            base = [ord(ch) % 256 for ch in text]
            if add_special_tokens:
                base.append(self.eos_token_id)
            return self._normalise_tokens(
                base,
                padding=kwargs.get("padding"),
                truncation=kwargs.get("truncation"),
                max_length=kwargs.get("max_length"),
            )

        def __call__(self, texts: Iterable[str], **kwargs: object) -> dict[str, list[list[int]]]:
            return {
                "input_ids": [
                    self.encode(
                        t,
                        add_special_tokens=kwargs.get("add_special_tokens", True),
                        padding=kwargs.get("padding"),
                        truncation=kwargs.get("truncation"),
                        max_length=kwargs.get("max_length"),
                    )
                    for t in texts
                ]
            }

        def batch_encode_plus(
            self, texts: Iterable[str], **kwargs: object
        ) -> dict[str, list[list[int]]]:
            return self.__call__(texts, **kwargs)

        def decode(
            self, tokens: Iterable[int], skip_special_tokens: bool = True, **_: object
        ) -> str:
            chars: list[str] = []
            specials = {self.pad_token_id, self.eos_token_id}
            for t in tokens:
                value = int(t)
                if skip_special_tokens and value in specials:
                    continue
                chars.append(chr(value % 256))
            return "".join(chars)

        def convert_ids_to_tokens(self, idx: int) -> str:
            return chr(int(idx) % 256)

        def convert_tokens_to_string(self, tokens: Iterable[str]) -> str:
            return "".join(tokens)

        def add_special_tokens(self, mapping: dict[str, object]) -> int:
            specials = mapping.get("additional_special_tokens") if mapping else None
            if isinstance(specials, (list, tuple)):
                self._additional_special_tokens.extend(str(s) for s in specials)
            pad_token = mapping.get("pad_token") if mapping else None
            if pad_token is not None:
                self.pad_token = str(pad_token)
            return len(self._additional_special_tokens)

        def save_pretrained(self, output_dir: str) -> None:
            path = Path(output_dir)
            path.mkdir(parents=True, exist_ok=True)
            (path / "tokenizer.json").write_text("stub", encoding="utf-8")

    class _StubPreTrainedTokenizerBase(_BaseStubHFTokenizer):
        """Baseline class mirroring ``PreTrainedTokenizerBase``."""

    class _StubAutoTokenizer(_StubPreTrainedTokenizerBase):
        """Minimal stand-in for Hugging Face's ``AutoTokenizer``."""

        @classmethod
        def from_pretrained(cls, identifier: str, **kwargs: object) -> "_StubAutoTokenizer":
            return cls(identifier, **kwargs)

    class _StubPreTrainedTokenizerFast(_StubPreTrainedTokenizerBase):
        """Stub matching the constructor used in tests when loading artifacts."""

        def __init__(self, tokenizer_file: str, **kwargs: object) -> None:
            super().__init__(tokenizer_file, **kwargs)
            self.tokenizer_file = tokenizer_file

    fake_transformers = types.ModuleType("transformers")
    fake_transformers.__dict__.update(
        {
            "__version__": "0.0",
            "IS_CODEX_STUB": True,
            "AutoTokenizer": _StubAutoTokenizer,
            "PreTrainedTokenizerBase": _StubPreTrainedTokenizerBase,
            "PreTrainedTokenizerFast": _StubPreTrainedTokenizerFast,
        }
    )
    fake_transformers.__spec__ = importlib.machinery.ModuleSpec("transformers", loader=None)
    sys.modules.setdefault("transformers", fake_transformers)

_spm_spec = None
if not _SPM_STUB_FLAG:
    try:
        _spm_spec = importlib.util.find_spec("sentencepiece")
    except ValueError:
        _spm_spec = None
    if _spm_spec is None:
        _SPM_STUB_FLAG = True

_tokenizers_spec = None
if not _TOKENIZERS_STUB_FLAG:
    try:
        _tokenizers_spec = importlib.util.find_spec("tokenizers")
    except ValueError:
        # Align behaviour with the transformers shim: treat a module with an
        # invalid/None spec as missing so tests fall back to the stub. This
        # happens in stripped-down environments where optional deps are mocked.
        _tokenizers_spec = None

if _TOKENIZERS_STUB_FLAG or _tokenizers_spec is None:

    class _StubSentencePieceUnigramTokenizer:
        """Minimal subset of sentencepiece's tokenizer API for tests."""

        def __init__(self, source: object) -> None:
            self.source = source

        @classmethod
        def from_spm(cls, source: object) -> "_StubSentencePieceUnigramTokenizer":
            return cls(source)

        def save(self, path: str) -> None:  # pragma: no cover - simple file write
            Path(path).write_text("stub", encoding="utf-8")

    class _StubTokenizer:
        def __init__(self, *args: object, **kwargs: object) -> None:
            self.vocab: dict[str, int] = {}

        @classmethod
        def from_file(cls, path: str):
            data = {}
            try:
                data = json.loads(Path(path).read_text(encoding="utf-8"))
            except Exception:
                pass
            inst = cls()
            vocab = data.get("vocab", {}) if isinstance(data, dict) else {}
            inst.vocab = {str(k): int(v) for k, v in vocab.items()}
            return inst

        def get_vocab_size(self) -> int:
            return len(self.vocab)

        def get_vocab(self) -> dict[str, int]:
            return dict(self.vocab)

        def get_special_tokens(self) -> list[str]:
            return [tok for tok, idx in self.vocab.items() if idx < 4]

        def train_from_iterator(self, iterator: Iterable[str], trainer: object = None) -> None:
            tokens: set[str] = set()
            for item in iterator:
                tokens.update(str(item).split())
            base = {"[PAD]": 0, "[UNK]": 1, "[BOS]": 2, "[EOS]": 3}
            sorted_tokens = sorted(tok for tok in tokens if tok)
            self.vocab = dict(base)
            for offset, tok in enumerate(sorted_tokens, start=len(base)):
                self.vocab[tok] = offset

        def encode(self, text: str) -> types.SimpleNamespace:
            ids = [self.vocab.get(tok, 1) for tok in str(text).split()]
            return types.SimpleNamespace(ids=ids)

        def save(self, path: str) -> None:
            Path(path).write_text(json.dumps({"vocab": self.vocab}), encoding="utf-8")

    class _StubBPE:
        def __init__(self, *args: object, **kwargs: object) -> None:
            pass

    fake_tokenizers = types.ModuleType("tokenizers")
    fake_tokenizers.__dict__.update(
        {
            "__version__": "0.0",
            "SentencePieceUnigramTokenizer": _StubSentencePieceUnigramTokenizer,
            "Tokenizer": _StubTokenizer,
            "models": types.SimpleNamespace(BPE=_StubBPE),
            "normalizers": types.SimpleNamespace(NFKC=lambda: None),
            "pre_tokenizers": types.SimpleNamespace(ByteLevel=lambda: None),
            "trainers": types.SimpleNamespace(BpeTrainer=lambda **_: None),
        }
    )
    fake_tokenizers.__spec__ = importlib.machinery.ModuleSpec("tokenizers", loader=None)
    sys.modules.setdefault("tokenizers", fake_tokenizers)

_SPM_STUB: types.SimpleNamespace | None = None
if _SPM_STUB_FLAG:

    def _fake_train(**kwargs):
        model_prefix = Path(kwargs["model_prefix"])
        tokens: list[str] = []
        if "input" in kwargs:
            for path in str(kwargs["input"]).split(","):
                if not path:
                    continue
                try:
                    data = Path(path).read_text(encoding="utf-8")
                except Exception:
                    continue
                tokens.extend(data.split())
        elif "sentence_iterator" in kwargs:
            iterator = kwargs["sentence_iterator"]
            try:
                for sentence in iterator:
                    tokens.extend(str(sentence).split())
            except Exception:
                tokens.extend(str(iterator).split())
        vocab = sorted({tok for tok in tokens if tok})
        model_data = {
            "tokens": vocab,
            "special": {"pad": 0, "unk": 1, "bos": 2, "eos": 3},
        }
        model_prefix.with_suffix(".model").write_text(json.dumps(model_data), encoding="utf-8")
        model_prefix.with_suffix(".vocab").write_text("\n".join(vocab), encoding="utf-8")

    class _StubSentencePieceProcessor:
        def __init__(self, model_file: str | None = None, **kwargs: object) -> None:
            self.model_file = None
            self._tokens: list[str] = []
            self._token_to_id: dict[str, int] = {}
            self._special = {"pad": 0, "unk": 1, "bos": 2, "eos": 3}
            if model_file is not None:
                self.Load(model_file)
            if kwargs:
                model = kwargs.get("model") or kwargs.get("model_file")
                if model and self.model_file is None:
                    self.Load(str(model))

        def Load(self, path: str) -> bool:
            self.model_file = path
            try:
                data = json.loads(Path(path).read_text(encoding="utf-8"))
            except Exception:
                data = {"tokens": []}
            self._tokens = list(data.get("tokens", []))
            self._token_to_id = {
                tok: idx + len(self._special) for idx, tok in enumerate(self._tokens)
            }
            return True

        def encode(
            self,
            text: str,
            out_type: type = int,
            *,
            add_bos: bool = False,
            add_eos: bool = False,
        ) -> list[int]:
            ids: list[int] = []
            for tok in str(text).split():
                ids.append(self._token_to_id.get(tok, self._special["unk"]))
            if add_bos:
                ids.insert(0, self._special["bos"])
            if add_eos:
                ids.append(self._special["eos"])
            return [int(out_type(i)) for i in ids]

        def decode(self, ids: Iterable[int]) -> str:
            pieces: list[str] = []
            for idx in ids:
                value = int(idx)
                if value in self._special.values():
                    continue
                pieces.append(
                    self._tokens[value - len(self._special)]
                    if value - len(self._special) < len(self._tokens)
                    else "<unk>"
                )
            return " ".join(pieces)

        def get_piece_size(self) -> int:
            return len(self._tokens) + len(self._special)

        def piece_size(self) -> int:
            return self.get_piece_size()

        def vocab_size(self) -> int:
            return self.get_piece_size()

    _SPM_STUB = types.ModuleType("sentencepiece")
    _SPM_STUB.SentencePieceTrainer = types.SimpleNamespace(Train=_fake_train, train=_fake_train)
    _SPM_STUB.SentencePieceProcessor = _StubSentencePieceProcessor
    _SPM_STUB.__spec__ = importlib.machinery.ModuleSpec("sentencepiece", loader=None)
    sys.modules.setdefault("sentencepiece", _SPM_STUB)

# If SentencePiece is entirely absent, individual tests handle skips via importorskip.


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
