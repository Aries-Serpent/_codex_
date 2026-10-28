"""Positive and negative contracts for the actual Phase 7B batch-3 APIs.

Prior art: tests/test_token_cache.py, tests/test_make_generator_worker_seed.py,
tests/tokenization/test_hf_adapter_canonical.py, tests/codex_ml/registry/test_base.py,
docs/dev/plugins.md, and docs/how-to/dataset_manifest.md.
No model downloads are needed: the tokenizer uses a local WordLevel artifact,
and tensor checks use small CPU tensors.
"""

from __future__ import annotations

import hashlib
import json
import math
import random
from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from tokenizers import Tokenizer
from tokenizers.models import WordLevel
from tokenizers.pre_tokenizers import Whitespace

import torch
from codex_ml.interfaces import tokenizer_hf
from codex_ml.metrics import text
from codex_ml.registry import base, token_cache
from codex_ml.tokenization import hf_adapter
from codex_ml.training import dataloader_utils
from codex_ml.training.device_strategy import DeviceConfig
from codex_ml.training.rng_checkpoint import RNGState
from data.manifest import DatasetManifest


class TestTokenLRU:
    def test_put_get_clear(self):
        cache = token_cache.TokenLRU()
        assert cache.get("missing") is None
        value = [1, 2]
        cache.put("tokens", value)
        assert cache.get("tokens") is value
        cache.clear()
        assert cache.get("tokens") is None

    def test_read_refreshes_recency(self):
        cache = token_cache.TokenLRU(maxsize=2)
        cache.put("a", 1)
        cache.put("b", 2)
        assert cache.get("a") == 1
        cache.put("c", 3)
        assert cache.get("b") is None
        assert cache.get("a") == 1
        assert cache.get("c") == 3

    def test_overwrite_refreshes_recency_without_extra_slot(self):
        cache = token_cache.TokenLRU(maxsize=2)
        cache.put("a", 1)
        cache.put("b", 2)
        cache.put("a", 10)
        cache.put("c", 3)
        assert cache.get("a") == 10
        assert cache.get("b") is None
        assert cache.get("c") == 3

    @pytest.mark.parametrize("value", [0, False, "", [], {}])
    def test_falsey_values_are_hits(self, value):
        cache = token_cache.TokenLRU(maxsize=2)
        cache.put("falsey", value)
        cache.put("other", 1)
        assert cache.get("falsey") == value
        cache.put("new", 2)
        assert cache.get("other") is None
        assert cache.get("falsey") == value

    def test_zero_capacity_retains_nothing(self):
        cache = token_cache.TokenLRU(maxsize=0)
        cache.put("a", 1)
        assert cache.get("a") is None

    def test_negative_capacity_is_unbounded(self):
        cache = token_cache.TokenLRU(maxsize=-1)
        for index in range(20):
            cache.put(index, index + 1)
        assert [cache.get(index) for index in range(20)] == list(range(1, 21))

    def test_missing_read_does_not_evict_or_refresh(self):
        cache = token_cache.TokenLRU(maxsize=2)
        cache.put("a", 1)
        cache.put("b", 2)
        assert cache.get("absent") is None
        cache.put("c", 3)
        assert cache.get("a") is None
        assert cache.get("b") == 2

    def test_tuple_key_encodes_all_tokenization_options(self):
        options = ("hello", False, False, 10, True)
        original = token_cache.cache_key(*options)
        assert original == options
        cache = token_cache.TokenLRU()
        cache.put(original, [1])
        for index, replacement in enumerate(("other", True, True, 20, False)):
            changed = list(options)
            changed[index] = replacement
            assert cache.get(token_cache.cache_key(*changed)) is None
        assert cache.get(original) == [1]

    @pytest.mark.parametrize(
        ("flag", "expected"),
        [
            (None, False),
            ("1", True),
            (" TRUE ", True),
            ("yes", True),
            ("on", True),
            ("0", False),
            ("false", False),
            ("", False),
            ("unknown", False),
        ],
    )
    def test_disable_environment_flag(self, monkeypatch, flag, expected):
        if flag is None:
            monkeypatch.delenv("CODEX_ML_TOKEN_CACHE_DISABLE", raising=False)
        else:
            monkeypatch.setenv("CODEX_ML_TOKEN_CACHE_DISABLE", flag)
        assert token_cache.is_cache_disabled() is expected


@pytest.fixture
def tokenizer_artifact(tmp_path):
    backend = Tokenizer(
        WordLevel(
            {"<unk>": 0, "<pad>": 1, "</s>": 2, "hello": 3, "world": 4, "café": 5},
            unk_token="<unk>",
        )
    )
    backend.pre_tokenizer = Whitespace()
    path = tmp_path / "tokenizer.json"
    backend.save(str(path))
    return path


