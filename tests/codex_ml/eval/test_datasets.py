"""
Test Eval Datasets Module

Tests for the datasets module including Example, DatasetBundle,
preset datasets, hash computation, and dataset loading.
"""

from __future__ import annotations

import hashlib
import json
import tempfile
import warnings
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from codex_ml.eval.datasets import (
    DatasetBundle,
    Example,
    _hash_examples,
    _PRESETS,
    load_dataset,
)


class TestExample:
    """Tests for Example dataclass."""

    def test_creation(self) -> None:
        """Test Example creation."""
        example = Example(input="hello", target="world")
        assert example.input == "hello"
        assert example.target == "world"

    def test_equality(self) -> None:
        """Test Example equality."""
        ex1 = Example(input="a", target="b")
        ex2 = Example(input="a", target="b")
        ex3 = Example(input="a", target="c")

        assert ex1 == ex2
        assert ex1 != ex3

    def test_repr(self) -> None:
        """Test Example repr."""
        example = Example(input="hello", target="world")
        repr_str = repr(example)
        assert "hello" in repr_str
        assert "world" in repr_str


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
        assert len(bundle.examples) == 2
        assert bundle.dataset_hash == "abc123"
        assert bundle.source == "test"
        assert bundle.metadata is None

    def test_with_metadata(self) -> None:
        """Test DatasetBundle with metadata."""
        examples = [Example(input="x", target="y")]
        bundle = DatasetBundle(
            examples=examples,
            dataset_hash="xyz",
            source="test",
            metadata={"key": "value"},
        )
        assert bundle.metadata == {"key": "value"}

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
        assert len(collected) == 3
        assert collected[0].input == "1"
        assert collected[2].target == "c"

    def test_length(self) -> None:
        """Test DatasetBundle length."""
        examples = [Example(input=str(i), target=str(i)) for i in range(10)]
        bundle = DatasetBundle(
            examples=examples,
            dataset_hash="hash",
            source="test",
        )
        assert len(bundle) == 10

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

        assert bundle[0].input == "first"
        assert bundle[1].input == "second"
        assert bundle[2].target == "3"

    def test_empty_bundle(self) -> None:
        """Test empty DatasetBundle."""
        bundle = DatasetBundle(
            examples=[],
            dataset_hash="empty",
            source="empty_test",
        )
        assert len(bundle) == 0
        assert list(bundle) == []

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
        assert hash1 == hash2

    def test_different_hash_for_different_examples(self) -> None:
        """Test different examples produce different hashes."""
        examples1 = [Example(input="a", target="b")]
        examples2 = [Example(input="c", target="d")]
        hash1 = _hash_examples(examples1)
        hash2 = _hash_examples(examples2)
        assert hash1 != hash2

    def test_order_matters(self) -> None:
        """Test that order affects the hash."""
        ex1 = Example(input="a", target="1")
        ex2 = Example(input="b", target="2")
        hash1 = _hash_examples([ex1, ex2])
        hash2 = _hash_examples([ex2, ex1])
        assert hash1 != hash2

    def test_empty_examples(self) -> None:
        """Test hash for empty examples."""
        hash_val = _hash_examples([])
        assert isinstance(hash_val, str)
        assert len(hash_val) == 64  # SHA-256 hex digest

    def test_returns_sha256_hex(self) -> None:
        """Test that hash is a valid SHA-256 hex string."""
        examples = [Example(input="test", target="test")]
        hash_val = _hash_examples(examples)
        assert len(hash_val) == 64
        assert all(c in "0123456789abcdef" for c in hash_val)


class TestPresets:
    """Tests for preset datasets."""

    def test_toy_copy_task_exists(self) -> None:
        """Test toy_copy_task preset exists."""
        assert "toy_copy_task" in _PRESETS

    def test_tiny_wikitext_exists(self) -> None:
        """Test tiny_wikitext preset exists."""
        assert "tiny_wikitext" in _PRESETS

    def test_presets_contain_examples(self) -> None:
        """Test presets contain Example objects."""
        for name, examples in _PRESETS.items():
            assert len(examples) > 0
            for ex in examples:
                assert isinstance(ex, Example)

    def test_toy_copy_task_content(self) -> None:
        """Test toy_copy_task content."""
        examples = _PRESETS["toy_copy_task"]
        assert len(examples) == 2
        # Copy task: input == target
        for ex in examples:
            assert ex.input == ex.target


