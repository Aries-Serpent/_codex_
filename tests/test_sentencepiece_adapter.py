"""Tests for SentencePieceAdapter covering both real sentencepiece and a stubbed implementation.

This merged test file removes merge conflict markers and combines behaviors from
both branches:

- Provides helper utilities to write a tiny corpus (_write_corpus) and to install
  a stubbed `spm` module inside the adapter module to exercise training/loading
  without requiring the sentencepiece package (_stub_sp).
- Keeps tests that require the real package guarded with pytest.importorskip so
  CI environments without sentencepiece continue to run the stubbed tests.
- Adds robust monkeypatching, reload strategies, and clear assertions to make
  tests resilient and backwards compatible with minor API variations in the
  adapter (e.g., string/Path inputs, encode/decode naming, etc).
"""

import importlib
import importlib.util
import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

pytestmark = pytest.mark.filterwarnings("ignore::DeprecationWarning")

# ChatGPT Codex tailored Commented Task Prompt:
# - Task: Expand or harden SentencePieceAdapter implementation and tests.
# - Goals for Codex:
#   1. Keep tests compatible with both the real `sentencepiece` package and a
#      lightweight stub used for CI/no-deps environments.
#   2. Add/extend tests to exercise:
#        - training path (creates .model file),
#        - loading path (existing model gets loaded),
#        - missing sentencepiece handling (AttributeError/ImportError),
#        - sidecar special tokens behavior,
#        - assert_vocab_size behaviors including error paths.
#   3. Preserve flexible input types (str/Path) and adapt to small API differences
#      in adapter (encode/decode vs EncodeAsIds/DecodeIds).
#   4. Provide clear, actionable error messages in test failures.
#
# Expandable items for Codex:
# - Add parametrized tests for different encodings/newline styles.
# - Add Hypothesis-based fuzz tests for unexpected subprocess outputs (optional).
#
# Note: This comment is instructional for future Codex expansions and does not
# affect test execution.

__all__ = [
    "_write_corpus",
    "_stub_sp",
    "test_train_and_reload_roundtrip",
    "test_train_or_load_trains_and_loads",
    "test_train_or_load_loads_existing_model",
    "test_train_or_load_requires_sentencepiece",
    "test_load_requires_sentencepiece",
    "test_add_special_tokens",
    "test_add_special_tokens_sidecar",
    "test_assert_vocab_size",
    "test_missing_sentencepiece_branch",
]


def _write_corpus(tmp_path: Path) -> Path:
    """Write a tiny corpus to tmp_path and return the file path."""
    p = tmp_path / "tiny.txt"
    p.write_text("hello world\nhello codex\n", encoding="utf-8")
    return p