@pytest.fixture
def adapter(tokenizer_artifact):
    return hf_adapter.HFTokenizerAdapter(str(tokenizer_artifact))


class TestHFTokenizerAdapter:
    def test_deprecated_interface_is_canonical_adapter(self):
        assert tokenizer_hf.HFTokenizerAdapter is hf_adapter.HFTokenizerAdapter

    @pytest.mark.parametrize(
        ("value", "ids"), [("", []), ("hello world", [3, 4]), ("café", [5]), ("unknown", [0])]
    )
    def test_encode_local_artifact(self, adapter, value, ids):
        assert adapter.encode(value) == ids

    def test_decode_accepts_iterable_and_roundtrips(self, adapter):
        ids = adapter.encode("hello world", add_special_tokens=False)
        assert adapter.decode(iter(ids), skip_special_tokens=False) == "hello world"

    def test_vocab_and_special_ids(self, adapter):
        assert adapter.vocab_size == 6
        assert adapter.pad_token_id == adapter.pad_id == 1
        assert adapter.eos_token_id == adapter.eos_id == 2

    def test_explicit_special_tokens(self, tokenizer_artifact):
        adapter = hf_adapter.HFTokenizerAdapter(
            str(tokenizer_artifact), pad_token="hello", eos_token="world"
        )
        assert adapter.pad_token_id == 3
        assert adapter.eos_token_id == 4

    def test_missing_special_tokens_use_documented_defaults(self, tmp_path):
        path = tmp_path / "plain.json"
        Tokenizer(WordLevel({"hello": 0, "world": 1})).save(str(path))
        adapter = hf_adapter.HFTokenizerAdapter(str(path))
        assert adapter.pad_id == 0
        assert adapter.eos_id == 1

    def test_missing_tokenizers_dependency_is_actionable(self, monkeypatch):
        monkeypatch.setattr(hf_adapter, "_FastTokenizer", None)
        with pytest.raises(ImportError, match="tokenizers is required for HFTokenizerAdapter"):
            hf_adapter.HFTokenizerAdapter("unused.json")

    def test_missing_artifact_is_not_silently_ignored(self, tmp_path):
        # tokenizers' Rust boundary raises its documented generic Exception.
        with pytest.raises(Exception, match="No such file or directory"):
            hf_adapter.HFTokenizerAdapter(str(tmp_path / "missing.json"))

    @pytest.mark.parametrize(
        ("configured", "fallback", "expected"),
        [
            (None, None, torch.int64),
            (None, torch.float32, torch.float32),
            (torch.float64, torch.float32, torch.float64),
        ],
    )
    def test_device_alignment_dtype_precedence(self, configured, fallback, expected):
        tensor = torch.tensor([1, 2], dtype=torch.int64)
        result = tokenizer_hf.align_tensor_to_device(
            tensor, DeviceConfig(device="cpu", dtype=configured), fallback_dtype=fallback
        )
        assert result.device.type == "cpu"
        assert result.dtype == expected
        assert result.tolist() == [1, 2]

    def test_no_device_configuration_preserves_tensor(self):
        tensor = torch.tensor([1])
        assert tokenizer_hf.align_tensor_to_device(tensor, None) is tensor

    def test_no_torch_alignment_is_identity(self, monkeypatch):
        monkeypatch.setattr(tokenizer_hf, "torch", None)
        sentinel = object()
        assert (
            tokenizer_hf.align_tensor_to_device(sentinel, DeviceConfig(device="cpu", dtype=None))
            is sentinel
        )


@pytest.fixture
def preserve_rng():
    state = RNGState()
    state.capture()
    yield
    state.restore()


class TestDataloaderSeeding:
    @pytest.mark.parametrize("seed", [0, 123, 2**31 - 1])
    def test_generator_reproducibility_without_global_reseed(self, seed):
        before = torch.get_rng_state().clone()
        first = dataloader_utils.make_generator(seed)
        second = dataloader_utils.make_generator(seed)
        assert isinstance(first, torch.Generator)
        assert first is not second
        assert torch.equal(
            torch.randint(0, 1000, (8,), generator=first),
            torch.randint(0, 1000, (8,), generator=second),
        )
        assert torch.equal(torch.get_rng_state(), before)

    @pytest.mark.parametrize("backend", [None, SimpleNamespace()])
    def test_no_generator_backend_returns_none(self, monkeypatch, backend):
        monkeypatch.setattr(dataloader_utils, "torch", backend)
        assert dataloader_utils.make_generator(5) is None

    def test_generator_errors_propagate(self, monkeypatch):
        constructor = Mock(side_effect=RuntimeError("backend failed"))
        monkeypatch.setattr(dataloader_utils, "torch", SimpleNamespace(Generator=constructor))
        with pytest.raises(RuntimeError, match="backend failed"):
            dataloader_utils.make_generator(5)

    @pytest.mark.parametrize("worker_id", [0, 1, 17])
    def test_worker_seeds_python_numpy_and_torch(self, monkeypatch, preserve_rng, worker_id):
        numpy_seed = Mock()
        torch_seed = Mock()
        getbits = Mock(return_value=123456)
        monkeypatch.setattr(dataloader_utils.random, "getrandbits", getbits)
        monkeypatch.setattr(
            dataloader_utils, "np", SimpleNamespace(random=SimpleNamespace(seed=numpy_seed))
        )
        monkeypatch.setattr(dataloader_utils, "torch", SimpleNamespace(manual_seed=torch_seed))
        dataloader_utils.seed_worker(worker_id)
        getbits.assert_called_once_with(32)
        numpy_seed.assert_called_once_with(123456)
        torch_seed.assert_called_once_with(123456)
        assert random.random() == random.Random(123456).random()

    def test_worker_seeds_python_without_optional_backends(self, monkeypatch, preserve_rng):
        monkeypatch.setattr(dataloader_utils, "np", None)
        monkeypatch.setattr(dataloader_utils, "torch", None)
        monkeypatch.setattr(dataloader_utils.random, "getrandbits", lambda bits: 99)
        dataloader_utils.seed_worker(0)
        assert random.random() == random.Random(99).random()


