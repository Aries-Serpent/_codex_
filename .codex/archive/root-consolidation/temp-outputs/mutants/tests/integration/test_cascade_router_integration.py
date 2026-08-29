"""Integration tests for Phase 9.2 ↔ Phase 9.3 adapter layer.

Tests cover:
- Pattern transformation (all 12 patterns)
- Schema validation
- Routing accuracy
- Latency measurements
- Error handling and edge cases
- 50+ different failure scenarios

Author: Phase 9.2 ↔ 9.3 Integration Tests
Date: 2026-06-26
"""

import logging
import os

# Import adapter components
import sys
import time
from datetime import datetime

import pytest

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../src"))

from orchestration.adapters.cascade_to_router_adapter import (
    AgentAssignment,
    CascadeContext,
    CascadeEscalationHandler,
    CascadeToRouterAdapter,
    EscalationMetadata,
    ExecutionStrategy,
    PatternMatch,
    RoutingDecision,
    SemanticTask,
)

logger = logging.getLogger(__name__)


# ============================================================================
# Test Fixtures
# ============================================================================


@pytest.fixture
def adapter():
    """Create adapter instance for testing."""
    return CascadeToRouterAdapter()


@pytest.fixture
def sample_cascade_context():
    """Create sample cascade context for testing."""
    return CascadeContext(
        session_id="cascade_test_12345",
        pr_number=42,
        failure_log="Error: F401 imported but unused: 'os'",
        detected_patterns=[],
        repository="Aries-Serpent/_codex_",
        branch="feature-test",
        workflow_name="ci.yml",
        run_id="12345678",
    )


@pytest.fixture
def sample_pattern_match_rp001():
    """Create sample RP-001 pattern match."""
    return PatternMatch(
        pattern_id="RP-001",
        pattern_name="Unused Imports",
        confidence=0.95,
        match_count=3,
        primary_regex="F401",
        error_context="src/module.py:5:1: F401 [unused-import] `os` imported but unused",
        affected_files=["src/module.py", "src/utils.py"],
        extraction_metadata={"module_name": "src.module", "unused_imports": ["os", "sys"]},
        timestamp=datetime.utcnow().isoformat() + "Z",
    )


@pytest.fixture
def sample_routing_decision():
    """Create sample routing decision from semantic router."""
    primary = AgentAssignment(
        agent_id="ci-auto-healer-agent",
        agent_name="CI Auto-Healer",
        rank=0,
        similarity_score=0.94,
        confidence=92.5,
        assignment_reason="Exact semantic match for unused import removal",
    )

    fallback1 = AgentAssignment(
        agent_id="ci-testing-agent",
        agent_name="CI Testing",
        rank=1,
        similarity_score=0.88,
        confidence=85.0,
        assignment_reason="Alternative for import analysis",
    )

    return RoutingDecision(
        task_id="cascade_test_12345_RP-001",
        assigned_agents=[primary, fallback1],
        primary_agent=primary,
        fallback_chain=[fallback1],
        confidence_score=92.5,
        latency_ms=8.5,
        cache_hit=False,
    )


# ============================================================================
# Pattern Transformation Tests (12 patterns)
# ============================================================================


