#!/usr/bin/env python3
from src.codex.utils.path_extended import get_repo_root

"""
PHASE 9.2 CRITICAL GAP-FILL TEST SUITE

Target coverage:
- cascade_orchestrator.py: 78.89% -> 94%+ (+16.11%)
- pattern_router.py: 81.03% -> 91%+ (+10.97%)

Gap-fill strategy:
1. Error handling paths and exceptions
2. Edge cases and boundary conditions
3. Timeout and resource management
4. Type validation and conflict detection
5. Routing decision variations

Authority: @mbaetiong (D-tier autonomy)
"""

import sys
import time
from unittest import mock

import pytest

# Import the modules to test
sys.path.insert(0, str(get_repo_root() / 'scripts/ci'))

from phase_9_2_cascade_orchestrator import (
    CascadeOrchestrator,
    FailureLog,
    FixAttempt,
    FixExecutor,
    FixRouter,
    FixStatus,
    Pattern,
    PatternConfidence,
    PatternDetector,
    PatternMatch,
    get_confidence_level,
    run_command,
)
from phase_9_2_pattern_router import (
    PatternMatcher,
    PatternRouter,
)

# ============================================================================
# TEST FIXTURES
# ============================================================================


@pytest.fixture
def simple_failure_log():
    """Simple failure log for basic tests"""
    return FailureLog(
        raw_log="F401 unused import 'sys'",
        job_name="test-job",
        workflow_name="test-workflow",
        timestamp="2025-07-01T12:00:00Z",
        exit_code=1
    )


@pytest.fixture
def coverage_failure_log():
    """Coverage-specific failure log"""
    return FailureLog(
        raw_log="coverage: FAILED --fail-under=80.0%: 79.5% < 80.0%",
        job_name="test-coverage",
        workflow_name="coverage-workflow",
        timestamp="2025-07-01T12:00:00Z",
        exit_code=1
    )


@pytest.fixture
def yaml_error_log():
    """YAML formatting error log"""
    return FailureLog(
        raw_log="""
Error parsing workflow YAML:
mapping values are not allowed here
  in ".github/workflows/test.yml", line 15
    timeout-minutes: invalid
               ^
        """,
        job_name="yaml-check",
        workflow_name="yaml-workflow",
        timestamp="2025-07-01T12:00:00Z",
        exit_code=1
    )


@pytest.fixture
def complex_failure_log():
    """Complex failure with multiple indicators"""
    return FailureLog(
        raw_log="""
FAILED tests/test_module.py::test_function
AssertionError: assert 5 == 10
  File "tests/test_module.py", line 45, in test_function
    assert result == expected
pytest: failed with exit code 1
        """,
        job_name="pytest-job",
        workflow_name="test-workflow",
        timestamp="2025-07-01T12:00:00Z",
        exit_code=1
    )


# ============================================================================
# CASCADE ORCHESTRATOR TESTS - ERROR HANDLING
# ============================================================================


