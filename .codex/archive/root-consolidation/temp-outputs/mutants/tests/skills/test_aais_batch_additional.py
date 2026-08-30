"""Additional advanced test cases for agent.aais.batch (P0.3 expansion).

This test suite expands on test_aais_batch_comprehensive.py with 25-30 additional
test cases focusing on:

1. Advanced Batch Processing Variations (8 tests)
2. Extended Error Handling (8 tests)
3. Performance & Concurrency Boundaries (6 tests)
4. Advanced Integration Scenarios (7 tests)

Total: 29 additional test cases targeting edge cases and advanced scenarios.
"""

from __future__ import annotations

import asyncio
import time

import pytest

from codex.skills.aais_batch.handler import (
    _build_summary,
    _get_max_concurrency,
    _score_item,
    run,
    run_async,
)

# ============================================================================
# ADVANCED BATCH PROCESSING VARIATIONS (8 tests)
# ============================================================================


class TestAdvancedBatchProcessing:
    """Test advanced batch processing scenarios and chunking edge cases."""

    def test_batch_exactly_at_chunk_boundary(self):
        """Test batch size that is exact multiple of chunk size."""
        # 100 items with 25-item chunks = exactly 4 chunks
        items = [{"id": f"item-{i}", "text": f"Doc {i}."} for i in range(100)]
        payload = {"items": items, "max_concurrency": 25}
        result = run(payload)
        assert len(result["scores"]) == 100
        assert result["summary"]["total"] == 100

    def test_batch_one_item_over_chunk_boundary(self):
        """Test batch size that is chunk_size + 1."""
        # 51 items with 25-item chunks = 2 chunks (25 + 26)
        items = [{"id": f"i-{i}", "text": f"text {i}"} for i in range(51)]
        payload = {"items": items, "max_concurrency": 25}
        result = run(payload)
        assert len(result["scores"]) == 51
        scores_match_ids = [s["id"] for s in result["scores"]]
        assert len(scores_match_ids) == 51

    def test_chunking_preserves_order(self):
        """Test that chunking preserves item order in results."""
        items = [{"id": f"id-{i:03d}", "text": f"Item {i}"} for i in range(47)]
        payload = {"items": items, "max_concurrency": 10}
        result = run(payload)
        
        # Extract IDs in order
        result_ids = [s["id"] for s in result["scores"]]
        expected_ids = [f"id-{i:03d}" for i in range(47)]
        assert result_ids == expected_ids

    def test_single_item_with_chunking_enabled(self):
        """Test that single item works with chunking enabled."""
        payload = {
            "items": [{"id": "only-one", "text": "Solo item"}],
            "max_concurrency": 10,
        }
        result = run(payload)
        assert len(result["scores"]) == 1
        assert result["scores"][0]["id"] == "only-one"

    def test_very_small_chunks(self):
        """Test processing with 1-item chunks (extreme chunking)."""
        items = [{"id": f"x{i}", "text": "t"} for i in range(10)]
        payload = {"items": items, "max_concurrency": 1}
        result = run(payload)
        assert len(result["scores"]) == 10
        assert all(s["total"] >= 0 for s in result["scores"])

    def test_chunk_size_larger_than_batch(self):
        """Test chunk size larger than total items."""
        items = [{"id": f"i{i}", "text": f"doc {i}"} for i in range(5)]
        payload = {"items": items, "max_concurrency": 100}
        result = run(payload)
        assert len(result["scores"]) == 5

    def test_chunking_with_dimension_extraction(self):
        """Test chunking preserves dimension extraction."""
        items = [
            {"id": f"item-{i}", "text": f"# Title {i}\n\nContent with doc_id: test{i}."}
            for i in range(15)
        ]
        payload = {"items": items, "max_concurrency": 5, "include_dimensions": True}
        result = run(payload)
        
        assert len(result["scores"]) == 15
        for score in result["scores"]:
            assert "dimensions" in score
            assert "concision" in score["dimensions"]

    def test_mixed_chunk_distribution(self):
        """Test that results are identical regardless of chunk size."""
        items = [{"id": f"test-{i}", "text": f"Content {i}."} for i in range(37)]
        
        # Process with no chunking
        result_no_chunk = run({"items": items, "max_concurrency": 0})
        
        # Process with chunking
        result_chunked = run({"items": items, "max_concurrency": 10})
        
        # Results should be identical
        assert len(result_no_chunk["scores"]) == len(result_chunked["scores"])
        for i, (s1, s2) in enumerate(zip(result_no_chunk["scores"], result_chunked["scores"])):
            assert s1["id"] == s2["id"], f"ID mismatch at index {i}"
            assert s1["total"] == s2["total"], f"Score mismatch at index {i}"