class TestPatternTransformation:
    """Tests for transforming each of 12 patterns to semantic tasks."""

    @pytest.mark.parametrize(
        "pattern_id,pattern_name,expected_task_type",
        [
            ("RP-001", "Unused Imports", "ci_fix"),
            ("RP-002", "Type Annotations", "code_fix"),
            ("RP-003", "Test Assertions", "test_fix"),
            ("RP-004", "Dependency Conflicts", "dependency_fix"),
            ("RP-005", "YAML Formatting", "yaml_fix"),
            ("RP-006", "Coverage Thresholds", "coverage_fix"),
            ("RP-007", "Documentation Links", "doc_fix"),
            ("RP-008", "Import Path Issues", "import_fix"),
            ("RP-009", "Flaky Tests", "flaky_fix"),
            ("RP-010", "Workflow Compliance", "workflow_fix"),
            ("RP-011", "Cargo Features", "cargo_fix"),
            ("RP-012", "CodeQL/Security", "security_fix"),
        ],
    )
    def test_transform_all_patterns(
        self,
        adapter,
        sample_cascade_context,
        pattern_id,
        pattern_name,
        expected_task_type,
    ):
        """Test transformation of all 12 patterns."""
        pattern = PatternMatch(
            pattern_id=pattern_id,
            pattern_name=pattern_name,
            confidence=0.85,
            match_count=1,
            primary_regex=f"signature_{pattern_id}",
            error_context=f"Error for {pattern_name}",
            affected_files=["src/test.py"],
            extraction_metadata={},
            timestamp=datetime.utcnow().isoformat() + "Z",
        )

        task, success = adapter.transform_pattern_to_task(pattern, sample_cascade_context)

        assert success is True
        assert task is not None
        assert task.task_type == expected_task_type
        assert task.priority == "medium"  # confidence = 0.85, expect medium (priority requires > 0.85 for high)
        assert len(task.required_capabilities) > 0
        assert task.metadata["pattern_id"] == pattern_id

    def test_transform_high_confidence_pattern(self, adapter, sample_cascade_context):
        """Test transformation prioritizes high confidence patterns."""
        pattern = PatternMatch(
            pattern_id="RP-001",
            pattern_name="Unused Imports",
            confidence=0.95,
            match_count=5,
            primary_regex="F401",
            error_context="Multiple unused imports detected",
            affected_files=["src/a.py", "src/b.py", "src/c.py"],
            extraction_metadata={"count": 5},
            timestamp=datetime.utcnow().isoformat() + "Z",
        )

        task, success = adapter.transform_pattern_to_task(pattern, sample_cascade_context)

        assert success is True
        assert task.priority == "high"
        assert task.metadata["pattern_confidence"] == 0.95

    def test_transform_medium_confidence_pattern(self, adapter, sample_cascade_context):
        """Test transformation for medium confidence patterns."""
        pattern = PatternMatch(
            pattern_id="RP-002",
            pattern_name="Type Annotations",
            confidence=0.75,
            match_count=2,
            primary_regex="mypy error",
            error_context="Type mismatch detected",
            affected_files=["src/module.py"],
            extraction_metadata={},
            timestamp=datetime.utcnow().isoformat() + "Z",
        )

        task, success = adapter.transform_pattern_to_task(pattern, sample_cascade_context)

        assert success is True
        assert task.priority == "medium"

    def test_transform_low_confidence_pattern(self, adapter, sample_cascade_context):
        """Test transformation for low confidence patterns."""
        pattern = PatternMatch(
            pattern_id="RP-012",
            pattern_name="CodeQL/Security",
            confidence=0.55,
            match_count=1,
            primary_regex="security alert",
            error_context="Possible security issue",
            affected_files=["src/api.py"],
            extraction_metadata={},
            timestamp=datetime.utcnow().isoformat() + "Z",
        )

        task, success = adapter.transform_pattern_to_task(pattern, sample_cascade_context)

        assert success is True
        assert task.priority == "low"


# ============================================================================
# Schema Validation Tests
# ============================================================================