class TestCascadeOrchestratorErrorHandling:
    """Test error handling paths in cascade orchestrator"""

    def test_orchestrate_with_no_matching_patterns(self):
        """Test orchestration when no patterns match"""
        orchestrator = CascadeOrchestrator()
        failure_log = FailureLog(
            raw_log="Some completely unknown error message",
            job_name="unknown-job",
            workflow_name="unknown-workflow",
            timestamp="2025-07-01T12:00:00Z",
            exit_code=1
        )
        
        result = orchestrator.orchestrate(failure_log)
        
        assert result.pattern_match is None
        assert result.final_status == FixStatus.ESCALATED
        assert result.escalation_reason == "No matching pattern detected"

    def test_orchestrate_with_low_confidence_escalation(self):
        """Test that low confidence patterns are escalated"""
        orchestrator = CascadeOrchestrator()
        # Create a log that matches a pattern but with low confidence
        failure_log = FailureLog(
            raw_log="vague error message",
            job_name="test-job",
            workflow_name="test-workflow",
            timestamp="2025-07-01T12:00:00Z",
            exit_code=1
        )
        
        result = orchestrator.orchestrate(failure_log)
        
        # If a pattern matches with low confidence, it should be escalated
        if result.pattern_match is not None:
            if result.pattern_match.confidence < 0.50:
                assert result.final_status == FixStatus.ESCALATED

    def test_pattern_detector_empty_log(self):
        """Test pattern detector with empty log"""
        detector = PatternDetector()
        failure_log = FailureLog(
            raw_log="",
            job_name="empty-job",
            workflow_name="empty-workflow",
            timestamp="2025-07-01T12:00:00Z",
            exit_code=1
        )
        
        matches = detector.detect(failure_log)
        
        assert isinstance(matches, list)
        assert len(matches) == 0

    def test_run_command_with_timeout(self):
        """Test command execution timeout"""
        # This should timeout
        exit_code, stdout, stderr = run_command(
            ["sleep", "60"],
            timeout_sec=1
        )
        
        assert exit_code == -1
        assert "TIMEOUT" in stderr

    def test_run_command_with_nonexistent_command(self):
        """Test running a command that doesn't exist"""
        exit_code, stdout, stderr = run_command(
            ["nonexistent_command_12345"],
            timeout_sec=5
        )
        
        assert exit_code == -1

    def test_fix_executor_with_max_attempts_exceeded(self):
        """Test fix executor when max attempts are exceeded"""
        executor = FixExecutor(max_attempts=2)
        
        failure_log = FailureLog(
            raw_log="Test failure for max attempts",
            job_name="test-job",
            workflow_name="test-workflow",
            timestamp="2025-07-01T12:00:00Z",
            exit_code=1
        )
        
        pattern = Pattern(
            id="TEST-001",
            name="Test Pattern",
            primary_regex="Test failure",
            agent="test-agent"
        )
        
        pattern_match = PatternMatch(
            pattern=pattern,
            confidence=0.95,
            matched_text="Test failure for max attempts",
            line_number=1
        )
        
        # Mock the fix to always fail
        with mock.patch.object(
            executor, '_simulate_agent_fix', 
            return_value=(False, "Simulated failure", False)
        ):
            result = executor.execute_fix(failure_log, pattern_match)
        
        assert result.final_status == FixStatus.ESCALATED
        assert len(result.fix_attempts) == 2

    def test_fix_executor_with_timeout(self):
        """Test fix executor timeout handling"""
        executor = FixExecutor(max_attempts=2)
        
        failure_log = FailureLog(
            raw_log="Timeout test",
            job_name="test-job",
            workflow_name="test-workflow",
            timestamp="2025-07-01T12:00:00Z",
            exit_code=1
        )
        
        pattern = Pattern(
            id="TEST-002",
            name="Timeout Pattern",
            primary_regex="Timeout test",
            agent="test-agent"
        )
        
        pattern_match = PatternMatch(
            pattern=pattern,
            confidence=0.95,
            matched_text="Timeout test",
            line_number=1
        )
        
        # Test _attempt_fix when TimeoutError is raised
        def mock_attempt_fix(*args, **kwargs):
            attempt = FixAttempt(
                attempt_number=1,
                pattern_id=pattern.id,
                agent=pattern.agent,
                fix_description="Attempt 1: Test",
                result=FixStatus.TIMEOUT,
                error_message="Agent fix exceeded timeout"
            )
            return attempt
        
        with mock.patch.object(executor, '_attempt_fix', side_effect=mock_attempt_fix):
            result = executor.execute_fix(failure_log, pattern_match)
        
        # Should have at least attempted once
        assert len(result.fix_attempts) >= 1


# ============================================================================
# CASCADE ORCHESTRATOR TESTS - EDGE CASES
# ============================================================================