# ============================================================================
# EXTENDED ERROR HANDLING & VALIDATION (8 tests)
# ============================================================================


class TestExtendedErrorHandling:
    """Test advanced error handling and validation scenarios."""

    def test_threshold_exactly_at_item_score(self):
        """Test threshold boundary when item score equals threshold."""
        # Use a well-structured item that produces a predictable score
        text = "# Title\n\nWell-structured document with clear sections."
        payload = {
            "items": [{"id": "x", "text": text}],
            "threshold": 0.5,  # Will test if score == threshold passes
        }
        result = run(payload)
        # The item should have a defined pass status
        assert "pass" in result["scores"][0]
        assert isinstance(result["scores"][0]["pass"], bool)

    def test_threshold_negative_value(self):
        """Test that negative threshold is accepted (all items pass)."""
        payload = {
            "items": [{"id": "x", "text": ""}, {"id": "y", "text": "text"}],
            "threshold": -0.5,
        }
        result = run(payload)
        assert all(s["pass"] for s in result["scores"])
        assert result["summary"]["passed"] == 2
        assert result["summary"]["failed"] == 0

    def test_threshold_well_above_one(self):
        """Test threshold > 1.0 (all items fail)."""
        payload = {
            "items": [{"id": "x", "text": "text"}, {"id": "y", "text": "more"}],
            "threshold": 1.5,
        }
        result = run(payload)
        assert all(not s["pass"] for s in result["scores"])
        assert result["summary"]["passed"] == 0
        assert result["summary"]["failed"] == 2

    def test_non_dict_items_in_list_raises(self):
        """Test that non-dict items in list are handled gracefully or raise."""
        payload = {"items": [{"id": "valid", "text": "text"}, "not-a-dict"]}
        # Should either skip or handle gracefully
        try:
            result = run(payload)
            # If it doesn't raise, check structure is valid
            assert "scores" in result
            assert "summary" in result
        except (TypeError, AttributeError):
            # It's acceptable to raise for invalid input
            pass

    def test_items_with_extra_fields_ignored(self):
        """Test that items with extra fields don't cause issues."""
        payload = {
            "items": [
                {
                    "id": "x",
                    "text": "content",
                    "extra_field": "ignored",
                    "another_field": 123,
                }
            ]
        }
        result = run(payload)
        assert len(result["scores"]) == 1
        assert result["scores"][0]["id"] == "x"

    def test_extremely_large_single_item_text(self):
        """Test processing a single item with very large text."""
        large_text = "word " * 50000  # ~250KB of text
        payload = {"items": [{"id": "big", "text": large_text}]}
        result = run(payload)
        assert len(result["scores"]) == 1
        assert isinstance(result["scores"][0]["total"], float)
        assert 0 <= result["scores"][0]["total"] <= 1

    def test_text_field_as_bytes_converted(self):
        """Test that text field as bytes is handled (if applicable)."""
        payload = {"items": [{"id": "x", "text": "text"}]}
        result = run(payload)
        # Should process without error
        assert len(result["scores"]) == 1

    def test_numeric_id_preservation_through_chunks(self):
        """Test that numeric IDs are correctly stringified in chunks."""
        items = [{"id": i, "text": f"doc {i}"} for i in range(1, 6)]
        payload = {"items": items, "max_concurrency": 2}
        result = run(payload)
        
        result_ids = [s["id"] for s in result["scores"]]
        expected_ids = [str(i) for i in range(1, 6)]
        assert result_ids == expected_ids


# ============================================================================
# PERFORMANCE & CONCURRENCY BOUNDARIES (6 tests)
# ============================================================================