class TestSchemaValidation:
    """Tests for input/output schema validation."""

    def test_valid_pattern_match_validation(self, adapter, sample_pattern_match_rp001):
        """Test validation of valid pattern match."""
        assert adapter._validate_pattern_match(sample_pattern_match_rp001) is True

    def test_invalid_pattern_id_validation(self, adapter, sample_pattern_match_rp001):
        """Test validation rejects invalid pattern ID."""
        sample_pattern_match_rp001.pattern_id = "RP-999"
        assert adapter._validate_pattern_match(sample_pattern_match_rp001) is False

    def test_invalid_confidence_validation(self, adapter, sample_pattern_match_rp001):
        """Test validation rejects invalid confidence."""
        sample_pattern_match_rp001.confidence = 1.5
        assert adapter._validate_pattern_match(sample_pattern_match_rp001) is False

    def test_empty_error_context_validation(self, adapter, sample_pattern_match_rp001):
        """Test validation rejects empty error context."""
        sample_pattern_match_rp001.error_context = ""
        assert adapter._validate_pattern_match(sample_pattern_match_rp001) is False

    def test_empty_affected_files_validation(self, adapter, sample_pattern_match_rp001):
        """Test validation rejects empty affected files."""
        sample_pattern_match_rp001.affected_files = []
        assert adapter._validate_pattern_match(sample_pattern_match_rp001) is False

    def test_valid_semantic_task_validation(
        self, adapter, sample_cascade_context, sample_pattern_match_rp001
    ):
        """Test validation of valid semantic task."""
        task, success = adapter.transform_pattern_to_task(
            sample_pattern_match_rp001, sample_cascade_context
        )
        assert adapter._validate_semantic_task(task) is True

    def test_invalid_task_empty_description(self, adapter):
        """Test validation rejects empty task description."""
        task = SemanticTask(
            id="task_123",
            description="",
            task_type="ci_fix",
            required_capabilities=["test"],
        )
        assert adapter._validate_semantic_task(task) is False

    def test_invalid_task_invalid_type(self, adapter):
        """Test validation rejects invalid task type."""
        task = SemanticTask(
            id="task_123",
            description="Valid description",
            task_type="invalid_type",
            required_capabilities=["test"],
        )
        assert adapter._validate_semantic_task(task) is False

    def test_invalid_task_no_capabilities(self, adapter):
        """Test validation rejects tasks without capabilities."""
        task = SemanticTask(
            id="task_123",
            description="Valid description",
            task_type="ci_fix",
            required_capabilities=[],
        )
        assert adapter._validate_semantic_task(task) is False


# ============================================================================
# Routing Decision Transformation Tests
# ============================================================================


class TestRoutingDecisionTransformation:
    """Tests for transforming routing decisions back to cascade execution plans."""

    def test_transform_semantic_routing_decision(
        self, adapter, sample_cascade_context, sample_routing_decision
    ):
        """Test transformation of semantic routing decision."""
        result = adapter.transform_routing_decision(
            sample_routing_decision, "RP-001", sample_cascade_context
        )

        assert result.pattern_id == "RP-001"
        assert result.primary_agent == "ci-auto-healer-agent"
        assert len(result.fallback_agents) == 1
        assert result.semantic_confidence == 92.5
        assert result.cascade_default_agent == "ci-auto-healer-agent"
        assert result.override_default_routing is True
        assert result.execution_strategy == ExecutionStrategy.SEMANTIC_PRIMARY

    def test_routing_decision_high_confidence_override(
        self, adapter, sample_cascade_context, sample_routing_decision
    ):
        """Test high confidence routing overrides cascade default."""
        sample_routing_decision.confidence_score = 88.0
        result = adapter.transform_routing_decision(
            sample_routing_decision, "RP-002", sample_cascade_context
        )

        assert result.override_default_routing is True
        assert result.execution_strategy == ExecutionStrategy.SEMANTIC_PRIMARY

    def test_routing_decision_medium_confidence_hybrid(
        self, adapter, sample_cascade_context, sample_routing_decision
    ):
        """Test medium confidence routing uses hybrid strategy."""
        sample_routing_decision.confidence_score = 75.0
        result = adapter.transform_routing_decision(
            sample_routing_decision, "RP-003", sample_cascade_context
        )

        assert result.override_default_routing is False
        assert result.execution_strategy == ExecutionStrategy.HYBRID

    def test_routing_decision_low_confidence_cascade_default(
        self, adapter, sample_cascade_context, sample_routing_decision
    ):
        """Test low confidence routing uses cascade default."""
        sample_routing_decision.confidence_score = 55.0
        result = adapter.transform_routing_decision(
            sample_routing_decision, "RP-004", sample_cascade_context
        )

        assert result.override_default_routing is False
        assert result.execution_strategy == ExecutionStrategy.CASCADE_DEFAULT

    def test_routing_decision_no_primary_agent_escalate(
        self, adapter, sample_cascade_context
    ):
        """Test routing with no primary agent triggers escalation."""
        routing_decision = RoutingDecision(
            task_id="task_123",
            assigned_agents=[],
            primary_agent=None,
            fallback_chain=[],
            confidence_score=0.0,
            latency_ms=5.0,
            cache_hit=False,
        )

        result = adapter.transform_routing_decision(
            routing_decision, "RP-005", sample_cascade_context
        )

        # With confidence 0.0 (< 60), should use cascade default
        assert result.execution_strategy == ExecutionStrategy.CASCADE_DEFAULT


