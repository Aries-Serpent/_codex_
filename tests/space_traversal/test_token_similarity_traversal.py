"""Tests for token-similarity duplication heuristic."""

from __future__ import annotations

from pathlib import Path

import pytest


def test_duplication_ratio_token_similarity_basic():
    """Test basic token similarity duplication detection."""
    from scripts.space_traversal.dup_similarity import duplication_ratio_token_similarity

    # Create test data
    evidence_files = ["src/module_a.py", "src/module_b.py", "src/different_file.py"]

    file_cache = {
        "src/module_a.py": "def foo():\n    return 42\n",
        "src/module_b.py": "def foo():\n    return 42\n",
        "src/different_file.py": "def bar():\n    return 'hello'\n",
    }

    # Files with similar content should have high duplication
    ratio = duplication_ratio_token_similarity(
        evidence_files, file_cache, threshold=0.5, max_pairwise=100
    )

    assert 0.0 <= ratio <= 1.0
    assert ratio > 0.0  # Should detect some similarity


def test_duplication_ratio_token_similarity_empty():
    """Test token similarity with empty/single file."""
    from scripts.space_traversal.dup_similarity import duplication_ratio_token_similarity

    # Empty list
    ratio = duplication_ratio_token_similarity([], {})
    assert ratio == 0.0

    # Single file
    ratio = duplication_ratio_token_similarity(["single.py"], {"single.py": "content"})
    assert ratio == 0.0


def test_duplication_ratio_token_similarity_max_pairwise():
    """Test that max_pairwise caps comparisons."""
    from scripts.space_traversal.dup_similarity import duplication_ratio_token_similarity

    # Create many files
    n = 20
    evidence_files = [f"file_{i}.py" for i in range(n)]
    file_cache = {f: f"content {i}" for i, f in enumerate(evidence_files)}

    # With max_pairwise=10, should only compare 10 pairs
    ratio = duplication_ratio_token_similarity(
        evidence_files, file_cache, threshold=0.7, max_pairwise=10
    )

    assert 0.0 <= ratio <= 1.0


def test_duplication_ratio_token_similarity_determinism():
    """Test that token similarity is deterministic."""
    from scripts.space_traversal.dup_similarity import duplication_ratio_token_similarity

    evidence_files = [f"file_{i}.py" for i in range(10)]
    file_cache = {f: f"content {i}" for i, f in enumerate(evidence_files)}

    # Run multiple times, should get same result
    ratio1 = duplication_ratio_token_similarity(
        evidence_files, file_cache, threshold=0.7, max_pairwise=20
    )
    ratio2 = duplication_ratio_token_similarity(
        evidence_files, file_cache, threshold=0.7, max_pairwise=20
    )

    assert ratio1 == ratio2


def test_stem_tokens():
    """Test deterministic tokenization."""
    from scripts.space_traversal.dup_similarity import _stem_tokens

    tokens = _stem_tokens("module_test_helper.py")
    assert "module" in tokens
    assert "test" in tokens
    assert "helper" in tokens
    assert all(isinstance(t, str) for t in tokens)
    assert all(t.islower() for t in tokens)


def test_jaccard_similarity():
    """Test Jaccard similarity calculation."""
    from scripts.space_traversal.dup_similarity import _jaccard

    a = {"foo", "bar", "baz"}
    b = {"foo", "bar", "qux"}

    # Intersection: {foo, bar} = 2
    # Union: {foo, bar, baz, qux} = 4
    # Jaccard = 2/4 = 0.5
    sim = _jaccard(a, b)
    assert abs(sim - 0.5) < 0.01

    # Identical sets
    sim = _jaccard(a, a)
    assert sim == 1.0

    # Disjoint sets
    c = {"x", "y", "z"}
    sim = _jaccard(a, c)
    assert sim == 0.0


def test_deterministic_sample_pairs():
    """Test deterministic pair sampling."""
    from scripts.space_traversal.dup_similarity import _deterministic_sample_pairs

    # Small n, all pairs should be returned
    pairs = _deterministic_sample_pairs(5, max_pairs=100)
    assert len(pairs) == 10  # C(5,2) = 10

    # Large n, should cap at max_pairs
    pairs = _deterministic_sample_pairs(20, max_pairs=10)
    assert len(pairs) <= 10

    # Check determinism
    pairs1 = _deterministic_sample_pairs(15, max_pairs=20)
    pairs2 = _deterministic_sample_pairs(15, max_pairs=20)
    assert pairs1 == pairs2


def test_tokenize_content():
    """Test content tokenization."""
    from scripts.space_traversal.dup_similarity import _tokenize_content

    content = "def foo():\n    return bar + 123\n"
    tokens = _tokenize_content(content, max_tokens=100)

    assert "def" in tokens
    assert "foo" in tokens
    assert "return" in tokens
    assert "bar" in tokens
    # Numbers should be tokenized
    assert "123" in tokens


def test_estimate_backward_compat():
    """Test that estimate() function still works (backward compatibility)."""
    from scripts.space_traversal.dup_similarity import estimate

    evidence_files = [
        "foo.py",
        "foo.md",
        "bar.py",
    ]

    # Provide dummy repo_root
    ratio = estimate(evidence_files, Path("/tmp"))
    assert 0.0 <= ratio <= 1.0
    assert ratio > 0.0  # Should detect duplication in "foo" stem
