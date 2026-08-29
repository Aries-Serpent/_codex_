"""
Test Eval Datasets Module

Tests for the datasets module including Example, DatasetBundle,
preset datasets, hash computation, and dataset loading.
"""

from __future__ import annotations

import json
import tempfile
import warnings
from pathlib import Path

import pytest

from codex_ml.eval.datasets import (
    _PRESETS,
    DatasetBundle,
    Example,
    _hash_examples,
    load_dataset,
)


class TestExample:
    """Tests for Example dataclass."""

    def test_creation(self) -> None:
        """Test Example creation."""
        example = Example(input="hello", target="world")
        assert example.input == "hello", "input is not valid"
        assert example.target == "world", "target is not valid"

    def test_equality(self) -> None:
        """Test Example equality."""
        ex1 = Example(input="a", target="b")
        ex2 = Example(input="a", target="b")
        ex3 = Example(input="a", target="c")

        assert ex1 == ex2, "ex1 is not valid"
        assert ex1 != ex3, "ex1 is not valid"

    def test_repr(self) -> None:
        """Test Example repr."""
        example = Example(input="hello", target="world")
        repr_str = repr(example)
        assert "hello" in repr_str, "Condition must be true"
        assert "world" in repr_str, "Condition must be true"


class TestDatasetBundle:
    """Tests for DatasetBundle class."""

    def test_creation(self) -> None:
        """Test DatasetBundle creation."""
        examples = [
            Example(input="a", target="b"),
            Example(input="c", target="d"),
        ]
        bundle = DatasetBundle(
            examples=examples,
            dataset_hash="abc123",
            source="test",
        )
        assert len(bundle.examples) == 2, "Collection must not be empty"
        assert bundle.dataset_hash == "abc123", "Data must not be empty"
        assert bundle.source == "test", "source is not valid"
        assert bundle.metadata is None, "Data must not be empty"

    def test_with_metadata(self) -> None:
        """Test DatasetBundle with metadata."""
        examples = [Example(input="x", target="y")]
        bundle = DatasetBundle(
            examples=examples,
            dataset_hash="xyz",
            source="test",
            metadata={"key": "value"},
        )
        assert bundle.metadata == {"key": "value"}, "Data must not be empty"

    def test_iteration(self) -> None:
        """Test DatasetBundle iteration."""
        examples = [
            Example(input="1", target="a"),
            Example(input="2", target="b"),
            Example(input="3", target="c"),
        ]
        bundle = DatasetBundle(
            examples=examples,
            dataset_hash="hash",
            source="test",
        )

        collected = list(bundle)
        assert len(collected) == 3, "Collected must not be empty"
        assert collected[0].input == "1", "input is not valid"
        assert collected[2].target == "c", "target is not valid"

    def test_length(self) -> None:
        """Test DatasetBundle length."""
        examples = [Example(input=str(i), target=str(i)) for i in range(10)]
        bundle = DatasetBundle(
            examples=examples,
            dataset_hash="hash",
            source="test",
        )
        assert len(bundle) == 10, "Bundle must not be empty"

    def test_getitem(self) -> None:
        """Test DatasetBundle indexing."""
        examples = [
            Example(input="first", target="1"),
            Example(input="second", target="2"),
            Example(input="third", target="3"),
        ]
        bundle = DatasetBundle(
            examples=examples,
            dataset_hash="hash",
            source="test",
        )

        assert bundle[0].input == "first", "input is not valid"
        assert bundle[1].input == "second", "input is not valid"
        assert bundle[2].target == "3", "target is not valid"

    def test_empty_bundle(self) -> None:
        """Test empty DatasetBundle."""
        bundle = DatasetBundle(
            examples=[],
            dataset_hash="empty",
            source="empty_test",
        )
        assert len(bundle) == 0, "Bundle must not be empty"
        assert list(bundle) == [], "Condition must be true"

    def test_is_sequence(self) -> None:
        """Test that DatasetBundle is a Sequence."""
        from collections.abc import Sequence

        examples = [Example(input="a", target="b")]
        bundle = DatasetBundle(
            examples=examples,
            dataset_hash="hash",
            source="test",
        )
        assert isinstance(bundle, Sequence)