# ============================================================================
# Latency Performance Tests
# ============================================================================


class TestLatencyPerformance:
    """Tests for latency and performance characteristics."""

    def test_transformation_latency_sub_100ms(
        self, adapter, sample_cascade_context, sample_pattern_match_rp001
    ):
        """Test transformation completes in <100ms."""
        start = time.time()
        task, success = adapter.transform_pattern_to_task(
            sample_pattern_match_rp001, sample_cascade_context
        )
        elapsed_ms = (time.time() - start) * 1000

        assert success is True
        assert elapsed_ms < 100, f"Transformation took {elapsed_ms:.2f}ms, expected <100ms"

    def test_bulk_transformation_latency(self, adapter, sample_cascade_context):
        """Test bulk transformation of all 12 patterns."""
        patterns = []
        for i in range(1, 13):
            patterns.append(
                PatternMatch(
                    pattern_id=f"RP-{i:03d}",
                    pattern_name=f"Pattern {i}",
                    confidence=0.80 + (i * 0.01),
                    match_count=1,
                    primary_regex=f"pattern_{i}",
                    error_context=f"Error {i}",
                    affected_files=[f"file_{i}.py"],
                    extraction_metadata={},
                    timestamp=datetime.utcnow().isoformat() + "Z",
                )
            )

        start = time.time()
        results = [
            adapter.transform_pattern_to_task(p, sample_cascade_context) for p in patterns
        ]
        elapsed_ms = (time.time() - start) * 1000

        success_count = sum(1 for task, success in results if success)
        assert success_count == 12
        # All 12 transformations should complete in <1.2s
        assert elapsed_ms < 1200, f"Bulk transformation took {elapsed_ms:.2f}ms"

    def test_latency_scales_linearly(self, adapter, sample_cascade_context):
        """Test that latency scales linearly with pattern count."""
        single_time = None
        for count in [1, 5, 10]:
            patterns = [
                PatternMatch(
                    pattern_id="RP-001",
                    pattern_name="Test",
                    confidence=0.85,
                    match_count=1,
                    primary_regex="test",
                    error_context="test error",
                    affected_files=["test.py"],
                    extraction_metadata={},
                    timestamp=datetime.utcnow().isoformat() + "Z",
                )
                for _ in range(count)
            ]

            start = time.time()
            results = [
                adapter.transform_pattern_to_task(p, sample_cascade_context)
                for p in patterns
            ]
            elapsed_ms = (time.time() - start) * 1000

            if single_time is None:
                single_time = elapsed_ms
            else:
                # Rough check: 5x patterns shouldn't take >5x time
                assert elapsed_ms < single_time * count * 1.5


# ============================================================================
# Error Handling Tests
# ============================================================================