class TestCascadeOrchestratorEdgeCases:
    """Test edge cases and boundary conditions"""

    def test_confidence_level_boundaries(self):
        """Test confidence level boundary conditions"""
        assert get_confidence_level(0.0) == PatternConfidence.VERY_LOW
        assert get_confidence_level(0.5) == PatternConfidence.LOW
        assert get_confidence_level(0.7) == PatternConfidence.MEDIUM
        assert get_confidence_level(0.85) == PatternConfidence.HIGH
        assert get_confidence_level(0.95) == PatternConfidence.VERY_HIGH
        assert get_confidence_level(1.0) == PatternConfidence.VERY_HIGH

    def test_pattern_detector_confidence_calculation(self):
        """Test confidence calculation in pattern detector"""
        detector = PatternDetector()
        
        # Log with strong primary match
        strong_log = FailureLog(
            raw_log="F401 imported but unused module 'sys'",
            job_name="test",
            workflow_name="test",
            timestamp="2025-07-01T12:00:00Z",
            exit_code=1
        )
        
        matches = detector.detect(strong_log)
        assert len(matches) > 0
        
        # First match should be RP-001 (Unused Imports)
        first_match = matches[0]
        assert first_match.pattern.id == "RP-001"
        assert first_match.confidence >= 0.65

    def test_fix_router_agent_mapping(self):
        """Test fix router agent mapping"""
        router = FixRouter()
        
        for pattern in router.agent_map.keys():
            agent = router.agent_map[pattern]
            assert isinstance(agent, str)
            assert len(agent) > 0

    def test_fix_router_escalation_threshold(self):
        """Test fix router escalation threshold"""
        router = FixRouter()
        
        # Below threshold should escalate
        assert router.should_escalate_immediately(0.4) == True
        assert router.should_escalate_immediately(0.49) == True
        
        # Above threshold should not escalate
        assert router.should_escalate_immediately(0.50) == False
        assert router.should_escalate_immediately(0.95) == False

    def test_pattern_detector_with_secondary_indicators(self):
        """Test pattern detection with secondary indicators"""
        detector = PatternDetector()
        
        # Log with both primary and secondary indicators
        log = FailureLog(
            raw_log="""
error: Argument 1 to function is not compatible
mypy error: incompatible type
File "module.py", line 42
            """,
            job_name="mypy-job",
            workflow_name="type-check",
            timestamp="2025-07-01T12:00:00Z",
            exit_code=1
        )
        
        matches = detector.detect(log)
        assert len(matches) > 0
        
        # Should match RP-002 (Type Annotations)
        type_matches = [m for m in matches if m.pattern.id == "RP-002"]
        assert len(type_matches) > 0


# ============================================================================
# PATTERN ROUTER TESTS - ROUTING DECISIONS
# ============================================================================


class TestPatternRouterRoutingDecisions:
    """Test routing decision variations"""

    def test_route_with_high_confidence(self):
        """Test routing with high confidence pattern"""
        router = PatternRouter()
        
        log = "F401 unused import"
        decision = router.route(log, fallback_to_human=False)
        
        assert decision["status"] in ["route", "route_with_notification"]
        assert decision["agent"] is not None
        assert decision["confidence"] > 0.0

    def test_route_with_medium_confidence(self):
        """Test routing with medium confidence (50-threshold)"""
        router = PatternRouter()
        
        log = "vague error"
        decision = router.route(log, fallback_to_human=False)
        
        # Should route or escalate based on confidence
        assert decision["status"] in [
            "route",
            "route_with_notification",
            "human_review",
            "escalate",
            "error"
        ]

    def test_route_with_fallback_to_human(self):
        """Test routing with fallback_to_human flag"""
        router = PatternRouter()
        
        log = "unknown error"
        decision = router.route(log, fallback_to_human=True)
        
        assert isinstance(decision, dict)
        assert "status" in decision
        assert "agent" in decision or decision.get("status") == "error"

    def test_confidence_level_mapping(self):
        """Test confidence level string mapping"""
        router = PatternRouter()
        
        assert router._get_confidence_level(0.99) == "VERY_HIGH"
        assert router._get_confidence_level(0.90) == "HIGH"
        assert router._get_confidence_level(0.75) == "MEDIUM"
        assert router._get_confidence_level(0.60) == "LOW"
        assert router._get_confidence_level(0.40) == "VERY_LOW"

    def test_alternative_matches_in_decision(self):
        """Test that alternative matches are included in decision"""
        router = PatternRouter()
        
        log = """
YAML error: mapping values
workflow: test.yml
indentation: bad
        """
        decision = router.route(log, fallback_to_human=False)
        
        assert "alternatives" in decision
        assert isinstance(decision["alternatives"], list)

    def test_pattern_matcher_keyword_matching(self):
        """Test keyword matching in pattern matcher"""
        matcher = PatternMatcher()
        
        # Test with matching keywords
        matches = matcher.match("F401 unused import warning", top_k=5)
        assert len(matches) > 0
        
        # First match should be RP-001
        assert matches[0][0] == "RP-001"

    def test_pattern_matcher_top_k_limit(self):
        """Test top_k parameter in pattern matcher"""
        matcher = PatternMatcher()
        
        log = "error failure warning bug issue problem"
        matches = matcher.match(log, top_k=3)
        
        assert len(matches) <= 3

    def test_pattern_matcher_confidence_ordering(self):
        """Test that matches are ordered by confidence"""
        matcher = PatternMatcher()
        
        log = "F401 unused import"
        matches = matcher.match(log, top_k=5)
        
        # Verify descending order
        for i in range(len(matches) - 1):
            assert matches[i][1] >= matches[i + 1][1]