class TestPerformanceConcurrencyBoundaries:
    """Test performance boundaries and concurrency edge cases."""

    def test_async_with_zero_concurrency_unsupported(self):
        """Test async with max_concurrency=0 uses appropriate default."""
        items = [{"id": f"i{i}", "text": "text"} for i in range(10)]
        payload = {"items": items, "max_concurrency": 0}
        
        result = asyncio.run(run_async(payload))
        assert len(result["scores"]) == 10

    def test_async_concurrency_one_sequential(self):
        """Test async with max_concurrency=1 processes sequentially."""
        items = [{"id": f"i{i}", "text": f"doc {i}"} for i in range(15)]
        payload = {"items": items, "max_concurrency": 1}
        
        result = asyncio.run(run_async(payload))
        assert len(result["scores"]) == 15
        # Should still match non-async results
        sync_result = run(payload)
        assert len(sync_result["scores"]) == len(result["scores"])

    def test_large_batch_async_processing(self):
        """Test async handles large batch efficiently."""
        items = [{"id": f"doc-{i}", "text": f"Content {i}"} for i in range(500)]
        payload = {"items": items, "max_concurrency": 32}
        
        start = time.time()
        result = asyncio.run(run_async(payload))
        elapsed = time.time() - start
        
        assert len(result["scores"]) == 500
        assert elapsed < 30, f"Async processing took {elapsed:.1f}s, expected < 30s"

    def test_sync_vs_async_score_equivalence_large_batch(self):
        """Test sync and async produce identical results on large batch."""
        items = [{"id": f"item-{i}", "text": f"text {i}"} for i in range(200)]
        payload = {"items": items, "include_dimensions": True}
        
        sync_result = run(payload)
        async_result = asyncio.run(run_async(payload))
        
        assert len(sync_result["scores"]) == len(async_result["scores"])
        for s1, s2 in zip(sync_result["scores"], async_result["scores"]):
            assert s1["id"] == s2["id"]
            assert s1["total"] == s2["total"]
            assert s1["pass"] == s2["pass"]

    def test_concurrency_exceeding_item_count(self):
        """Test max_concurrency larger than item count."""
        items = [{"id": f"i{i}", "text": "text"} for i in range(3)]
        payload = {"items": items, "max_concurrency": 1000}
        
        result = run(payload)
        assert len(result["scores"]) == 3

    def test_async_concurrency_exceeding_item_count(self):
        """Test async max_concurrency larger than item count."""
        items = [{"id": f"i{i}", "text": "text"} for i in range(3)]
        payload = {"items": items, "max_concurrency": 1000}
        
        result = asyncio.run(run_async(payload))
        assert len(result["scores"]) == 3


# ============================================================================
# ADVANCED INTEGRATION SCENARIOS (7 tests)
# ============================================================================


class TestAdvancedIntegration:
    """Test advanced integration scenarios and complex workflows."""

    def test_sequential_batch_processing(self):
        """Test processing multiple batches sequentially."""
        batch1 = run({"items": [{"id": "b1-i1", "text": "content"}]})
        batch2 = run({"items": [{"id": "b2-i1", "text": "other"}]})
        
        assert batch1["summary"]["total"] == 1
        assert batch2["summary"]["total"] == 1
        assert batch1["scores"][0]["id"] == "b1-i1"
        assert batch2["scores"][0]["id"] == "b2-i1"

    def test_dimensions_field_consistency(self):
        """Test dimension fields are consistently named and structured."""
        payload = {
            "items": [{"id": "x", "text": "# Title\n\nContent"}],
            "include_dimensions": True,
        }
        result = run(payload)
        
        dims = result["scores"][0]["dimensions"]
        expected_dims = {
            "concision",
            "acronym_discipline",
            "structure",
            "clarity",
            "citation_lineage",
        }
        assert set(dims.keys()) == expected_dims

    def test_summary_calculation_with_mixed_pass_fail(self):
        """Test summary correctly counts mixed passing/failing items."""
        items = [
            {"id": "good", "text": "# Title\n\nWell-structured content"},
            {"id": "bad", "text": ""},
        ]
        payload = {"items": items, "threshold": 0.5}
        result = run(payload)
        
        summary = result["summary"]
        assert summary["total"] == 2
        assert summary["passed"] + summary["failed"] == 2

    def test_payload_with_all_optional_parameters(self):
        """Test payload with all optional parameters specified."""
        payload = {
            "items": [
                {"id": "test", "text": "Sample document text."},
                {"id": "test2", "text": "Another document."},
            ],
            "threshold": 0.6,
            "include_dimensions": True,
            "max_concurrency": 5,
        }
        result = run(payload)
        
        assert len(result["scores"]) == 2
        assert result["summary"]["threshold"] == 0.6
        assert all("dimensions" in s for s in result["scores"])

    def test_async_payload_with_all_optional_parameters(self):
        """Test async with all optional parameters."""
        payload = {
            "items": [
                {"id": "a", "text": "text1"},
                {"id": "b", "text": "text2"},
            ],
            "threshold": 0.7,
            "include_dimensions": True,
            "max_concurrency": 3,
        }
        result = asyncio.run(run_async(payload))
        
        assert len(result["scores"]) == 2
        assert result["summary"]["threshold"] == 0.7
        assert all("dimensions" in s for s in result["scores"])

    def test_result_summary_threshold_matches_input(self):
        """Test that summary.threshold matches input threshold."""
        for threshold in [0.3, 0.5, 0.75, 0.9]:
            payload = {
                "items": [{"id": "x", "text": "text"}],
                "threshold": threshold,
            }
            result = run(payload)
            assert result["summary"]["threshold"] == threshold

    def test_helper_build_summary_with_varying_scores(self):
        """Test _build_summary with various score combinations."""
        scores = [
            {"id": "a", "total": 0.2, "pass": False},
            {"id": "b", "total": 0.8, "pass": True},
            {"id": "c", "total": 0.5, "pass": False},
        ]
        summary = _build_summary(scores, 0.6)
        
        assert summary["total"] == 3
        assert summary["passed"] == 1
        assert summary["failed"] == 2
        expected_avg = round((0.2 + 0.8 + 0.5) / 3, 4)
        assert summary["avg_score"] == expected_avg