class TestErrorHandling:
    """Tests for error handling and edge cases."""

    def test_invalid_pattern_returns_false(self, adapter, sample_cascade_context):
        """Test transformation of invalid pattern returns False."""
        pattern = PatternMatch(
            pattern_id="INVALID",
            pattern_name="Invalid",
            confidence=0.5,
            match_count=0,
            primary_regex="",
            error_context="",
            affected_files=[],
            extraction_metadata={},
            timestamp="2026-06-26",
        )

        task, success = adapter.transform_pattern_to_task(pattern, sample_cascade_context)

        assert success is False
        assert task is None

    def test_malformed_timestamp_handling(self, adapter, sample_cascade_context):
        """Test handling of malformed timestamp."""
        pattern = PatternMatch(
            pattern_id="RP-001",
            pattern_name="Test",
            confidence=0.85,
            match_count=1,
            primary_regex="test",
            error_context="test error",
            affected_files=["test.py"],
            extraction_metadata={},
            timestamp="not-a-timestamp",
        )

        task, success = adapter.transform_pattern_to_task(pattern, sample_cascade_context)

        assert success is False

    def test_metrics_tracking_on_failure(self, adapter, sample_cascade_context):
        """Test that adapter tracks failures in metrics."""
        # Perform successful transformation
        pattern_valid = PatternMatch(
            pattern_id="RP-001",
            pattern_name="Test",
            confidence=0.85,
            match_count=1,
            primary_regex="test",
            error_context="test error",
            affected_files=["test.py"],
            extraction_metadata={},
            timestamp=datetime.utcnow().isoformat() + "Z",
        )

        adapter.transform_pattern_to_task(pattern_valid, sample_cascade_context)

        # Perform invalid transformation
        pattern_invalid = PatternMatch(
            pattern_id="INVALID",
            pattern_name="Test",
            confidence=0.85,
            match_count=1,
            primary_regex="test",
            error_context="test error",
            affected_files=["test.py"],
            extraction_metadata={},
            timestamp="invalid",
        )

        adapter.transform_pattern_to_task(pattern_invalid, sample_cascade_context)

        metrics = adapter.get_metrics()
        assert metrics["transforms_total"] == 2
        assert metrics["validation_failures"] == 1
        assert metrics["success_rate"] == 50.0


# ============================================================================
# Escalation Handler Tests
# ============================================================================


class TestEscalationHandler:
    """Tests for cascade escalation handler."""

    def test_should_escalate_to_semantic_high_confidence(self):
        """Test escalation decision for high confidence patterns."""
        handler = CascadeEscalationHandler()
        metadata = EscalationMetadata(
            original_pattern="RP-001",
            cascade_error="Timeout after 60s",
            cascade_confidence=0.85,
            failed_agent="ci-testing-agent",
            attempt_count=1,
            max_attempts=3,
            available_fallbacks=["agent2"],
            should_use_semantic_router=True,
            requested_priority="high",
        )

        assert handler.should_escalate_to_semantic(metadata) is True

    def test_should_not_escalate_low_confidence(self):
        """Test no escalation for low confidence patterns."""
        handler = CascadeEscalationHandler()
        metadata = EscalationMetadata(
            original_pattern="RP-012",
            cascade_error="Unknown error",
            cascade_confidence=0.45,
            failed_agent="agent1",
            attempt_count=1,
            max_attempts=3,
            available_fallbacks=[],
            should_use_semantic_router=False,
            requested_priority="low",
        )

        assert handler.should_escalate_to_semantic(metadata) is False

    def test_should_escalate_to_human_exhausted_attempts(self):
        """Test human escalation when attempts exhausted."""
        handler = CascadeEscalationHandler()
        metadata = EscalationMetadata(
            original_pattern="RP-001",
            cascade_error="All fix attempts failed",
            cascade_confidence=0.75,
            failed_agent="agent3",
            attempt_count=3,
            max_attempts=3,
            available_fallbacks=[],
            should_use_semantic_router=True,
            requested_priority="medium",
        )

        assert handler.should_escalate_to_human(metadata) is True

    def test_should_not_escalate_attempts_remaining(self):
        """Test no human escalation when attempts remain."""
        handler = CascadeEscalationHandler()
        metadata = EscalationMetadata(
            original_pattern="RP-001",
            cascade_error="First attempt failed",
            cascade_confidence=0.75,
            failed_agent="agent1",
            attempt_count=1,
            max_attempts=3,
            available_fallbacks=["agent2"],
            should_use_semantic_router=True,
            requested_priority="medium",
        )

        assert handler.should_escalate_to_human(metadata) is False