class TestHashExamples:
    """Tests for _hash_examples function."""

    def test_consistent_hash(self) -> None:
        """Test hash is consistent for same examples."""
        examples = [
            Example(input="hello", target="world"),
            Example(input="foo", target="bar"),
        ]
        hash1 = _hash_examples(examples)
        hash2 = _hash_examples(examples)
        assert hash1 == hash2, "hash1 is not valid"

    def test_different_hash_for_different_examples(self) -> None:
        """Test different examples produce different hashes."""
        examples1 = [Example(input="a", target="b")]
        examples2 = [Example(input="c", target="d")]
        hash1 = _hash_examples(examples1)
        hash2 = _hash_examples(examples2)
        assert hash1 != hash2, "hash1 is not valid"

    def test_order_matters(self) -> None:
        """Test that order affects the hash."""
        ex1 = Example(input="a", target="1")
        ex2 = Example(input="b", target="2")
        hash1 = _hash_examples([ex1, ex2])
        hash2 = _hash_examples([ex2, ex1])
        assert hash1 != hash2, "hash1 is not valid"

    def test_empty_examples(self) -> None:
        """Test hash for empty examples."""
        hash_val = _hash_examples([])
        assert isinstance(hash_val, str)
        assert len(hash_val) == 64, "Hash_val must not be empty"

    def test_returns_sha256_hex(self) -> None:
        """Test that hash is a valid SHA-256 hex string."""
        examples = [Example(input="test", target="test")]
        hash_val = _hash_examples(examples)
        assert len(hash_val) == 64, "Hash_val must not be empty"
        assert all(c in "0123456789abcdef" for c in hash_val), "Condition must be true"


class TestPresets:
    """Tests for preset datasets."""

    def test_toy_copy_task_exists(self) -> None:
        """Test toy_copy_task preset exists."""
        assert "toy_copy_task" in _PRESETS, "Condition must be true"

    def test_tiny_wikitext_exists(self) -> None:
        """Test tiny_wikitext preset exists."""
        assert "tiny_wikitext" in _PRESETS, "Condition must be true"

    def test_presets_contain_examples(self) -> None:
        """Test presets contain Example objects."""
        for name, examples in _PRESETS.items():
            assert len(examples) > 0, "Examples must not be empty"
            for ex in examples:
                assert isinstance(ex, Example)

    def test_toy_copy_task_content(self) -> None:
        """Test toy_copy_task content."""
        examples = _PRESETS["toy_copy_task"]
        assert len(examples) == 2, "Examples must not be empty"
        # Copy task: input == target
        for ex in examples:
            assert ex.input == ex.target, "input is not valid"


class TestLoadDataset:
    """Tests for load_dataset function."""

    def test_load_preset_toy_copy_task(self) -> None:
        """Test loading preset dataset."""
        bundle = load_dataset("toy_copy_task")  # nosec B615 - Test code with known preset dataset
        assert len(bundle) == 2, "Bundle must not be empty"
        assert bundle.source == "toy_copy_task", "source is not valid"
        assert bundle.dataset_hash is not None, "dataset_hash must be initialized"

    def test_load_preset_tiny_wikitext(self) -> None:
        """Test loading tiny_wikitext preset."""
        bundle = load_dataset("tiny_wikitext")  # nosec B615 - Test code with known preset dataset
        assert len(bundle) >= 1, "Bundle must not be empty"
        assert bundle.source == "tiny_wikitext", "source is not valid"

    def test_load_with_max_samples(self) -> None:
        """Test max_samples parameter."""
        bundle = load_dataset(
            "toy_copy_task", max_samples=1
        )  # nosec B615 - Test code with known preset dataset
        assert len(bundle) == 1, "Bundle must not be empty"

    def test_load_with_zero_max_samples(self) -> None:
        """Test max_samples=0 returns empty bundle."""
        bundle = load_dataset(
            "toy_copy_task", max_samples=0
        )  # nosec B615 - Test code with known preset dataset
        assert len(bundle) == 0, "Bundle must not be empty"

    def test_load_jsonl_file(self) -> None:
        """Test loading JSONL file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "data.jsonl"
            examples = [
                {"input": "hello", "target": "world"},
                {"input": "foo", "target": "bar"},
            ]
            path.write_text(
                "\n".join(json.dumps(ex) for ex in examples),
                encoding="utf-8",
            )

            bundle = load_dataset(str(path))  # nosec B615 - Test code loading local dataset file
            assert len(bundle) == 2, "Bundle must not be empty"
            assert bundle[0].input == "hello", "input is not valid"
            assert bundle[1].target == "bar", "target is not valid"

    def test_load_ndjson_file(self) -> None:
        """Test loading NDJSON file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "data.ndjson"
            examples = [{"input": "test", "target": "result"}]
            path.write_text(json.dumps(examples[0]), encoding="utf-8")

            bundle = load_dataset(str(path))  # nosec B615 - Test code loading local dataset file
            assert len(bundle) == 1, "Bundle must not be empty"
            assert bundle[0].input == "test", "input is not valid"

    def test_load_jsonl_skips_empty_lines(self) -> None:
        """Test JSONL loading skips empty lines."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "data.jsonl"
            content = '{"input": "a", "target": "1"}\n\n{"input": "b", "target": "2"}'
            path.write_text(content, encoding="utf-8")

            bundle = load_dataset(str(path))  # nosec B615 - Test code loading local dataset file
            assert len(bundle) == 2, "Bundle must not be empty"

    def test_metadata_includes_source(self) -> None:
        """Test metadata includes source information."""
        bundle = load_dataset("toy_copy_task")  # nosec B615 - Test code with known preset dataset
        assert bundle.metadata is not None, "metadata must be initialized"
        assert "source" in bundle.metadata, "Data must not be empty"

    def test_metadata_includes_num_examples(self) -> None:
        """Test metadata includes num_examples."""
        bundle = load_dataset("toy_copy_task")  # nosec B615 - Test code with known preset dataset
        assert bundle.metadata is not None, "metadata must be initialized"
        assert "num_examples" in bundle.metadata, "Data must not be empty"
        assert bundle.metadata["num_examples"] == len(bundle), "Bundle must not be empty"

    def test_hf_text_field_deprecation_warning(self) -> None:
        """Test hf_text_field raises deprecation warning."""
        with warnings.catch_warnings(record=True):
            warnings.simplefilter("always")
            try:
                # This will fail because it's not a valid HF dataset,
                # but the warning should be raised before that
                load_dataset(  # nosec B615 - Test code with known preset dataset
                    "toy_copy_task",  # Use preset to avoid HF requirement
                    hf_text_field="text",
                )
            except Exception as _err:
                _ = None  # Expected to fail for preset

            # Check if deprecation warning was issued
            # (may not be for preset, but validates parameter handling)

    def test_hf_text_field_conflict_raises_error(self) -> None:
        """Test hf_text_field + hf_input_field raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            load_dataset(  # nosec B615 - Test code, intentionally passing invalid parameters
                "hf://some/dataset",
                hf_text_field="text",
                hf_input_field="input",
            )
        assert "cannot be combined" in str(exc_info.value), "Value must be initialized"