class TestDatasetManifest:
    @pytest.mark.parametrize("filename", ["shard.jsonl", "space name.txt", "café-日本語.txt"])
    def test_build_write_load_verify(self, tmp_path, monkeypatch, filename):
        monkeypatch.setenv("SOURCE_DATE_EPOCH", "1234567890")
        payload = "hello café\n".encode()
        (tmp_path / filename).write_bytes(payload)
        manifest = DatasetManifest.build(tmp_path, [filename])
        manifest.dataset_id = "local-dataset"
        assert manifest.created_at == 1234567890
        assert len(manifest.shards) == 1
        shard = manifest.shards[0]
        assert (shard.path, shard.size, shard.sha256) == (
            filename,
            len(payload),
            hashlib.sha256(payload).hexdigest(),
        )
        path = tmp_path / "manifest.json"
        assert manifest.write(path) == path
        before = path.read_bytes()
        loaded = DatasetManifest.load(path)
        assert loaded == manifest
        assert loaded.verify(tmp_path) is None
        assert path.read_bytes() == before
        assert json.loads(manifest.to_json())["dataset_id"] == "local-dataset"

    def test_empty_manifest_and_independent_shard_lists(self, tmp_path):
        first, second = DatasetManifest(), DatasetManifest()
        assert first.shards == second.shards == []
        assert first.shards is not second.shards
        assert first.verify(tmp_path) is None

    def test_build_preserves_requested_shard_order(self, tmp_path):
        for name in ("b", "a"):
            (tmp_path / name).write_bytes(name.encode())
        manifest = DatasetManifest.build(tmp_path, ["b", "a"])
        assert [shard.path for shard in manifest.shards] == ["b", "a"]

    def test_build_missing_shard_raises(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            DatasetManifest.build(tmp_path, ["missing"])

    @pytest.mark.parametrize("mutation", ["missing", "checksum"])
    def test_verify_detects_missing_or_changed_shards(self, tmp_path, mutation):
        path = tmp_path / "shard"
        path.write_bytes(b"original")
        manifest = DatasetManifest.build(tmp_path, ["shard"])
        if mutation == "missing":
            path.unlink()
        else:
            path.write_bytes(b"modified")
        with pytest.raises(
            ValueError,
            match=(
                "Missing shard: shard" if mutation == "missing" else "Checksum mismatch for shard"
            ),
        ):
            manifest.verify(tmp_path)

    def test_load_invalid_json_raises(self, tmp_path):
        path = tmp_path / "bad.json"
        path.write_text("{")
        with pytest.raises(json.JSONDecodeError):
            DatasetManifest.load(path)

    def test_load_missing_file_raises(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            DatasetManifest.load(tmp_path / "missing.json")

    def test_load_defaults_for_absent_optional_fields(self, tmp_path):
        path = tmp_path / "minimal.json"
        path.write_text("{}")
        manifest = DatasetManifest.load(path)
        assert manifest.schema_version == "1.0"
        assert manifest.created_at == 0
        assert manifest.dataset_id is None
        assert manifest.shards == []


class TestRegistry:
    def test_registration_decorator_and_case_insensitive_lookup(self):
        registry = base.Registry("test")

        @registry.register("Example")
        def component():
            return "component"

        assert registry.get("EXAMPLE") is component
        assert registry.get("example")() == "component"
        assert registry.list() == ["example"]

    def test_list_is_sorted(self):
        registry = base.Registry("test")
        registry.register("Z", 1)
        registry.register("A", 2)
        assert registry.list() == ["a", "z"]

    def test_duplicate_rejected_and_explicit_override(self):
        registry = base.Registry("test")
        registry.register("item", 1, source="first")
        with pytest.raises(base.RegistryConflictError, match="Existing source: first"):
            registry.register("ITEM", 2, source="second")
        assert registry.get("item") == 1
        registry.register("ITEM", 3, override=True)
        assert registry.get("item") == 3

    def test_unknown_key_lists_available_components(self):
        registry = base.Registry("test")
        registry.register("known", 1)
        with pytest.raises(base.RegistryNotFoundError, match="Available: known"):
            registry.get("missing")

    @pytest.mark.parametrize("fail_inside", [False, True])
    def test_temporary_registration_restores_state(self, fail_inside):
        registry = base.Registry("test")
        registry.register("existing", 1)

        def use_temporary():
            with registry.temporarily_registered({"existing": 2, "new": 3}):
                assert registry.get("EXISTING") == 2
                assert registry.get("new") == 3
                if fail_inside:
                    raise ValueError("body failure")

        if fail_inside:
            with pytest.raises(ValueError, match="body failure"):
                use_temporary()
        else:
            use_temporary()
        assert registry.get("existing") == 1
        assert registry.list() == ["existing"]
        with pytest.raises(base.RegistryNotFoundError):
            registry.get("new")

    def test_entrypoints_lazy_and_loaded_once(self, monkeypatch):
        plugin = object()
        load = Mock(return_value=plugin)
        entrypoint = SimpleNamespace(name="Plugin", value="package:plugin", load=load)
        discover = Mock(return_value=[entrypoint])
        monkeypatch.setattr(base.metadata, "entry_points", discover)
        registry = base.Registry("test", entry_point_group="test.plugins")
        registry.register("local", object())
        registry.get("LOCAL")
        discover.assert_not_called()
        assert registry.get("PLUGIN") is plugin
        assert registry.list() == ["local", "plugin"]
        discover.assert_called_once_with(group="test.plugins")
        load.assert_called_once_with()

    @pytest.mark.parametrize("allow_override", [False, True])
    def test_entrypoint_collision_policy(self, monkeypatch, allow_override):
        load = Mock(return_value="plugin")
        entrypoint = SimpleNamespace(name="ITEM", value="package:item", load=load)
        monkeypatch.setattr(base.metadata, "entry_points", Mock(return_value=[entrypoint]))
        registry = base.Registry(
            "test",
            entry_point_group="test.plugins",
            allow_entrypoint_overrides=allow_override,
        )
        registry.register("item", "local")
        assert registry.list() == ["item"]  # Explicitly triggers discovery.
        assert registry.get("item") == ("plugin" if allow_override else "local")
        assert load.call_count == int(allow_override)

    @pytest.mark.parametrize("error_type", [ValueError, TypeError])
    def test_failed_entrypoint_reports_original_cause(self, monkeypatch, error_type):
        original = error_type("bad plugin")
        entrypoint = SimpleNamespace(
            name="broken", value="package:broken", load=Mock(side_effect=original)
        )
        monkeypatch.setattr(base.metadata, "entry_points", Mock(return_value=[entrypoint]))
        registry = base.Registry("test", entry_point_group="test.plugins")
        with pytest.raises(base.RegistryLoadError, match="bad plugin") as error:
            registry.get("broken")
        assert error.value.__cause__ is original
        assert registry.list() == []


class TestTextMetrics:
    @pytest.mark.parametrize(
        ("loss", "expected"), [(0.0, 1.0), (math.log(2), 2.0), (1.0, math.e), (-1.0, 1 / math.e)]
    )
    def test_perplexity_from_cross_entropy(self, loss, expected):
        assert text.perplexity(loss) == pytest.approx(expected)

    def test_perplexity_overflow_is_infinity(self):
        assert text.perplexity(1000.0) == float("inf")

    def test_perplexity_invalid_input_raises(self):
        with pytest.raises(TypeError):
            text.perplexity(None)

    @pytest.mark.parametrize(("targets", "expected"), [([0, 1], 1.0), ([1, 0], 0.0), ([0, 0], 0.5)])
    def test_token_accuracy_uses_argmax(self, targets, expected):
        logits = torch.tensor([[[5.0, 1.0], [1.0, 5.0]]])
        assert text.token_accuracy(logits, torch.tensor([targets])) == expected

    def test_empty_token_accuracy_is_zero(self):
        logits = torch.empty((0, 2))
        targets = torch.empty((0,), dtype=torch.long)
        assert text.token_accuracy(logits, targets) == 0.0

    def test_token_accuracy_requires_torch(self, monkeypatch):
        monkeypatch.setattr(text, "_HAS_TORCH", False)
        monkeypatch.setattr(text, "_torch", None)
        with pytest.raises(ImportError, match="PyTorch is required for token_accuracy"):
            text.token_accuracy(None, None)