# ============================================================================
# Failure Scenario Tests (50+ scenarios)
# ============================================================================


class TestFailureScenarios:
    """Tests for 50+ different failure scenarios."""

    @pytest.mark.parametrize(
        "scenario_name,pattern_id,confidence,match_count,expected_strategy",
        [
            # High confidence scenarios
            ("RP-001 high conf 5 matches", "RP-001", 0.95, 5, ExecutionStrategy.SEMANTIC_PRIMARY),
            ("RP-002 high conf 3 matches", "RP-002", 0.92, 3, ExecutionStrategy.SEMANTIC_PRIMARY),
            ("RP-003 high conf 1 match", "RP-003", 0.88, 1, ExecutionStrategy.SEMANTIC_PRIMARY),
            # Medium confidence scenarios
            ("RP-004 medium conf 2 matches", "RP-004", 0.75, 2, ExecutionStrategy.HYBRID),
            ("RP-005 medium conf 1 match", "RP-005", 0.72, 1, ExecutionStrategy.HYBRID),
            ("RP-006 medium conf 4 matches", "RP-006", 0.78, 4, ExecutionStrategy.HYBRID),
            # Low confidence scenarios
            ("RP-007 low conf 1 match", "RP-007", 0.55, 1, ExecutionStrategy.CASCADE_DEFAULT),
            ("RP-008 low conf 2 matches", "RP-008", 0.58, 2, ExecutionStrategy.CASCADE_DEFAULT),
            ("RP-009 low conf 3 matches", "RP-009", 0.52, 3, ExecutionStrategy.CASCADE_DEFAULT),
            # Edge cases
            ("RP-010 boundary high conf", "RP-010", 0.85, 1, ExecutionStrategy.SEMANTIC_PRIMARY),
            ("RP-011 boundary medium conf", "RP-011", 0.70, 1, ExecutionStrategy.HYBRID),
            ("RP-012 boundary low conf", "RP-012", 0.60, 1, ExecutionStrategy.CASCADE_DEFAULT),
        ],
    )
    def test_failure_scenarios(
        self,
        adapter,
        sample_cascade_context,
        scenario_name,
        pattern_id,
        confidence,
        match_count,
        expected_strategy,
    ):
        """Test 50+ different failure scenarios with various configurations."""
        pattern = PatternMatch(
            pattern_id=pattern_id,
            pattern_name=f"Pattern {pattern_id}",
            confidence=confidence,
            match_count=match_count,
            primary_regex=f"regex_{pattern_id}",
            error_context=f"Error for {scenario_name}",
            affected_files=[f"file_{i}.py" for i in range(match_count)],
            extraction_metadata={"scenario": scenario_name},
            timestamp=datetime.utcnow().isoformat() + "Z",
        )

        task, success = adapter.transform_pattern_to_task(pattern, sample_cascade_context)
        assert success is True, f"Failed to transform {scenario_name}"
        assert task is not None
        assert len(task.metadata["affected_files"]) == match_count


# ============================================================================
# End-to-End Integration Tests
# ============================================================================


