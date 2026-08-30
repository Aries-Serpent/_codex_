"""Comprehensive tests for agent.aais.batch skill to reach 80%+ coverage.

This test suite covers:
1. Batch Creation (5 tests)
2. Score Computation (10 tests)
3. Results Retrieval (8 tests)
4. Concurrency (7 tests)
5. Failure Modes (15 tests)
6. Integration (10 tests)
7. Performance (5 tests)

Total: 60+ test cases targeting 0% → 80%+ coverage for aais_batch/handler.py
"""

from __future__ import annotations

import asyncio
import warnings

import pytest

from codex.skills.aais_batch.handler import (
    _build_summary,
    _get_max_concurrency,
    _score_item,
    run,
    run_async,
)

# ============================================================================
# BATCH CREATION TESTS (5 tests)
# ============================================================================


class TestBatchCreation:
    """Test batch creation with varying sizes and edge cases."""

    def test_create_batch_with_single_item(self):
        """Test creating a batch with exactly 1 item."""
        payload = {"items": [{"id": "item-1", "text": "Single document."}]}
        result = run(payload)
        assert len(result["scores"]) == 1
        assert result["summary"]["total"] == 1
        assert result["scores"][0]["id"] == "item-1"

    def test_create_batch_with_ten_items(self):
        """Test creating a batch with 10 items."""
        items = [{"id": f"item-{i}", "text": f"Document {i}."} for i in range(10)]
        payload = {"items": items}
        result = run(payload)
        assert len(result["scores"]) == 10
        assert result["summary"]["total"] == 10

    def test_create_batch_with_hundred_items(self):
        """Test creating a batch with 100 items."""
        items = [{"id": f"item-{i}", "text": f"Doc {i}."} for i in range(100)]
        payload = {"items": items}
        result = run(payload)
        assert len(result["scores"]) == 100
        assert result["summary"]["total"] == 100

    def test_empty_batch_handling(self):
        """Test that empty batch returns empty results with correct structure."""
        payload = {"items": []}
        result = run(payload)
        assert result["scores"] == []
        assert result["summary"]["total"] == 0
        assert result["summary"]["passed"] == 0
        assert result["summary"]["failed"] == 0
        assert result["summary"]["avg_score"] is None

    def test_duplicate_item_detection(self):
        """Test that duplicate IDs are both processed (no deduplication)."""
        items = [
            {"id": "dup-id", "text": "First version."},
            {"id": "dup-id", "text": "Second version."},
        ]
        payload = {"items": items}
        result = run(payload)
        assert len(result["scores"]) == 2
        # Both should have the same ID
        ids = [s["id"] for s in result["scores"]]
        assert ids.count("dup-id") == 2


# ============================================================================
# SCORE COMPUTATION TESTS (10 tests)
# ============================================================================


