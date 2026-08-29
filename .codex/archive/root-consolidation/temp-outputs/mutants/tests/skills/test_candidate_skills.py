"""Tests for the three candidate skills: test.failure.matcher, ci.health.analyzer, agent.aais.batch."""

from __future__ import annotations

import asyncio

from codex.skills.aais_batch.handler import run as aais_batch_run
from codex.skills.aais_batch.handler import run_async as aais_batch_run_async
from codex.skills.ci_health_analyzer.handler import run as ci_health_run
from codex.skills.test_failure_matcher.handler import run as tfm_run

# ---------------------------------------------------------------------------
# test.failure.matcher
# ---------------------------------------------------------------------------


class TestTestFailureMatcher:
    def test_empty_input_returns_empty(self):
        result = tfm_run({"test_output": ""})
        assert result["failures"] == [], "Result must not be empty"
        assert result["summary"]["total"] == 0, "Result must not be empty"

    def test_classifies_module_not_found(self):
        log = "ModuleNotFoundError: No module named 'src.codex.something'"
        result = tfm_run({"test_output": log})
        assert result["summary"]["total"] >= 1, "Value must be greater than zero"
        ids = [f["pattern_id"] for f in result["failures"]]
        assert "RP-019" in ids, "Condition must be true"

    def test_classifies_ruff_error(self):
        log = "src/codex/skills/cli.py:10:5: F401 'os' imported but unused"
        result = tfm_run({"test_output": log})
        ids = [f["pattern_id"] for f in result["failures"]]
        assert "RP-RUFF" in ids, "Condition must be true"

    def test_classifies_transient(self):
        log = "runner has received a shutdown signal"
        result = tfm_run({"test_output": log})
        ids = [f["pattern_id"] for f in result["failures"]]
        assert "RP-TRANSIENT" in ids, "Condition must be true"

    def test_classifies_assertion_error(self):
        log = "AssertionError: expected 1 got 2"
        result = tfm_run({"test_output": log})
        ids = [f["pattern_id"] for f in result["failures"]]
        assert "RP-ASSERT" in ids, "Condition must be true"

    def test_unclassified_failed_line(self):
        log = "FAILED tests/foo/test_bar.py::TestFoo::test_something - some reason"
        result = tfm_run({"test_output": log})
        # Should capture as unclassified
        assert result["summary"]["total"] >= 1, "Value must be greater than zero"

    def test_max_failures_cap(self):
        # Generate 20 ruff errors
        lines = "\n".join(f"src/codex/x.py:{i}:1: F401 unused import" for i in range(1, 21))
        result = tfm_run({"test_output": lines, "max_failures": 5})
        assert len(result["failures"]) <= 5, "Collection must not be empty"

    def test_summary_categories(self):
        log = "ModuleNotFoundError: No module named 'foo'\n" "AssertionError: wrong value\n"
        result = tfm_run({"test_output": log})
        assert "categories" in result["summary"], "Result must not be empty"
        assert isinstance(result["summary"]["categories"], dict)


# ---------------------------------------------------------------------------
# ci.health.analyzer
# ---------------------------------------------------------------------------


class TestCIHealthAnalyzer:
    def test_empty_logs_returns_unknown(self):
        result = ci_health_run({"run_logs": ""})
        assert result["category"] == "unknown", "Result must not be empty"
        assert result["confidence"] == 0.0, "Result must not be empty"

    def test_classifies_transient_shutdown(self):
        logs = "runner has received a shutdown signal during job execution"
        result = ci_health_run({"run_logs": logs})
        assert result["category"] == "transient-infra", "Result must not be empty"
        assert result["confidence"] >= 0.9, "Value must be greater than zero"

    def test_classifies_api503(self):
        logs = "An error occurred while processing your request. Please try again later"
        result = ci_health_run({"run_logs": logs})
        assert result["category"] == "transient-infra", "Result must not be empty"

    def test_classifies_changelog_gate(self):
        logs = "CHANGELOG.md not updated in last commit - failing pre-flight"
        result = ci_health_run({"run_logs": logs})
        assert result["category"] == "pre-flight-gate", "Result must not be empty"
        assert "CHANGELOG" in result["fix_commands"][0], "Result must not be empty"

    def test_classifies_p23(self):
        logs = "TypeError: No such VerifiedJwtBearerDetector"
        result = ci_health_run({"run_logs": logs})
        assert result["pattern_id"] == "RP-P23", "Result must not be empty"
        assert result["category"] == "supply-chain", "Result must not be empty"

    def test_includes_workflow_and_sha(self):
        result = ci_health_run(
            {
                "run_logs": "some generic failure",
                "workflow_name": "My Workflow",
                "commit_sha": "abc123",
            }
        )
        assert result["workflow_name"] == "My Workflow", "Result must not be empty"
        assert result["commit_sha"] == "abc123", "Result must not be empty"

    def test_all_matches_list(self):
        # Both actionlint and ruff patterns
        logs = "actionlint .github/workflows/ci.yml:10: syntax error\n" "src/x.py:5:1: F401 unused"
        result = ci_health_run({"run_logs": logs})
        assert len(result["all_matches"]) >= 1, "Collection must not be empty"

    def test_fix_commands_not_empty(self):
        logs = "CHANGELOG.md not updated"
        result = ci_health_run({"run_logs": logs})
        assert len(result["fix_commands"]) >= 1, "Collection must not be empty"