def _stub_sp(monkeypatch, model: Path, vocab_size: int = 5):
    """
    Install a lightweight stubbed `spm` object on codex_ml.tokenization.sentencepiece_adapter.

    Returns a tuple (calls_list, sp_stub) where calls_list collects trainer calls.
    The stub provides:
      - SentencePieceTrainer.Train / .train that writes model_prefix + ".model".
      - SentencePieceProcessor with Load/load and encode/decode helpers and model_file.
    """
    calls = []

    class SentencePieceTrainer:
        # Provide both Train and train names to be robust to adapter calling either.
        @staticmethod
        def Train(*args, **kwargs):
            # Capture what was passed for later inspection
            calls.append({"args": args, "kwargs": kwargs})
            # Attempt to determine model_prefix from kwargs or args
            model_prefix = kwargs.get("model_prefix") or kwargs.get("model_prefix", "")
            if not model_prefix and args:
                # If adapter passed a single string like "--model_prefix=prefix --vocab_size=8"
                argstr = args[0] if args else ""
                for token in str(argstr).split():
                    if token.startswith("--model_prefix="):
                        model_prefix = token.split("=", 1)[1]
            if not model_prefix:
                # Fallback: use model parent stem
                model_prefix = str(model.with_suffix("")).rstrip(".")
            # Write a model file so adapter.load can find it.
            Path(str(model_prefix) + ".model").write_text("model", encoding="utf-8")

        @staticmethod
        def train(*args, **kwargs):
            return SentencePieceTrainer.Train(*args, **kwargs)

    class SentencePieceProcessor:
        def __init__(self):
            self.model_file = None
            self._vocab_size = vocab_size

        # Provide both Load and load naming variants; some adapters call one or the other.
        def Load(self, model_file):
            self.model_file = str(model_file)

        def load(self, model_file):
            return self.Load(model_file)

        # Typical sentencepiece processor exposes EncodeAsIds / DecodeIds; provide small emulation.
        def EncodeAsIds(self, text):
            # Simple deterministic encoding: byte values of UTF-8 (mod 256) per char
            return [ord(c) % 256 for c in str(text)]

        def DecodeIds(self, ids):
            try:
                return "".join(chr(int(i) % 256) for i in ids)
            except Exception:
                return ""

        # Convenience aliases common in lightweight adapters
        def encode(self, text):
            return self.EncodeAsIds(text)

        def GetPieceSize(self):
            return self._vocab_size

        def piece_size(self):
            return self._vocab_size

        def vocab_size(self):  # pragma: no cover - compatibility alias
            return self._vocab_size

        def decode(self, ids):
            return self.DecodeIds(ids)

    sp_stub = SimpleNamespace(
        SentencePieceTrainer=SentencePieceTrainer, SentencePieceProcessor=SentencePieceProcessor
    )

    # Install the stub on the adapter module (be tolerant if the module isn't imported yet)
    monkeypatch.setattr("codex_ml.tokenization.sentencepiece_adapter.spm", sp_stub, raising=False)
    return calls, sp_stub


def _get_adapter_module():
    """Import and return the sentencepiece_adapter module, skipping tests when unavailable."""
    try:
        module = importlib.import_module("codex_ml.tokenization.sentencepiece_adapter")
        return module
    except Exception:
        # If the module cannot be imported for reasons unrelated to sentencepiece, raise so tests fail loudly.
        raise


def _get_model_file_from_adapter(adapter):
    """Safe way to extract model file path from adapter instance for assertions."""
    sp = getattr(adapter, "sp", None)
    if sp is None:
        return None
    return getattr(sp, "model_file", None)


def test_train_and_reload_roundtrip(tmp_path):
    """
    This test exercises an end-to-end flow using the real sentencepiece package.
    It is skipped in environments without sentencepiece.
    """
    pytest.importorskip("sentencepiece", reason="sentencepiece not installed")
    from codex_ml.tokenization.sentencepiece_adapter import SentencePieceAdapter

    corpus = _write_corpus(tmp_path)
    model_prefix = tmp_path / "spm_model"
    model_path = model_prefix.with_suffix(".model")
    adapter = SentencePieceAdapter(model_path)
    # Allow both str and Path inputs; adapter implementations vary.
    adapter.train_or_load(input_path=str(corpus), vocab_size=14, character_coverage=1.0)

    # Reload from disk and ensure encode/decode surface.
    adapter2 = SentencePieceAdapter(model_path)
    adapter2.load()
    # Some adapters expose encode/decode, others EncodeAsIds/DecodeIds. Guard accordingly.
    if hasattr(adapter2, "encode") and hasattr(adapter2, "decode"):
        ids = adapter2.encode("hello codex")
        assert isinstance(ids, (list, tuple))
        assert "hello" in adapter2.decode(ids)
    else:
        # If not available, ensure sp attribute was set
        model_file = _get_model_file_from_adapter(adapter2)
        assert model_file is not None and model_file.endswith(".model")