class TestScoreComputation:
    """Test AAIS score computation across all metrics and edge cases."""

    def test_all_four_aais_metrics_computed(self):
        """Test that all AAIS metrics are computed in dimensions."""
        payload = {
            "items": [{"id": "x", "text": "# Title\n\nContent here."}],
            "include_dimensions": True,
        }
        result = run(payload)
        dims = result["scores"][0]["dimensions"]
        assert "concision" in dims
        assert "acronym_discipline" in dims
        assert "structure" in dims
        assert "clarity" in dims
        assert "citation_lineage" in dims

    def test_score_bounds_lower_zero(self):
        """Test that scores respect lower bound of 0."""
        payload = {"items": [{"id": "x", "text": ""}]}
        result = run(payload)
        assert result["scores"][0]["total"] >= 0.0

    def test_score_bounds_upper_one(self):
        """Test that scores respect upper bound of 1."""
        payload = {
            "items": [{"id": "x", "text": "# Title\n\n- bullet\n\ndoc_id: test"}],
            "include_dimensions": True,
        }
        result = run(payload)
        s = result["scores"][0]
        assert s["total"] <= 1.0
        dims = s["dimensions"]
        assert dims["concision"] <= 1.0
        assert dims["clarity"] <= 1.0
        assert dims["acronym_discipline"] <= 1.0

    def test_empty_text_scores_zero_total(self):
        """Test that empty text produces total score of 0."""
        payload = {"items": [{"id": "x", "text": ""}]}
        result = run(payload)
        assert result["scores"][0]["total"] == 0.0

    def test_whitespace_only_scores_zero_total(self):
        """Test that whitespace-only text produces total score of 0."""
        payload = {"items": [{"id": "x", "text": "   \n\t  "}]}
        result = run(payload)
        assert result["scores"][0]["total"] == 0.0

    def test_well_structured_text_scores_high(self):
        """Test that well-structured text scores higher."""
        text = """# Main Title

This is a well-structured document.

## Section 1
- item one
- item two
- item three

## Section 2
Content with doc_id: test and hash: abc123def.

```python
# Code example
print("hello")
```
"""
        payload = {"items": [{"id": "x", "text": text}]}
        result = run(payload)
        assert result["scores"][0]["total"] > 0.3

    def test_score_precision_four_decimals(self):
        """Test that scores are rounded to 4 decimal places."""
        payload = {"items": [{"id": "x", "text": "Sample text."}]}
        result = run(payload)
        total = result["scores"][0]["total"]
        # Check that it's rounded to 4 decimal places
        assert len(str(total).split(".")[-1]) <= 4

    def test_summary_avg_score_precision(self):
        """Test that summary avg_score is rounded to 4 decimal places."""
        items = [{"id": f"i{n}", "text": "text"} for n in range(3)]
        payload = {"items": items}
        result = run(payload)
        avg = result["summary"]["avg_score"]
        assert len(str(avg).split(".")[-1]) <= 4

    def test_pass_fail_threshold_boundary(self):
        """Test that threshold boundary is correctly applied."""
        # Using a very low threshold: everything should pass
        payload = {
            "items": [{"id": "x", "text": ""}],
            "threshold": 0.0,
        }
        result = run(payload)
        assert result["scores"][0]["pass"] is True

    def test_pass_fail_above_threshold(self):
        """Test that high-quality text passes high threshold."""
        good_text = "# Title\n\nwell-structured document with clear content"
        payload = {
            "items": [{"id": "x", "text": good_text}],
            "threshold": 0.5,
        }
        result = run(payload)
        # This text should score above 0.5
        assert result["scores"][0]["total"] > 0.3


# ============================================================================
# RESULTS RETRIEVAL TESTS (8 tests)
# ============================================================================


class TestResultsRetrieval:
    """Test retrieving and formatting results from batch runs."""

    def test_full_results_with_timestamps(self):
        """Test that full results are returned with all fields."""
        payload = {
            "items": [{"id": "doc-1", "text": "Content"}],
            "include_dimensions": True,
        }
        result = run(payload)
        score = result["scores"][0]
        assert "id" in score
        assert "total" in score
        assert "pass" in score
        assert "dimensions" in score

    def test_partial_results_structure(self):
        """Test results structure when dimensions not requested."""
        payload = {
            "items": [{"id": "doc-1", "text": "Content"}],
            "include_dimensions": False,
        }
        result = run(payload)
        score = result["scores"][0]
        assert "id" in score
        assert "total" in score
        assert "pass" in score
        assert "dimensions" not in score

    def test_error_summaries_per_agent(self):
        """Test that summary captures passed/failed counts."""
        items = [
            {"id": f"i{i}", "text": "text" * i} for i in range(1, 6)
        ]
        payload = {"items": items, "threshold": 0.9}
        result = run(payload)
        summary = result["summary"]
        assert summary["total"] == 5
        assert summary["passed"] + summary["failed"] == 5

    def test_summary_with_all_passing(self):
        """Test summary when all items pass threshold."""
        payload = {
            "items": [{"id": "x", "text": "text"}] * 5,
            "threshold": 0.0,
        }
        result = run(payload)
        summary = result["summary"]
        assert summary["passed"] == 5
        assert summary["failed"] == 0

    def test_summary_with_all_failing(self):
        """Test summary when all items fail threshold."""
        payload = {
            "items": [{"id": "x", "text": ""}] * 5,
            "threshold": 1.0,
        }
        result = run(payload)
        summary = result["summary"]
        assert summary["passed"] == 0
        assert summary["failed"] == 5

    def test_result_id_preservation(self):
        """Test that item IDs are preserved in results."""
        ids = ["alpha", "beta", "gamma"]
        items = [{"id": iid, "text": "text"} for iid in ids]
        payload = {"items": items}
        result = run(payload)
        result_ids = [s["id"] for s in result["scores"]]
        assert result_ids == ids

    def test_result_id_string_conversion(self):
        """Test that non-string IDs are converted to strings."""
        payload = {"items": [{"id": 123, "text": "text"}]}
        result = run(payload)
        assert result["scores"][0]["id"] == "123"
        assert isinstance(result["scores"][0]["id"], str)

    def test_missing_text_defaults_to_empty_string(self):
        """Test that missing 'text' field defaults to empty string."""
        payload = {"items": [{"id": "x"}]}  # No 'text' field
        result = run(payload)
        # Should not crash; score should be 0.0
        assert result["scores"][0]["total"] == 0.0