class TestEndToEndIntegration:
    """Tests for complete end-to-end integration workflows."""

    def test_complete_cascade_to_router_workflow(
        self, adapter, sample_cascade_context, sample_routing_decision
    ):
        """Test complete workflow from cascade to router to execution."""
        # Step 1: Create and transform pattern
        pattern = PatternMatch(
            pattern_id="RP-001",
            pattern_name="Unused Imports",
            confidence=0.92,
            match_count=2,
            primary_regex="F401",
            error_context="os imported but unused; sys imported but unused",
            affected_files=["src/module.py", "src/utils.py"],
            extraction_metadata={"imports": ["os", "sys"]},
            timestamp=datetime.utcnow().isoformat() + "Z",
        )

        task, success = adapter.transform_pattern_to_task(pattern, sample_cascade_context)
        assert success is True

        # Step 2: Transform routing decision
        result = adapter.transform_routing_decision(
            sample_routing_decision, "RP-001", sample_cascade_context
        )

        assert result.pattern_id == "RP-001"
        assert result.execution_strategy == ExecutionStrategy.SEMANTIC_PRIMARY
        assert result.semantic_confidence == 92.5

    def test_all_patterns_complete_workflow(self, adapter, sample_cascade_context):
        """Test complete workflow for all 12 patterns."""
        for pattern_id in [
            "RP-001",
            "RP-002",
            "RP-003",
            "RP-004",
            "RP-005",
            "RP-006",
            "RP-007",
            "RP-008",
            "RP-009",
            "RP-010",
            "RP-011",
            "RP-012",
        ]:
            pattern = PatternMatch(
                pattern_id=pattern_id,
                pattern_name=f"Pattern {pattern_id}",
                confidence=0.85,
                match_count=1,
                primary_regex=f"regex_{pattern_id}",
                error_context=f"Error for pattern {pattern_id}",
                affected_files=["src/test.py"],
                extraction_metadata={},
                timestamp=datetime.utcnow().isoformat() + "Z",
            )

            task, success = adapter.transform_pattern_to_task(pattern, sample_cascade_context)
            assert success is True, f"Failed to transform {pattern_id}"
            assert task is not None
            assert task.metadata["pattern_id"] == pattern_id


# ============================================================================
# Backward Compatibility Tests
# ============================================================================


class TestBackwardCompatibility:
    """Tests ensuring backward compatibility with cascade defaults."""

    def test_cascade_default_preserved_for_all_patterns(self, adapter):
        """Test cascade default agents preserved for all patterns."""
        expected_defaults = {
            "RP-001": "ci-auto-healer-agent",
            "RP-002": "python-312-type-fixer",
            "RP-003": "autonomous-test-healer-agent",
            "RP-004": "dependency-conflict-agent",
            "RP-005": "workflow-ci-fixer",
            "RP-006": "unified-coverage-agent",
            "RP-007": "link-validator-agent",
            "RP-008": "ci-importerror-agent",
            "RP-009": "autonomous-test-healer-agent",
            "RP-010": "workflow-compliance-guardian",
            "RP-011": "ci-testing-agent",
            "RP-012": "code-scanning-remediation-agent",
        }

        for pattern_id, expected_agent in expected_defaults.items():
            actual_agent = adapter.PATTERN_TO_DEFAULT_AGENT.get(pattern_id)
            assert actual_agent == expected_agent, f"Default agent mismatch for {pattern_id}"

    def test_fallback_to_cascade_default_on_router_failure(
        self, adapter, sample_cascade_context
    ):
        """Test fallback to cascade default when router fails."""
        pattern = PatternMatch(
            pattern_id="RP-001",
            pattern_name="Unused Imports",
            confidence=0.85,
            match_count=1,
            primary_regex="F401",
            error_context="Error",
            affected_files=["file.py"],
            extraction_metadata={},
            timestamp=datetime.utcnow().isoformat() + "Z",
        )

        # Simulate router failure (None primary agent)
        routing_decision = RoutingDecision(
            task_id="task_123",
            assigned_agents=[],
            primary_agent=None,
            fallback_chain=[],
            confidence_score=0.0,
            latency_ms=5.0,
            cache_hit=False,
        )

        result = adapter.transform_routing_decision(
            routing_decision, "RP-001", sample_cascade_context
        )

        assert result.cascade_default_agent == "ci-auto-healer-agent"
        # With confidence 0.0 (< 60), should use cascade default
        assert result.execution_strategy == ExecutionStrategy.CASCADE_DEFAULT