# ---------------------------------------------------------------------------
# agent.aais.batch
# ---------------------------------------------------------------------------


class TestAAISBatch:
    def test_empty_items(self):
        result = aais_batch_run({"items": []})
        assert result["scores"] == [], "Result must not be empty"
        assert result["summary"]["total"] == 0, "Result must not be empty"
        assert result["summary"]["avg_score"] is None, "Result must not be empty"

    def test_single_item(self):
        result = aais_batch_run({"items": [{"id": "doc-1", "text": "Short text."}]})
        assert len(result["scores"]) == 1, "Collection must not be empty"
        s = result["scores"][0]
        assert s["id"] == "doc-1", "Condition must be true"
        assert 0.0 <= s["total"] <= 1.0, "0 is not valid"
        assert isinstance(s["pass"], bool)

    def test_multiple_items(self):
        items = [{"id": f"doc-{i}", "text": f"Document {i} content."} for i in range(5)]
        result = aais_batch_run({"items": items})
        assert len(result["scores"]) == 5, "Collection must not be empty"
        assert result["summary"]["total"] == 5, "Result must not be empty"
        assert result["summary"]["passed"] + result["summary"]["failed"] == 5, "Result must not be empty"

    def test_custom_threshold(self):
        # Threshold 0.0 → everything passes
        items = [{"id": "x", "text": "a"}]
        result = aais_batch_run({"items": items, "threshold": 0.0})
        assert result["scores"][0]["pass"] is True, "Result must not be empty"
        assert result["summary"]["threshold"] == 0.0, "Result must not be empty"

    def test_include_dimensions(self):
        items = [{"id": "d", "text": "well structured document with clear headings"}]
        result = aais_batch_run({"items": items, "include_dimensions": True})
        dims = result["scores"][0].get("dimensions", {})
        assert "concision" in dims, "Condition must be true"
        assert "clarity" in dims, "Condition must be true"
        assert "structure" in dims, "Condition must be true"

    def test_no_dimensions_by_default(self):
        items = [{"id": "x", "text": "text"}]
        result = aais_batch_run({"items": items})
        assert "dimensions" not in result["scores"][0], "Result must not be empty"

    def test_summary_avg_score(self):
        items = [{"id": f"i{n}", "text": "text"} for n in range(3)]
        result = aais_batch_run({"items": items})
        avg = result["summary"]["avg_score"]
        assert avg is not None, "avg must be initialized"
        assert 0.0 <= avg <= 1.0, "0 is not valid"


class TestAAISBatchAsync:
    """Tests for the async run_async() path, including max_concurrency throttle."""

    def test_empty_items_async(self):
        result = asyncio.run(aais_batch_run_async({"items": []}))
        assert result["scores"] == [], "Result must not be empty"
        assert result["summary"]["total"] == 0, "Result must not be empty"

    def test_basic_async(self):
        items = [{"id": f"doc-{i}", "text": f"Document {i}"} for i in range(4)]
        result = asyncio.run(aais_batch_run_async({"items": items}))
        assert len(result["scores"]) == 4, "Collection must not be empty"
        assert result["summary"]["total"] == 4, "Result must not be empty"

    def test_max_concurrency_throttle(self):
        """max_concurrency=1 forces sequential execution — result must still be complete."""
        items = [{"id": f"doc-{i}", "text": f"text {i}"} for i in range(6)]
        result = asyncio.run(aais_batch_run_async({"items": items, "max_concurrency": 1}))
        assert len(result["scores"]) == 6, "Collection must not be empty"
        assert result["summary"]["total"] == 6, "Result must not be empty"

    def test_max_workers_alias(self):
        """max_workers is accepted as a backwards-compat alias for max_concurrency."""
        items = [{"id": "x", "text": "text"}]
        result = asyncio.run(aais_batch_run_async({"items": items, "max_workers": 1}))
        assert len(result["scores"]) == 1, "Collection must not be empty"

    def test_async_matches_sync(self):
        """Async and sync paths must produce identical scores for the same input."""
        items = [{"id": f"i{n}", "text": f"sample text {n}"} for n in range(5)]
        sync_result = aais_batch_run({"items": items})
        async_result = asyncio.run(aais_batch_run_async({"items": items}))
        for s, a in zip(sync_result["scores"], async_result["scores"]):
            assert s["total"] == a["total"], "Condition must be true"
            assert s["pass"] == a["pass"], "Condition must be true"