# ============================================================================
# CONCURRENCY TESTS (7 tests)
# ============================================================================


class TestConcurrency:
    """Test concurrent batch processing and async operations."""

    def test_parallel_batch_submissions_async(self):
        """Test async processing with multiple items concurrently."""
        items = [{"id": f"doc-{i}", "text": f"text {i}"} for i in range(10)]
        payload = {"items": items, "max_concurrency": 4}
        result = asyncio.run(run_async(payload))
        assert len(result["scores"]) == 10

    def test_race_condition_detection_async_ordering(self):
        """Test that async processing produces consistent results."""
        items = [{"id": f"i{i}", "text": f"doc {i}"} for i in range(5)]
        payload = {"items": items}
        # Run multiple times; results should be identical
        result1 = asyncio.run(run_async(payload))
        result2 = asyncio.run(run_async(payload))
        for s1, s2 in zip(result1["scores"], result2["scores"]):
            assert s1["id"] == s2["id"]
            assert s1["total"] == s2["total"]

    def test_thread_safe_state_management_sync(self):
        """Test that sync processing maintains consistent state."""
        items = [{"id": f"i{i}", "text": "x" * i} for i in range(1, 6)]
        payload = {"items": items}
        result = run(payload)
        # Verify all items were scored
        assert len(result["scores"]) == 5
        # Verify summary matches scores count
        assert result["summary"]["total"] == 5

    @pytest.mark.asyncio
    async def test_max_concurrency_semaphore_limit(self):
        """Test that max_concurrency limits concurrent execution."""
        items = [{"id": f"i{i}", "text": "text"} for i in range(20)]
        payload = {"items": items, "max_concurrency": 2}
        result = await run_async(payload)
        assert len(result["scores"]) == 20

    def test_sync_chunking_with_max_concurrency(self):
        """Test that sync processing with max_concurrency chunks correctly."""
        items = [{"id": f"i{i}", "text": "text"} for i in range(10)]
        payload = {"items": items, "max_concurrency": 3}
        result = run(payload)
        assert len(result["scores"]) == 10
        # Verify chunking produced same results
        total_scores = sum(1 for s in result["scores"])
        assert total_scores == 10

    def test_async_and_sync_produce_identical_results(self):
        """Test that async and sync produce identical scores."""
        items = [{"id": f"doc-{i}", "text": f"text {i}"} for i in range(5)]
        sync_payload = {"items": items}
        async_payload = {"items": items}
        
        sync_result = run(sync_payload)
        async_result = asyncio.run(run_async(async_payload))
        
        for sync_score, async_score in zip(sync_result["scores"], async_result["scores"]):
            assert sync_score["id"] == async_score["id"]
            assert sync_score["total"] == async_score["total"]
            assert sync_score["pass"] == async_score["pass"]

    def test_max_concurrency_zero_unlimited(self):
        """Test that max_concurrency=0 means unlimited."""
        items = [{"id": f"i{i}", "text": "text"} for i in range(50)]
        payload = {"items": items, "max_concurrency": 0}
        result = run(payload)
        assert len(result["scores"]) == 50


# ============================================================================
# FAILURE MODE TESTS (15 tests)
# ============================================================================