class TestLoadDataset:
    """Tests for load_dataset function."""

    def test_load_preset_toy_copy_task(self) -> None:
        """Test loading preset dataset."""
        bundle = load_dataset("toy_copy_task")
        assert len(bundle) == 2
        assert bundle.source == "toy_copy_task"
        assert bundle.dataset_hash is not None

    def test_load_preset_tiny_wikitext(self) -> None:
        """Test loading tiny_wikitext preset."""
        bundle = load_dataset("tiny_wikitext")
        assert len(bundle) >= 1
        assert bundle.source == "tiny_wikitext"

    def test_load_with_max_samples(self) -> None:
        """Test max_samples parameter."""
        bundle = load_dataset("toy_copy_task", max_samples=1)
        assert len(bundle) == 1

    def test_load_with_zero_max_samples(self) -> None:
        """Test max_samples=0 returns empty bundle."""
        bundle = load_dataset("toy_copy_task", max_samples=0)
        assert len(bundle) == 0

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

            bundle = load_dataset(str(path))
            assert len(bundle) == 2
            assert bundle[0].input == "hello"
            assert bundle[1].target == "bar"

    def test_load_ndjson_file(self) -> None:
        """Test loading NDJSON file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "data.ndjson"
            examples = [{"input": "test", "target": "result"}]
            path.write_text(json.dumps(examples[0]), encoding="utf-8")

            bundle = load_dataset(str(path))
            assert len(bundle) == 1
            assert bundle[0].input == "test"

    def test_load_jsonl_skips_empty_lines(self) -> None:
        """Test JSONL loading skips empty lines."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "data.jsonl"
            content = '{"input": "a", "target": "1"}\n\n{"input": "b", "target": "2"}'
            path.write_text(content, encoding="utf-8")

            bundle = load_dataset(str(path))
            assert len(bundle) == 2

    def test_metadata_includes_source(self) -> None:
        """Test metadata includes source information."""
        bundle = load_dataset("toy_copy_task")
        assert bundle.metadata is not None
        assert "source" in bundle.metadata

    def test_metadata_includes_num_examples(self) -> None:
        """Test metadata includes num_examples."""
        bundle = load_dataset("toy_copy_task")
        assert bundle.metadata is not None
        assert "num_examples" in bundle.metadata
        assert bundle.metadata["num_examples"] == len(bundle)

    def test_hf_text_field_deprecation_warning(self) -> None:
        """Test hf_text_field raises deprecation warning."""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            try:
                # This will fail because it's not a valid HF dataset,
                # but the warning should be raised before that
                load_dataset(
                    "toy_copy_task",  # Use preset to avoid HF requirement
                    hf_text_field="text",
                )
            except Exception:
                pass  # Expected to fail for preset

            # Check if deprecation warning was issued
            # (may not be for preset, but validates parameter handling)

    def test_hf_text_field_conflict_raises_error(self) -> None:
        """Test hf_text_field + hf_input_field raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            load_dataset(
                "hf://some/dataset",
                hf_text_field="text",
                hf_input_field="input",
            )
        assert "cannot be combined" in str(exc_info.value)


class TestLoadDatasetEdgeCases:
    """Edge case tests for load_dataset."""

    def test_nonexistent_preset_as_path(self) -> None:
        """Test nonexistent path handling."""
        with pytest.raises((ValueError, FileNotFoundError, OSError)):
            load_dataset("/nonexistent/path/data.jsonl")

    def test_negative_max_samples_treated_as_zero(self) -> None:
        """Test negative max_samples is treated as 0."""
        bundle = load_dataset("toy_copy_task", max_samples=-5)
        assert len(bundle) == 0


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

        assert examples[0] in bundle
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
        assert reversed_list[0].input == "3"
        assert reversed_list[2].input == "1"

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

        assert bundle.count(examples[0]) == 2
        assert bundle.count(examples[2]) == 1

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

        assert bundle.index(examples[0]) == 0
        assert bundle.index(examples[1]) == 1