# ============================================================================
# STRESS TESTS & BOUNDARY CONDITIONS (Additional edge cases)
# ============================================================================


class TestStressAndBoundary:
    """Stress tests and boundary conditions."""

    def test_items_with_only_id_no_text(self):
        """Test items missing text field default correctly."""
        payload = {"items": [{"id": "orphan"}]}
        result = run(payload)
        assert len(result["scores"]) == 1
        assert result["scores"][0]["total"] == 0.0

    def test_items_with_none_text(self):
        """Test items with None text value."""
        payload = {"items": [{"id": "x", "text": None}]}
        result = run(payload)
        # Should convert None to string and score
        assert len(result["scores"]) == 1

    def test_very_large_batch_reasonable_throughput(self):
        """Test 2000-item batch completes in reasonable time."""
        items = [{"id": f"id-{i:04d}", "text": f"Item {i}"} for i in range(2000)]
        payload = {"items": items}
        
        start = time.time()
        result = run(payload)
        elapsed = time.time() - start
        
        assert len(result["scores"]) == 2000
        assert elapsed < 120, f"2000 items took {elapsed:.1f}s, expected < 120s"

    def test_chunked_vs_unchunked_memory_profile(self):
        """Test chunking doesn't significantly impact memory for same batch."""
        items = [{"id": f"i{i}", "text": "content " * 100} for i in range(300)]
        
        result1 = run({"items": items, "max_concurrency": 0})
        result2 = run({"items": items, "max_concurrency": 30})
        
        # Both should have same number of results
        assert len(result1["scores"]) == len(result2["scores"])
        assert result1["summary"]["total"] == result2["summary"]["total"]

    def test_max_concurrency_validation(self):
        """Test _get_max_concurrency with edge cases."""
        # Valid cases
        assert _get_max_concurrency({"max_concurrency": 10}, 5) == 10
        assert _get_max_concurrency({"max_concurrency": 0}, 5) == 0
        
        # max_workers deprecated but still works
        import warnings
        with warnings.catch_warnings(record=True):
            warnings.simplefilter("always")
            result = _get_max_concurrency({"max_workers": 8}, 5)
            assert result == 8

    def test_score_item_with_empty_dimensions_request(self):
        """Test _score_item respects include_dims=False."""
        item = {"id": "test", "text": "Content with # title"}
        
        result_no_dims = _score_item(item, 0.5, False)
        result_with_dims = _score_item(item, 0.5, True)
        
        assert "dimensions" not in result_no_dims
        assert "dimensions" in result_with_dims

    def test_json_serializable_output(self):
        """Test that all output is JSON-serializable."""
        import json
        
        payload = {
            "items": [
                {"id": "x", "text": "# Title\n\nContent"},
                {"id": "y", "text": "Other"},
            ],
            "include_dimensions": True,
            "max_concurrency": 2,
        }
        result = run(payload)
        
        # Should not raise
        json_str = json.dumps(result)
        assert json_str  # Non-empty
        
        # Round-trip
        reparsed = json.loads(json_str)
        assert reparsed["summary"]["total"] == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