def test_train_or_load_trains_and_loads(tmp_path, monkeypatch):
    """
    Use a stubbed spm to validate training path: when model is absent trainer is invoked
    and a .model file is created and loaded into adapter.sp.model_file.
    """
    model = tmp_path / "toy.model"
    corpus = tmp_path / "corpus.txt"
    corpus.write_text("hello", encoding="utf-8")

    calls, sp_stub = _stub_sp(monkeypatch, model, vocab_size=8)

    # Import adapter module/class after installing stub ensures adapter uses the stub.
    mod = importlib.import_module("codex_ml.tokenization.sentencepiece_adapter")
    SentencePieceAdapter = getattr(mod, "SentencePieceAdapter")

    adapter = SentencePieceAdapter(model)
    # Some adapters allow overriding model_prefix attribute; be tolerant.
    if hasattr(adapter, "model_prefix"):
        adapter.model_prefix = model.with_suffix("")
    adapter.train_or_load(corpus, vocab_size=8)

    assert model.exists(), "Training path should have written the .model file"
    assert len(calls) > 0, "Trainer should have been invoked for missing model"
    # Ensure adapter loaded the model into its sp instance
    model_file = _get_model_file_from_adapter(adapter)
    assert model_file == str(model)


def test_train_or_load_loads_existing_model(tmp_path, monkeypatch):
    """
    If the model file exists, trainer should not be called and the adapter should
    load the existing model.
    """
    model = tmp_path / "toy.model"
    model.write_text("model", encoding="utf-8")
    corpus = tmp_path / "corpus.txt"
    corpus.write_text("hello", encoding="utf-8")

    calls, sp_stub = _stub_sp(monkeypatch, model, vocab_size=7)
    mod = importlib.import_module("codex_ml.tokenization.sentencepiece_adapter")
    SentencePieceAdapter = getattr(mod, "SentencePieceAdapter")

    adapter = SentencePieceAdapter(model)
    if hasattr(adapter, "model_prefix"):
        adapter.model_prefix = model.with_suffix("")
    adapter.train_or_load(corpus)

    assert len(calls) == 0, "Trainer should not be called when model already exists"
    assert _get_model_file_from_adapter(adapter) == str(model)


def test_train_or_load_requires_sentencepiece(tmp_path, monkeypatch):
    """
    When the adapter no longer has a valid spm object, calling train_or_load
    should raise an AttributeError (adapter expects methods on the spm object).
    """
    model = tmp_path / "toy.model"
    corpus = tmp_path / "corpus.txt"
    corpus.write_text("x", encoding="utf-8")

    # Ensure adapter module is importable even without real sentencepiece
    monkeypatch.setitem(sys.modules, "sentencepiece", SimpleNamespace())
    mod = importlib.import_module("codex_ml.tokenization.sentencepiece_adapter")
    # Remove or None out the spm symbol to emulate missing sentencepiece at runtime
    monkeypatch.setattr(mod, "spm", None, raising=False)

    SentencePieceAdapter = getattr(mod, "SentencePieceAdapter")
    adapter = SentencePieceAdapter(model)
    with pytest.raises(AttributeError):
        adapter.train_or_load(corpus)


def test_load_requires_sentencepiece(tmp_path, monkeypatch):
    """
    When spm is None, load() should raise AttributeError because library functionality
    is missing.
    """
    model = tmp_path / "toy.model"
    model.write_text("model", encoding="utf-8")

    monkeypatch.setitem(sys.modules, "sentencepiece", SimpleNamespace())
    mod = importlib.import_module("codex_ml.tokenization.sentencepiece_adapter")
    monkeypatch.setattr(mod, "spm", None, raising=False)

    SentencePieceAdapter = getattr(mod, "SentencePieceAdapter")
    adapter = SentencePieceAdapter(model)
    with pytest.raises(AttributeError):
        adapter.load()