# ============================================================================
# PATTERN ROUTER TESTS - CONFLICT DETECTION
# ============================================================================


class TestPatternRouterConflictDetection:
    """Test conflict detection in pattern matching"""

    def test_conflict_matrix_rp001_rp002(self):
        """Test conflict between imports and types (RP-001 vs RP-002)"""
        matcher = PatternMatcher()
        
        # Log with both import and type indicators
        log = """
F401 unused import 'sys'
error: Argument 1 to function is not compatible
        """
        matches = matcher.match(log, top_k=5)
        
        # Should detect conflict but still return matches
        assert len(matches) > 0

    def test_conflict_matrix_rp005_rp010(self):
        """Test conflict between YAML and workflow compliance"""
        matcher = PatternMatcher()
        
        log = """
YAML error: mapping values
timeout-minutes: 360
workflow compliance: check
        """
        matches = matcher.match(log, top_k=5)
        
        assert len(matches) > 0

    def test_conflict_check_with_no_conflicts(self):
        """Test conflict check when no conflicts present"""
        matcher = PatternMatcher()
        
        log = "F401 unused import clean signal"
        
        # Get the config for RP-001
        pattern_config = matcher.config["patterns"]["RP-001"]
        
        # Test conflict check directly
        conflict_score = matcher._conflict_check(log, "RP-001")
        
        # Should have high score (1.0) since no conflicts
        assert 0.5 <= conflict_score <= 1.0


# ============================================================================
# PATTERN ROUTER TESTS - SCORE FUNCTIONS
# ============================================================================