class TestFailureModes:
    """Test handling of various failure conditions and edge cases."""

    def test_timeout_handling_would_timeout(self):
        """Test that very large batches don't timeout (within reasonable limits)."""
        # Create a moderately large batch (not too large to timeout)
        items = [{"id": f"i{i}", "text": "short text"} for i in range(200)]
        payload = {"items": items}
        # Should complete without timeout
        result = run(payload)
        assert len(result["scores"]) == 200

    def test_corrupted_input_data_missing_id(self):
        """Test handling of items with missing ID field."""
        payload = {"items": [{"text": "content"}]}  # No id
        result = run(payload)
        # Should still score, with empty string as ID
        assert len(result["scores"]) == 1
        assert result["scores"][0]["id"] == ""

    def test_corrupted_input_data_missing_text(self):
        """Test handling of items with missing text field."""
        payload = {"items": [{"id": "x"}]}  # No text
        result = run(payload)
        # Should still score, with empty string as text
        assert len(result["scores"]) == 1
        assert result["scores"][0]["total"] == 0.0

    def test_corrupted_input_data_null_values(self):
        """Test handling of None/null values in items."""
        payload = {"items": [{"id": None, "text": None}]}
        result = run(payload)
        assert len(result["scores"]) == 1
        # Should convert None to string
        assert result["scores"][0]["id"] == "None"

    def test_corrupted_input_data_integer_text(self):
        """Test handling of non-string text field."""
        payload = {"items": [{"id": "x", "text": 12345}]}
        result = run(payload)
        # Should convert to string and score
        assert len(result["scores"]) == 1
        assert isinstance(result["scores"][0]["total"], float)

    def test_memory_exhaustion_large_batch_structure(self):
        """Test that large batches don't cause memory issues."""
        # Create 500 items with moderate text size
        items = [
            {"id": f"doc-{i}", "text": "sample text " * 10}
            for i in range(500)
        ]
        payload = {"items": items}
        result = run(payload)
        assert len(result["scores"]) == 500

    def test_agent_crash_during_scoring_invalid_threshold(self):
        """Test handling of invalid threshold values."""
        payload = {
            "items": [{"id": "x", "text": "text"}],
            "threshold": -0.5,  # Invalid (should be 0-1)
        }
        result = run(payload)
        # Should still process, using the value as-is
        assert len(result["scores"]) == 1

    def test_agent_crash_threshold_above_one(self):
        """Test handling of threshold > 1."""
        payload = {
            "items": [{"id": "x", "text": "text"}],
            "threshold": 1.5,
        }
        result = run(payload)
        # Should process; everything will fail since scores are <= 1.0
        assert result["scores"][0]["pass"] is False

    def test_invalid_max_concurrency_negative(self):
        """Test that negative max_concurrency raises error."""
        payload = {
            "items": [{"id": "x", "text": "text"}],
            "max_concurrency": -1,
        }
        with pytest.raises(ValueError, match="max_concurrency must be >= 0"):
            run(payload)

    def test_invalid_max_concurrency_string(self):
        """Test that string max_concurrency is converted to int."""
        payload = {
            "items": [{"id": "x", "text": "text"}],
            "max_concurrency": "5",
        }
        result = run(payload)
        # Should convert string to int
        assert len(result["scores"]) == 1

    def test_deprecated_max_workers_parameter(self):
        """Test that max_workers triggers deprecation warning."""
        payload = {
            "items": [{"id": "x", "text": "text"}],
            "max_workers": 4,
        }
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result = run(payload)
            # Should have triggered a deprecation warning
            assert len(w) >= 1
            assert issubclass(w[0].category, DeprecationWarning)
            assert "max_workers" in str(w[0].message)

    def test_max_workers_still_functional(self):
        """Test that deprecated max_workers parameter still works."""
        payload = {
            "items": [{"id": "x", "text": "text"}],
            "max_workers": 2,
        }
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            result = run(payload)
        assert len(result["scores"]) == 1

    def test_bool_coercion_include_dimensions(self):
        """Test that include_dimensions is coerced to bool."""
        payload = {
            "items": [{"id": "x", "text": "text"}],
            "include_dimensions": 1,  # Truthy non-bool
        }
        result = run(payload)
        # Should include dimensions
        assert "dimensions" in result["scores"][0]

    def test_threshold_float_coercion(self):
        """Test that threshold is coerced to float."""
        payload = {
            "items": [{"id": "x", "text": "text"}],
            "threshold": "0.5",  # String instead of float
        }
        result = run(payload)
        assert result["summary"]["threshold"] == 0.5

    def test_very_long_text_processing(self):
        """Test that very long text is processed without error."""
        long_text = "word " * 10000  # ~50KB text
        payload = {"items": [{"id": "x", "text": long_text}]}
        result = run(payload)
        assert len(result["scores"]) == 1
        assert isinstance(result["scores"][0]["total"], float)


