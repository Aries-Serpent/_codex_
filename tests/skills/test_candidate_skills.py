"""Tests for the three candidate skills: test.failure.matcher, ci.health.analyzer, agent.aais.batch."""

from __future__ import annotations

import pytest

from codex.skills.aais_batch.handler import run as aais_batch_run
from codex.skills.ci_health_analyzer.handler import run as ci_health_run
from codex.skills.test_failure_matcher.handler import run as tfm_run


# ---------------------------------------------------------------------------
# test.failure.matcher
# ---------------------------------------------------------------------------


class TestTestFailureMatcher:
    def test_empty_input_returns_empty(self):
        result = tfm_run({"test_output": ""})
        assert result["failures"] == []
        assert result["summary"]["total"] == 0

    def test_classifies_module_not_found(self):
        log = "ModuleNotFoundError: No module named 'src.codex.something'"
        result = tfm_run({"test_output": log})
        assert result["summary"]["total"] >= 1
        ids = [f["pattern_id"] for f in result["failures"]]
        assert "RP-019" in ids

    def test_classifies_ruff_error(self):
        log = "src/codex/skills/cli.py:10:5: F401 'os' imported but unused"
        result = tfm_run({"test_output": log})
        ids = [f["pattern_id"] for f in result["failures"]]
        assert "RP-RUFF" in ids

    def test_classifies_transient(self):
        log = "runner has received a shutdown signal"
        result = tfm_run({"test_output": log})
        ids = [f["pattern_id"] for f in result["failures"]]
        assert "RP-TRANSIENT" in ids

    def test_classifies_assertion_error(self):
        log = "AssertionError: expected 1 got 2"
        result = tfm_run({"test_output": log})
        ids = [f["pattern_id"] for f in result["failures"]]
        assert "RP-ASSERT" in ids

    def test_unclassified_failed_line(self):
        log = "FAILED tests/foo/test_bar.py::TestFoo::test_something - some reason"
        result = tfm_run({"test_output": log})
        # Should capture as unclassified
        assert result["summary"]["total"] >= 1

    def test_max_failures_cap(self):
        # Generate 20 ruff errors
        lines = "\n".join(
            f"src/codex/x.py:{i}:1: F401 unused import" for i in range(1, 21)
        )
        result = tfm_run({"test_output": lines, "max_failures": 5})
        assert len(result["failures"]) <= 5

    def test_summary_categories(self):
        log = (
            "ModuleNotFoundError: No module named 'foo'\n"
            "AssertionError: wrong value\n"
        )
        result = tfm_run({"test_output": log})
        assert "categories" in result["summary"]
        assert isinstance(result["summary"]["categories"], dict)


# ---------------------------------------------------------------------------
# ci.health.analyzer
# ---------------------------------------------------------------------------


class TestCIHealthAnalyzer:
    def test_empty_logs_returns_unknown(self):
        result = ci_health_run({"run_logs": ""})
        assert result["category"] == "unknown"
        assert result["confidence"] == 0.0

    def test_classifies_transient_shutdown(self):
        logs = "runner has received a shutdown signal during job execution"
        result = ci_health_run({"run_logs": logs})
        assert result["category"] == "transient-infra"
        assert result["confidence"] >= 0.9

    def test_classifies_api503(self):
        logs = "An error occurred while processing your request. Please try again later"
        result = ci_health_run({"run_logs": logs})
        assert result["category"] == "transient-infra"

    def test_classifies_changelog_gate(self):
        logs = "CHANGELOG.md not updated in last commit - failing pre-flight"
        result = ci_health_run({"run_logs": logs})
        assert result["category"] == "pre-flight-gate"
        assert "CHANGELOG" in result["fix_commands"][0]

    def test_classifies_p23(self):
        logs = "TypeError: No such VerifiedJwtBearerDetector"
        result = ci_health_run({"run_logs": logs})
        assert result["pattern_id"] == "RP-P23"
        assert result["category"] == "supply-chain"

    def test_includes_workflow_and_sha(self):
        result = ci_health_run(
            {
                "run_logs": "some generic failure",
                "workflow_name": "My Workflow",
                "commit_sha": "abc123",
            }
        )
        assert result["workflow_name"] == "My Workflow"
        assert result["commit_sha"] == "abc123"

    def test_all_matches_list(self):
        # Both actionlint and ruff patterns
        logs = (
            "actionlint .github/workflows/ci.yml:10: syntax error\n"
            "src/x.py:5:1: F401 unused"
        )
        result = ci_health_run({"run_logs": logs})
        assert len(result["all_matches"]) >= 1

    def test_fix_commands_not_empty(self):
        logs = "CHANGELOG.md not updated"
        result = ci_health_run({"run_logs": logs})
        assert len(result["fix_commands"]) >= 1


# ---------------------------------------------------------------------------
# agent.aais.batch
# ---------------------------------------------------------------------------


class TestAAISBatch:
    def test_empty_items(self):
        result = aais_batch_run({"items": []})
        assert result["scores"] == []
        assert result["summary"]["total"] == 0
        assert result["summary"]["avg_score"] is None

    def test_single_item(self):
        result = aais_batch_run({"items": [{"id": "doc-1", "text": "Short text."}]})
        assert len(result["scores"]) == 1
        s = result["scores"][0]
        assert s["id"] == "doc-1"
        assert 0.0 <= s["total"] <= 1.0
        assert isinstance(s["pass"], bool)

    def test_multiple_items(self):
        items = [{"id": f"doc-{i}", "text": f"Document {i} content."} for i in range(5)]
        result = aais_batch_run({"items": items})
        assert len(result["scores"]) == 5
        assert result["summary"]["total"] == 5
        assert result["summary"]["passed"] + result["summary"]["failed"] == 5

    def test_custom_threshold(self):
        # Threshold 0.0 → everything passes
        items = [{"id": "x", "text": "a"}]
        result = aais_batch_run({"items": items, "threshold": 0.0})
        assert result["scores"][0]["pass"] is True
        assert result["summary"]["threshold"] == 0.0

    def test_include_dimensions(self):
        items = [{"id": "d", "text": "well structured document with clear headings"}]
        result = aais_batch_run({"items": items, "include_dimensions": True})
        dims = result["scores"][0].get("dimensions", {})
        assert "concision" in dims
        assert "clarity" in dims
        assert "structure" in dims

    def test_no_dimensions_by_default(self):
        items = [{"id": "x", "text": "text"}]
        result = aais_batch_run({"items": items})
        assert "dimensions" not in result["scores"][0]

    def test_summary_avg_score(self):
        items = [{"id": f"i{n}", "text": "text"} for n in range(3)]
        result = aais_batch_run({"items": items})
        avg = result["summary"]["avg_score"]
        assert avg is not None
        assert 0.0 <= avg <= 1.0