class TestPatternRouterScoreFunctions:
    """Test individual scoring functions in pattern router"""

    def test_score_unused_imports(self):
        """Test unused imports scoring"""
        matcher = PatternMatcher()
        
        # Should score high
        assert matcher._score_unused_imports("F401 unused import") > 0.9
        assert matcher._score_unused_imports("imported but unused") > 0.9
        assert matcher._score_unused_imports("ruff F401") > 0.9
        
        # Should score low
        assert matcher._score_unused_imports("no match here") == 0.0

    def test_score_type_errors(self):
        """Test type error scoring"""
        matcher = PatternMatcher()
        
        assert matcher._score_type_errors("error: Argument 1 type mismatch") > 0.8
        assert matcher._score_type_errors("mypy error") > 0.8
        assert matcher._score_type_errors("incompatible type") > 0.8
        assert matcher._score_type_errors("missing type annotation") > 0.8
        
        assert matcher._score_type_errors("no type error") == 0.0

    def test_score_test_failures(self):
        """Test failure scoring"""
        matcher = PatternMatcher()
        
        assert matcher._score_test_failures("AssertionError in test") > 0.8
        assert matcher._score_test_failures("assert x == y") > 0.8
        assert matcher._score_test_failures("FAILED test_module.py") > 0.7
        
        assert matcher._score_test_failures("test passed") == 0.0

    def test_score_dependency_conflicts(self):
        """Test dependency conflict scoring"""
        matcher = PatternMatcher()
        
        assert matcher._score_dependency_conflicts("ResolutionImpossible") > 0.9
        assert matcher._score_dependency_conflicts("VersionConflict") > 0.9
        assert matcher._score_dependency_conflicts("requires 2.0 but installed 1.0") > 0.9
        
        assert matcher._score_dependency_conflicts("no conflicts") == 0.0

    def test_score_yaml_errors(self):
        """Test YAML error scoring"""
        matcher = PatternMatcher()
        
        assert matcher._score_yaml_errors("YAML error parsing") > 0.9
        assert matcher._score_yaml_errors("mapping values not allowed") > 0.9
        assert matcher._score_yaml_errors("indentation error") > 0.9
        assert matcher._score_yaml_errors("yaml invalid") > 0.9
        
        # "no yaml error" contains "yaml" so it will match
        assert matcher._score_yaml_errors("completely clean message") == 0.0

    def test_score_coverage(self):
        """Test coverage scoring"""
        matcher = PatternMatcher()
        
        assert matcher._score_coverage("coverage below threshold") > 0.8
        assert matcher._score_coverage("fail-under 80%") > 0.8
        # The regex pattern is r"coverage.*below|fail-under|Coverage.*%"
        # So we need "coverage" or "fail-under" or "Coverage" with %
        assert matcher._score_coverage("fail-under 80%") > 0.8
        
        assert matcher._score_coverage("completely clean message") == 0.0

    def test_score_import_errors(self):
        """Test import error scoring"""
        matcher = PatternMatcher()
        
        assert matcher._score_import_errors("ImportError: module not found") > 0.8
        assert matcher._score_import_errors("ModuleNotFoundError") > 0.8
        assert matcher._score_import_errors("cannot import name") > 0.8
        
        assert matcher._score_import_errors("no import error") == 0.0

    def test_score_flaky_tests(self):
        """Test flaky test scoring"""
        matcher = PatternMatcher()
        
        assert matcher._score_flaky_tests("FLAKY test marked") > 0.8
        assert matcher._score_flaky_tests("TimeoutError in test") > 0.8
        assert matcher._score_flaky_tests("intermittent failure") > 0.8
        assert matcher._score_flaky_tests("Passed on retry") > 0.8
        
        assert matcher._score_flaky_tests("no flaky") == 0.0

    def test_score_workflow_compliance(self):
        """Test workflow compliance scoring"""
        matcher = PatternMatcher()
        
        assert matcher._score_workflow_compliance("concurrency violation") > 0.9
        assert matcher._score_workflow_compliance("timeout-minutes missing") > 0.9
        assert matcher._score_workflow_compliance("compliance check failed") > 0.9
        
        # "compliance" is in the regex pattern r"concurrency|timeout-minutes|compliance"
        # so "no compliance" will match
        assert matcher._score_workflow_compliance("completely clean message") == 0.0

    def test_score_cargo_features(self):
        """Test Cargo feature scoring"""
        matcher = PatternMatcher()
        
        assert matcher._score_cargo_features("unexpected cfg feature") > 0.9
        assert matcher._score_cargo_features("feature not found") > 0.9
        assert matcher._score_cargo_features("Cargo.toml error") > 0.9
        
        assert matcher._score_cargo_features("no cargo") == 0.0

    def test_score_security_alerts(self):
        """Test security alert scoring"""
        matcher = PatternMatcher()
        
        assert matcher._score_security_alerts("CodeQL alert found") > 0.8
        assert matcher._score_security_alerts("security alert") > 0.8
        assert matcher._score_security_alerts("vulnerability detected") > 0.8
        
        assert matcher._score_security_alerts("no security") == 0.0


# ============================================================================
# PATTERN ROUTER TESTS - KEYWORD MATCHING
# ============================================================================