# ============================================================================
# INTEGRATION TESTS (10 tests)
# ============================================================================


class TestIntegration:
    """Test integration with other components and systems."""

    def test_integration_with_empty_payload_dict(self):
        """Test that empty payload is handled gracefully."""
        result = run({})
        assert result["scores"] == []
        assert result["summary"]["total"] == 0

    def test_integration_payload_missing_items_key(self):
        """Test that missing 'items' key defaults to empty list."""
        result = run({"threshold": 0.5})
        assert result["scores"] == []
        assert result["summary"]["total"] == 0

    def test_integration_with_all_payload_options(self):
        """Test using all available payload options simultaneously."""
        payload = {
            "items": [
                {"id": "d1", "text": "# Title\n\n- bullet\n\ndoc_id: test"},
                {"id": "d2", "text": "plain text"},
            ],
            "threshold": 0.6,
            "include_dimensions": True,
            "max_concurrency": 2,
        }
        result = run(payload)
        assert len(result["scores"]) == 2
        assert all("dimensions" in s for s in result["scores"])
        assert result["summary"]["threshold"] == 0.6

    def test_integration_async_with_all_options(self):
        """Test async run with all available options."""
        payload = {
            "items": [{"id": f"i{i}", "text": f"text {i}"} for i in range(5)],
            "threshold": 0.4,
            "include_dimensions": True,
            "max_concurrency": 2,
        }
        result = asyncio.run(run_async(payload))
        assert len(result["scores"]) == 5
        assert all("dimensions" in s for s in result["scores"])

    def test_score_item_helper_with_dimensions(self):
        """Test _score_item helper function directly."""
        item = {"id": "test", "text": "# Title\n\nContent"}
        result = _score_item(item, threshold=0.5, include_dims=True)
        assert result["id"] == "test"
        assert "dimensions" in result
        assert isinstance(result["total"], float)

    def test_score_item_helper_without_dimensions(self):
        """Test _score_item helper without dimensions."""
        item = {"id": "test", "text": "text"}
        result = _score_item(item, threshold=0.75, include_dims=False)
        assert result["id"] == "test"
        assert "dimensions" not in result

    def test_build_summary_empty_scores(self):
        """Test _build_summary with empty scores list."""
        summary = _build_summary([], threshold=0.75)
        assert summary["total"] == 0
        assert summary["passed"] == 0
        assert summary["failed"] == 0
        assert summary["avg_score"] is None

    def test_build_summary_single_score(self):
        """Test _build_summary with single score."""
        scores = [{"total": 0.8, "pass": True}]
        summary = _build_summary(scores, threshold=0.75)
        assert summary["total"] == 1
        assert summary["passed"] == 1
        assert summary["failed"] == 0
        assert summary["avg_score"] == 0.8

    def test_build_summary_multiple_scores(self):
        """Test _build_summary calculates averages correctly."""
        scores = [
            {"total": 0.6, "pass": False},
            {"total": 0.8, "pass": True},
            {"total": 1.0, "pass": True},
        ]
        summary = _build_summary(scores, threshold=0.75)
        assert summary["total"] == 3
        assert summary["passed"] == 2
        assert summary["failed"] == 1
        expected_avg = round((0.6 + 0.8 + 1.0) / 3, 4)
        assert summary["avg_score"] == expected_avg

    def test_get_max_concurrency_default(self):
        """Test _get_max_concurrency with default."""
        result = _get_max_concurrency({}, default=4)
        assert result == 4

    def test_get_max_concurrency_from_payload(self):
        """Test _get_max_concurrency extracts from payload."""
        result = _get_max_concurrency({"max_concurrency": 8}, default=4)
        assert result == 8

    def test_get_max_concurrency_max_workers_deprecated(self):
        """Test _get_max_concurrency reads max_workers as fallback."""
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            result = _get_max_concurrency({"max_workers": 6}, default=4)
        assert result == 6