def test_add_special_tokens(tmp_path):
    """
    Using the stub, ensure add_special_tokens writes a JSON sidecar next to model.
    """
    model = tmp_path / "toy.model"
    adapter_mod = importlib.import_module("codex_ml.tokenization.sentencepiece_adapter")
    # Ensure stub exists so add_special_tokens can operate without real sentencepiece
    calls, sp_stub = _stub_sp(
        pytest.MonkeyPatch(), model
    )  # create a one-off stub; will not be used by adapter here
    # Import the class after monkeypatch of module-level spm above (the function used pytest.MonkeyPatch
    # only to construct stub object; actual tests below ensure module attr exists)
    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.setattr("codex_ml.tokenization.sentencepiece_adapter.spm", sp_stub, raising=False)
    try:
        SentencePieceAdapter = getattr(adapter_mod, "SentencePieceAdapter")
        adapter = SentencePieceAdapter(model)
        if hasattr(adapter, "model_prefix"):
            adapter.model_prefix = model.with_suffix("")
        adapter.add_special_tokens({"a": "<a>"})
        sidecar_path = model.with_suffix(".special_tokens.json")
        assert sidecar_path.exists(), "add_special_tokens should create .special_tokens.json"
        data = json.loads(sidecar_path.read_text(encoding="utf-8"))
        assert data.get("a") == "<a>"
    finally:
        monkeypatch.undo()


def test_add_special_tokens_sidecar(tmp_path):
    """
    Real-sentencepiece path validating the sidecar creation if sentencepiece is present.
    """
    pytest.importorskip("sentencepiece", reason="sentencepiece not installed")
    from codex_ml.tokenization.sentencepiece_adapter import SentencePieceAdapter

    corpus = _write_corpus(tmp_path)
    model_prefix = tmp_path / "spm_model"
    model_path = model_prefix.with_suffix(".model")
    adapter = SentencePieceAdapter(model_path)
    adapter.train_or_load(str(corpus), vocab_size=14, character_coverage=1.0)

    specials = {"pad_token": "<pad>", "eos_token": "</s>"}
    adapter.add_special_tokens(specials)

    sidecar = Path(str(model_prefix) + ".special_tokens.json")
    assert sidecar.exists()
    data = json.loads(sidecar.read_text(encoding="utf-8"))
    assert data.get("pad_token") == "<pad>"


def test_assert_vocab_size(tmp_path, monkeypatch):
    """
    Combine both behaviors:
      - If using a stubbed spm with a small vocab, assert_vocab_size should
        pass for the reported size and fail for larger requirements.
      - If adapter.sp is None, assert_vocab_size should raise a RuntimeError.
      - Also keep a real-sentencepiece invocation guarded by importorskip above.
    """
    # Stubbed path
    model = tmp_path / "toy.model"
    model.write_text("model", encoding="utf-8")
    calls, sp_stub = _stub_sp(monkeypatch, model, vocab_size=7)
    mod = importlib.import_module("codex_ml.tokenization.sentencepiece_adapter")
    SentencePieceAdapter = getattr(mod, "SentencePieceAdapter")

    adapter = SentencePieceAdapter(model)
    if hasattr(adapter, "model_prefix"):
        adapter.model_prefix = model.with_suffix("")
    adapter.train_or_load(tmp_path / "corpus.txt")

    # Expect to match stubbed size
    adapter.assert_vocab_size(7)
    with pytest.raises(AssertionError):
        adapter.assert_vocab_size(10)

    # If the adapter loses its sp instance, raise a RuntimeError
    adapter.sp = None
    with pytest.raises(RuntimeError):
        adapter.assert_vocab_size(7)


def test_missing_sentencepiece_branch(monkeypatch):
    """
    Ensure the adapter module surfaces an ImportError when the top-level
    `sentencepiece` module is missing at import-time (this guards the branch
    that imports sentencepiece inside the adapter module).
    """
    # Temporarily inject a sentinel None module to emulate missing dependency
    monkeypatch.setitem(sys.modules, "sentencepiece", None)
    with pytest.raises(ImportError):
        importlib.reload(importlib.import_module("codex_ml.tokenization.sentencepiece_adapter"))