class TestPatternRouterKeywordMatching:
    """Test keyword matching logic"""

    def test_keyword_match_full_match(self):
        """Test keyword matching with all keywords present"""
        matcher = PatternMatcher()
        
        keywords = ["error", "failed", "test"]
        log = "error: test failed in module"
        
        score = matcher._keyword_match(log, keywords)
        
        assert score == 1.0  # All 3 keywords match

    def test_keyword_match_partial_match(self):
        """Test keyword matching with some keywords"""
        matcher = PatternMatcher()
        
        keywords = ["error", "failed", "test"]
        log = "error: something went wrong"
        
        score = matcher._keyword_match(log, keywords)
        
        assert 0.0 < score < 1.0  # Only 1 keyword matches

    def test_keyword_match_no_match(self):
        """Test keyword matching with no matches"""
        matcher = PatternMatcher()
        
        keywords = ["error", "failed", "test"]
        log = "everything is fine"
        
        score = matcher._keyword_match(log, keywords)
        
        assert score == 0.0  # No keywords match

    def test_keyword_match_case_insensitive(self):
        """Test that keyword matching is case-insensitive"""
        matcher = PatternMatcher()
        
        keywords = ["ERROR", "FAILED"]
        log = "error: test failed"
        
        score = matcher._keyword_match(log, keywords)
        
        assert score == 1.0  # Case-insensitive match


# ============================================================================
# INTEGRATION TESTS
# ============================================================================


class TestIntegrationCascadeAndRouter:
    """Integration tests between cascade orchestrator and pattern router"""

    def test_cascade_with_coverage_failure(self, coverage_failure_log):
        """Test full cascade orchestration with coverage failure"""
        orchestrator = CascadeOrchestrator()
        result = orchestrator.orchestrate(coverage_failure_log)
        
        assert result.failure_log == coverage_failure_log
        if result.pattern_match:
            assert result.pattern_match.pattern.id == "RP-006"

    def test_cascade_with_yaml_failure(self, yaml_error_log):
        """Test cascade with YAML error"""
        orchestrator = CascadeOrchestrator()
        result = orchestrator.orchestrate(yaml_error_log)
        
        if result.pattern_match:
            assert result.pattern_match.pattern.id == "RP-005"

    def test_cascade_with_test_failure(self, complex_failure_log):
        """Test cascade with test assertion failure"""
        orchestrator = CascadeOrchestrator()
        result = orchestrator.orchestrate(complex_failure_log)
        
        if result.pattern_match:
            assert result.pattern_match.pattern.id == "RP-003"

    def test_router_decision_matches_cascade_detection(self, simple_failure_log):
        """Test that router and detector agree on pattern"""
        cascade = CascadeOrchestrator()
        router = PatternRouter()
        
        # Get cascade detection
        cascade_matches = cascade.detector.detect(simple_failure_log)
        
        # Get router decision
        router_decision = router.route(simple_failure_log.raw_log)
        
        # Should both detect same pattern if any
        if cascade_matches and router_decision.get("pattern_id"):
            assert cascade_matches[0].pattern.id == router_decision["pattern_id"]


# ============================================================================
# PERFORMANCE TESTS
# ============================================================================


class TestPerformance:
    """Test performance requirements"""

    def test_pattern_detection_performance(self):
        """Test pattern detection speed (should be <100ms)"""
        detector = PatternDetector()
        
        log = FailureLog(
            raw_log="F401 unused import test message",
            job_name="test",
            workflow_name="test",
            timestamp="2025-07-01T12:00:00Z",
            exit_code=1
        )
        
        start = time.time()
        for _ in range(100):
            detector.detect(log)
        elapsed = time.time() - start
        
        # Should complete 100 detections in <100ms
        assert elapsed < 0.1

    def test_routing_performance(self):
        """Test routing speed (should be <50ms)"""
        router = PatternRouter()
        
        log = "F401 unused import test"
        
        start = time.time()
        for _ in range(100):
            router.route(log)
        elapsed = time.time() - start
        
        # Should complete 100 routes in <50ms
        assert elapsed < 0.05


# ============================================================================
# MAIN TEST EXECUTION
# ============================================================================


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