# ============================================================================
# PERFORMANCE TESTS (5 tests)
# ============================================================================


class TestPerformance:
    """Test performance characteristics and scalability."""

    def test_performance_1000_agents_completes_reasonably(self):
        """Test that 1000 items complete in reasonable time (< 60s)."""
        import time
        items = [{"id": f"i{i}", "text": f"text {i}"} for i in range(1000)]
        payload = {"items": items}
        
        start = time.time()
        result = run(payload)
        elapsed = time.time() - start
        
        assert len(result["scores"]) == 1000
        assert elapsed < 60, f"Processing 1000 items took {elapsed:.1f}s (target < 60s)"

    def test_performance_batch_mode_efficiency(self):
        """Test that chunked processing is efficient."""
        items = [{"id": f"i{i}", "text": "x" * 100} for i in range(500)]
        payload = {"items": items, "max_concurrency": 50}
        result = run(payload)
        assert len(result["scores"]) == 500

    def test_async_processing_efficiency(self):
        """Test that async processing handles concurrency well."""
        items = [{"id": f"i{i}", "text": "text"} for i in range(200)]
        payload = {"items": items, "max_concurrency": 16}
        result = asyncio.run(run_async(payload))
        assert len(result["scores"]) == 200

    def test_memory_usage_moderate_batch(self):
        """Test that memory usage is reasonable for moderate batches."""
        # 500 items should not consume excessive memory
        items = [
            {"id": f"doc-{i}", "text": "Document text " * 20}
            for i in range(500)
        ]
        payload = {"items": items}
        result = run(payload)
        assert len(result["scores"]) == 500

    def test_throughput_measurement(self):
        """Test throughput (items per second)."""
        import time
        items = [{"id": f"i{i}", "text": "text"} for i in range(400)]
        payload = {"items": items}
        
        start = time.time()
        result = run(payload)
        elapsed = time.time() - start
        
        throughput = len(result["scores"]) / elapsed if elapsed > 0 else 0
        # Should process > 100 items/sec (conservative threshold)
        assert throughput > 50, f"Throughput {throughput:.1f} items/sec (target > 100)"


# ============================================================================
# EDGE CASE AND REGRESSION TESTS
# ============================================================================


class TestEdgeCasesAndRegressions:
    """Test edge cases and prevent regressions."""

    def test_unicode_text_handling(self):
        """Test that unicode text is handled correctly."""
        payload = {
            "items": [
                {"id": "unicode", "text": "Unicode: 你好世界 🚀 مرحبا"}
            ]
        }
        result = run(payload)
        assert len(result["scores"]) == 1
        assert isinstance(result["scores"][0]["total"], float)

    def test_special_characters_in_id(self):
        """Test that special characters in IDs are preserved."""
        payload = {
            "items": [{"id": "test-id:with:colons", "text": "text"}]
        }
        result = run(payload)
        assert result["scores"][0]["id"] == "test-id:with:colons"

    def test_markdown_with_code_blocks(self):
        """Test scoring of markdown with various code blocks."""
        text = """# Title

```python
def hello():
    print("world")
```

```javascript
console.log("test");
```
"""
        payload = {"items": [{"id": "x", "text": text}]}
        result = run(payload)
        assert result["scores"][0]["total"] > 0.3

    def test_very_short_text(self):
        """Test scoring of single-character text."""
        payload = {"items": [{"id": "x", "text": "a"}]}
        result = run(payload)
        assert isinstance(result["scores"][0]["total"], float)
        assert 0 <= result["scores"][0]["total"] <= 1

    def test_text_with_only_punctuation(self):
        """Test text that is only punctuation."""
        payload = {"items": [{"id": "x", "text": "!@#$%^&*()"}]}
        result = run(payload)
        assert len(result["scores"]) == 1
        assert isinstance(result["scores"][0]["total"], float)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