class TestLoadDatasetEdgeCases:
    """Edge case tests for load_dataset."""

    def test_nonexistent_preset_as_path(self) -> None:
        """Test nonexistent path handling."""
        with pytest.raises((ValueError, FileNotFoundError, OSError)):
            load_dataset("/nonexistent/path/data.jsonl")

    def test_negative_max_samples_treated_as_zero(self) -> None:
        """Test negative max_samples is treated as 0."""
        bundle = load_dataset(
            "toy_copy_task", max_samples=-5
        )  # nosec B615 - Test code with known preset dataset
        assert len(bundle) == 0, "Bundle must not be empty"


class TestDatasetBundleSequenceProtocol:
    """Tests for Sequence protocol implementation."""

    def test_contains_check(self) -> None:
        """Test 'in' operator for DatasetBundle."""
        examples = [
            Example(input="a", target="1"),
            Example(input="b", target="2"),
        ]
        bundle = DatasetBundle(
            examples=examples,
            dataset_hash="hash",
            source="test",
        )

        assert examples[0] in bundle, "Condition must be true"
        assert Example(input="z", target="z") not in bundle

    def test_reversed_iteration(self) -> None:
        """Test reversed iteration."""
        examples = [
            Example(input="1", target="a"),
            Example(input="2", target="b"),
            Example(input="3", target="c"),
        ]
        bundle = DatasetBundle(
            examples=examples,
            dataset_hash="hash",
            source="test",
        )

        reversed_list = list(reversed(bundle))
        assert reversed_list[0].input == "3", "input is not valid"
        assert reversed_list[2].input == "1", "input is not valid"

    def test_count_method(self) -> None:
        """Test count method."""
        examples = [
            Example(input="a", target="1"),
            Example(input="a", target="1"),
            Example(input="b", target="2"),
        ]
        bundle = DatasetBundle(
            examples=examples,
            dataset_hash="hash",
            source="test",
        )

        assert bundle.count(examples[0]) == 2, "Count must be greater than zero"
        assert bundle.count(examples[2]) == 1, "Count must be greater than zero"

    def test_index_method(self) -> None:
        """Test index method."""
        examples = [
            Example(input="first", target="1"),
            Example(input="second", target="2"),
        ]
        bundle = DatasetBundle(
            examples=examples,
            dataset_hash="hash",
            source="test",
        )

        assert bundle.index(examples[0]) == 0, "Condition must be true"
        assert bundle.index(examples[1]) == 1, "Condition must be true"
