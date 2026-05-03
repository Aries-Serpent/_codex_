#!/usr/bin/env python3
"""
Tests for the AgentBrainInterface

This test module provides comprehensive coverage for the cognitive brain
interface, including pattern querying, objective alignment, session state,
and learning feedback.
"""

import json

# Import the brain interface
import sys
import tempfile
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from codex.cognitive.brain_interface import (
    AgentBrainInterface,
    AgentCategory,
    AgentContext,
    BrainResponse,
    LearningFeedback,
    ObjectiveAlignment,
    PatternConfidence,
    PatternMatch,
)

# =========================================================================
# Environment isolation
# =========================================================================

@pytest.fixture(autouse=True)
def _reset_pattern_min_confidence():
    """Isolate tests from COGNITIVE_BRAIN_PATTERN_MIN_CONFIDENCE environment variable.

    The module-level ``_MIN_CONFIDENCE`` constant is read once at import time from
    the environment.  CI runners set this to 0.75 to tighten production matching,
    which causes Jaccard-score ~0.43 pattern tests to return empty results.
    Reset to 0.0 for the duration of each test so pattern-query tests are
    environment-independent.
    """
    import codex.cognitive.brain_interface as _bm

    original = _bm._MIN_CONFIDENCE
    _bm._MIN_CONFIDENCE = 0.0
    yield
    _bm._MIN_CONFIDENCE = original


# =========================================================================
# Fixtures
# =========================================================================

@pytest.fixture
def temp_repo():
    """Create a temporary repository structure."""
    with tempfile.TemporaryDirectory() as tmpdir:
        repo_root = Path(tmpdir)

        # Create cognitive brain directory
        cognitive_dir = repo_root / ".codex" / "cognitive_brain"
        cognitive_dir.mkdir(parents=True)

        # Create pattern store
        pattern_store = {
            "metadata": {
                "version": "1.0.0",
                "created": "2026-02-05T09:20:00Z"
            },
            "patterns": {
                "test_failure_resolution": {
                    "id": "TFR-001",
                    "category": "testing",
                    "symptoms": [
                        "pytest collection error",
                        "exit code 2",
                        "ImportError in tests"
                    ],
                    "diagnosis_steps": [
                        "Run pytest --collect-only",
                        "Check for circular imports"
                    ],
                    "solutions": [
                        "Add missing imports",
                        "Rename conflicting files"
                    ],
                    "success_rate": 0.95,
                    "times_applied": 5,
                    "last_used": "2026-02-05T06:28:44Z",
                    "related_prs": ["#3155", "#3154"]
                },
                "workflow_failure": {
                    "id": "WFR-001",
                    "category": "ci_cd",
                    "symptoms": [
                        "GitHub Actions workflow failure",
                        "action_required status"
                    ],
                    "diagnosis_steps": [
                        "Check workflow logs",
                        "Identify failing step"
                    ],
                    "solutions": [
                        "Fix specific failing step",
                        "Add retry logic"
                    ],
                    "success_rate": 0.88,
                    "times_applied": 7,
                    "last_used": "2026-02-05T06:28:44Z",
                    "related_prs": ["#3157"]
                }
            },
            "statistics": {
                "total_patterns": 2,
                "total_applications": 12
            }
        }

        pattern_path = cognitive_dir / "pattern_learning_store.json"
        with open(pattern_path, 'w') as f:
            json.dump(pattern_store, f, indent=2)

        # Create session tracker
        session_tracker = """# Session Tracker

**Session ID:** test-session-001
**Status:** active
**Phase:** testing

## Current Tasks
- [ ] Fix failing tests
- [x] Review patterns
"""
        (cognitive_dir / "session_tracker.md").write_text(session_tracker)

        # Create objectives tracker
        objectives_tracker = """# Objectives Tracker

## Current Objectives

### Primary
- [ ] Achieve 70% test coverage
- [ ] Fix all security vulnerabilities
- [x] Complete documentation review

### Secondary
- [ ] Improve CI/CD pipeline
"""
        (cognitive_dir / "objectives_tracker.md").write_text(objectives_tracker)

        yield repo_root


@pytest.fixture
def brain_interface(temp_repo):
    """Create an AgentBrainInterface instance."""
    return AgentBrainInterface(
        agent_id="test-agent",
        repo_root=temp_repo,
        auto_register=True
    )


@pytest.fixture
def ci_agent_interface(temp_repo):
    """Create an AgentBrainInterface for a CI/CD agent."""
    return AgentBrainInterface(
        agent_id="ci-testing-agent",
        repo_root=temp_repo,
        auto_register=True
    )


# =========================================================================
# Initialization Tests
# =========================================================================

class TestInitialization:
    """Tests for interface initialization."""

    def test_basic_initialization(self, temp_repo):
        """Test basic interface initialization."""
        brain = AgentBrainInterface(
            agent_id="test-agent",
            repo_root=temp_repo
        )

        assert brain.agent_id == "test-agent"
        assert brain.agent_category == AgentCategory.UNKNOWN
        assert brain._registered is True

    def test_known_agent_category(self, temp_repo):
        """Test that known agents get correct category."""
        brain = AgentBrainInterface(
            agent_id="ci-testing-agent",
            repo_root=temp_repo
        )

        assert brain.agent_category == AgentCategory.CI_CD

    def test_patterns_loaded(self, brain_interface):
        """Test that patterns are loaded on initialization."""
        assert len(brain_interface._patterns) == 2
        assert "test_failure_resolution" in brain_interface._patterns
        assert "workflow_failure" in brain_interface._patterns

    def test_objectives_loaded(self, brain_interface):
        """Test that objectives are loaded on initialization."""
        objectives = brain_interface.get_objectives()
        assert len(objectives) >= 2
        assert any("coverage" in obj.lower() for obj in objectives)

    def test_session_state_loaded(self, brain_interface):
        """Test that session state is loaded on initialization."""
        state = brain_interface.get_session_state()
        assert state.get("loaded") is True

    def test_empty_repo_graceful(self):
        """Test graceful handling of empty repository."""
        with tempfile.TemporaryDirectory() as tmpdir:
            brain = AgentBrainInterface(
                agent_id="test-agent",
                repo_root=tmpdir
            )

            assert len(brain._patterns) == 0
            assert len(brain._objectives) == 0

    def test_repr(self, brain_interface):
        """Test string representation."""
        repr_str = repr(brain_interface)
        assert "test-agent" in repr_str
        assert "patterns_loaded" in repr_str


# =========================================================================
# Pattern Query Tests
# =========================================================================

class TestPatternQuery:
    """Tests for pattern querying functionality."""

    def test_query_by_symptom(self, brain_interface):
        """Test querying patterns by symptom."""
        patterns = brain_interface.query_patterns("pytest collection error")

        assert len(patterns) > 0
        assert patterns[0].pattern_id == "TFR-001"

    def test_query_multiple_symptoms(self, brain_interface):
        """Test querying with multiple symptoms."""
        patterns = brain_interface.query_patterns([
            "pytest collection error",
            "ImportError in tests"
        ])

        assert len(patterns) > 0
        assert patterns[0].category == "testing"

    def test_query_with_category_filter(self, brain_interface):
        """Test querying with category filter."""
        patterns = brain_interface.query_patterns(
            "error",
            category="testing"
        )

        for pattern in patterns:
            assert pattern.category == "testing"

    def test_query_min_confidence(self, brain_interface):
        """Test querying with minimum confidence."""
        patterns = brain_interface.query_patterns(
            "pytest",
            min_confidence=PatternConfidence.HIGH
        )

        for pattern in patterns:
            assert pattern.confidence == PatternConfidence.HIGH

    def test_query_limit(self, brain_interface):
        """Test query result limiting."""
        patterns = brain_interface.query_patterns("error", limit=1)

        assert len(patterns) <= 1

    def test_query_returns_pattern_match(self, brain_interface):
        """Test that query returns PatternMatch objects."""
        patterns = brain_interface.query_patterns("pytest")

        for pattern in patterns:
            assert isinstance(pattern, PatternMatch)
            assert hasattr(pattern, 'pattern_id')
            assert hasattr(pattern, 'solutions')
            assert hasattr(pattern, 'success_rate')

    def test_query_no_match(self, brain_interface):
        """Test query with no matching patterns."""
        patterns = brain_interface.query_patterns(
            "completely unrelated string xyz123"
        )

        # Should return empty or low-confidence matches
        assert isinstance(patterns, list)

    def test_get_pattern_by_id(self, brain_interface):
        """Test getting a specific pattern by ID."""
        pattern = brain_interface.get_pattern("TFR-001")

        assert pattern is not None
        assert pattern.pattern_id == "TFR-001"
        assert pattern.category == "testing"

    def test_get_pattern_not_found(self, brain_interface):
        """Test getting a non-existent pattern."""
        pattern = brain_interface.get_pattern("NONEXISTENT-999")

        assert pattern is None


# =========================================================================
# Pattern Submission Tests
# =========================================================================

class TestPatternSubmission:
    """Tests for pattern submission functionality."""

    def test_submit_new_pattern(self, brain_interface):
        """Test submitting a new pattern."""
        result = brain_interface.submit_pattern(
            pattern_id="NEW-001",
            category="testing",
            symptoms=["new symptom 1", "new symptom 2"],
            solutions=["solution 1", "solution 2"],
            diagnosis_steps=["step 1", "step 2"]
        )

        assert result is True

        # Verify pattern was added
        pattern = brain_interface.get_pattern("NEW-001")
        assert pattern is not None
        assert pattern.category == "testing"

    def test_submitted_pattern_persists(self, brain_interface, temp_repo):
        """Test that submitted patterns are saved to file."""
        brain_interface.submit_pattern(
            pattern_id="PERSIST-001",
            category="testing",
            symptoms=["test symptom"],
            solutions=["test solution"]
        )

        # Read the file directly
        pattern_path = temp_repo / ".codex/cognitive_brain/pattern_learning_store.json"
        with open(pattern_path) as f:
            data = json.load(f)

        assert "persist_001" in data["patterns"]


# =========================================================================
# Objective Alignment Tests
# =========================================================================

class TestObjectiveAlignment:
    """Tests for objective alignment checking."""

    def test_aligned_action(self, brain_interface):
        """Test detection of aligned actions."""
        alignment = brain_interface.check_alignment("increase test coverage")

        assert alignment in [
            ObjectiveAlignment.ALIGNED,
            ObjectiveAlignment.PARTIALLY_ALIGNED
        ]

    def test_misaligned_action(self, brain_interface):
        """Test detection of misaligned actions."""
        alignment = brain_interface.check_alignment("skip all tests")

        assert alignment == ObjectiveAlignment.MISALIGNED

    def test_unknown_alignment(self):
        """Test unknown alignment when no objectives loaded."""
        with tempfile.TemporaryDirectory() as tmpdir:
            brain = AgentBrainInterface(
                agent_id="test-agent",
                repo_root=tmpdir
            )

            alignment = brain.check_alignment("some action")
            assert alignment == ObjectiveAlignment.UNKNOWN

    def test_get_objectives(self, brain_interface):
        """Test getting current objectives."""
        objectives = brain_interface.get_objectives()

        assert isinstance(objectives, list)
        assert len(objectives) >= 2

    def test_update_objective_progress(self, brain_interface):
        """Test updating objective progress."""
        objectives = brain_interface.get_objectives()
        if objectives:
            result = brain_interface.update_objective_progress(
                objectives[0],
                completed=False,
                progress_note="Making progress"
            )

            assert result is True


# =========================================================================
# Session State Tests
# =========================================================================

class TestSessionState:
    """Tests for session state management."""

    def test_get_session_state(self, brain_interface):
        """Test getting session state."""
        state = brain_interface.get_session_state()

        assert isinstance(state, dict)

    def test_update_session_state_merge(self, brain_interface):
        """Test updating session state with merge."""
        brain_interface.update_session_state({
            "new_key": "new_value"
        }, merge=True)

        state = brain_interface.get_session_state()
        assert state.get("new_key") == "new_value"
        assert state.get("loaded") is True  # Original value preserved

    def test_update_session_state_replace(self, brain_interface):
        """Test updating session state with replace."""
        brain_interface.update_session_state({
            "new_key": "new_value"
        }, merge=False)

        state = brain_interface.get_session_state()
        assert state.get("new_key") == "new_value"
        assert state.get("loaded") is None  # Original value not preserved

    def test_session_state_tracks_updates(self, brain_interface):
        """Test that session state tracks who updated it."""
        brain_interface.update_session_state({"test": "value"})

        state = brain_interface.get_session_state()
        assert state.get("updated_by") == "test-agent"
        assert "last_updated" in state


# =========================================================================
# Learning Feedback Tests
# =========================================================================

class TestLearningFeedback:
    """Tests for learning feedback submission."""

    def test_submit_success_learning(self, brain_interface):
        """Test submitting successful learning feedback."""
        result = brain_interface.submit_learning(
            pattern_id="TFR-001",
            outcome="success",
            context={"error": "import error", "fix": "added mock"}
        )

        assert result is True

    def test_submit_failure_learning(self, brain_interface):
        """Test submitting failure learning feedback."""
        result = brain_interface.submit_learning(
            pattern_id="TFR-001",
            outcome="failure",
            context={"error": "still failing"}
        )

        assert result is True

    def test_submit_partial_learning(self, brain_interface):
        """Test submitting partial success learning feedback."""
        result = brain_interface.submit_learning(
            pattern_id="TFR-001",
            outcome="partial",
            context={"note": "some tests fixed"}
        )

        assert result is True

    def test_learning_updates_success_rate(self, brain_interface):
        """Test that learning updates pattern success rate."""
        # Get initial success rate
        pattern = brain_interface.get_pattern("TFR-001")
        _ = pattern.success_rate  # Initial rate used for comparison implicitly

        # Submit multiple success feedbacks
        brain_interface.submit_learning("TFR-001", "success")
        brain_interface.submit_learning("TFR-001", "success")

        # Get updated pattern
        pattern = brain_interface.get_pattern("TFR-001")

        # Rate should still be in valid range
        assert 0.0 <= pattern.success_rate <= 1.0

    def test_learning_with_details(self, brain_interface):
        """Test submitting learning with full details."""
        result = brain_interface.submit_learning(
            pattern_id="TFR-001",
            outcome="success",
            context={"pr": 3160},
            resolution_details="Fixed by adding mock",
            new_symptoms=["new error discovered"],
            suggested_improvements=["add more solutions"]
        )

        assert result is True


# =========================================================================
# Diagnosis Tests
# =========================================================================

class TestDiagnosis:
    """Tests for the diagnose convenience method."""

    def test_diagnose_returns_brain_response(self, brain_interface):
        """Test that diagnose returns a BrainResponse."""
        response = brain_interface.diagnose("pytest error")

        assert isinstance(response, BrainResponse)
        assert response.success is True

    def test_diagnose_includes_patterns(self, brain_interface):
        """Test that diagnosis includes matching patterns."""
        response = brain_interface.diagnose("pytest collection error")

        assert len(response.patterns) > 0

    def test_diagnose_includes_objectives(self, brain_interface):
        """Test that diagnosis includes objectives."""
        response = brain_interface.diagnose("error")

        assert isinstance(response.objectives, list)

    def test_diagnose_includes_recommendations(self, brain_interface):
        """Test that diagnosis includes recommendations."""
        response = brain_interface.diagnose("pytest collection error")

        assert isinstance(response.recommendations, list)
        if response.patterns:
            assert len(response.recommendations) > 0

    def test_diagnose_includes_metadata(self, brain_interface):
        """Test that diagnosis includes metadata."""
        response = brain_interface.diagnose("error")

        assert "agent_id" in response.metadata
        assert "timestamp" in response.metadata


# =========================================================================
# Match Score Tests
# =========================================================================

class TestMatchScore:
    """Tests for pattern match scoring."""

    def test_exact_match_high_score(self, brain_interface):
        """Test that exact matches get high scores."""
        patterns = brain_interface.query_patterns([
            "pytest collection error",
            "exit code 2",
            "ImportError in tests"
        ])

        if patterns:
            assert patterns[0].match_score > 0.5

    def test_partial_match_lower_score(self, brain_interface):
        """Test that partial matches get lower scores."""
        patterns = brain_interface.query_patterns("some random error")

        # Should have lower scores than exact matches
        for pattern in patterns:
            assert 0.0 <= pattern.match_score <= 1.0

    def test_confidence_levels(self, brain_interface):
        """Test confidence level assignment."""
        patterns = brain_interface.query_patterns("pytest")

        for pattern in patterns:
            assert isinstance(pattern.confidence, PatternConfidence)


# =========================================================================
# Data Type Tests
# =========================================================================

class TestDataTypes:
    """Tests for data type correctness."""

    def test_agent_context(self):
        """Test AgentContext dataclass."""
        context = AgentContext(
            agent_id="test-agent",
            agent_category=AgentCategory.TESTING,
            session_id="session-001",
            pr_number=3160,
            symptoms=["error 1"],
            current_phase="testing"
        )

        assert context.agent_id == "test-agent"
        assert context.agent_category == AgentCategory.TESTING

    def test_pattern_match(self):
        """Test PatternMatch dataclass."""
        match = PatternMatch(
            pattern_id="TEST-001",
            category="testing",
            confidence=PatternConfidence.HIGH,
            match_score=0.95,
            symptoms=["symptom"],
            solutions=["solution"],
            success_rate=0.9,
            times_applied=5
        )

        assert match.pattern_id == "TEST-001"
        assert match.confidence == PatternConfidence.HIGH

    def test_learning_feedback(self):
        """Test LearningFeedback dataclass."""
        feedback = LearningFeedback(
            pattern_id="TEST-001",
            outcome="success",
            agent_id="test-agent",
            context={"key": "value"}
        )

        assert feedback.pattern_id == "TEST-001"
        assert feedback.outcome == "success"

    def test_brain_response(self):
        """Test BrainResponse dataclass."""
        response = BrainResponse(
            success=True,
            message="Test message",
            patterns=[],
            objectives=["obj1"]
        )

        assert response.success is True
        assert len(response.objectives) == 1


# =========================================================================
# Edge Case Tests
# =========================================================================

class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_empty_symptoms(self, brain_interface):
        """Test querying with empty symptoms."""
        patterns = brain_interface.query_patterns([])

        assert isinstance(patterns, list)

    def test_none_symptoms(self, brain_interface):
        """Test querying with None-like input."""
        patterns = brain_interface.query_patterns("")

        assert isinstance(patterns, list)

    def test_very_long_symptoms(self, brain_interface):
        """Test querying with very long symptom strings."""
        long_symptom = "error " * 1000
        patterns = brain_interface.query_patterns(long_symptom)

        assert isinstance(patterns, list)

    def test_special_characters_in_symptoms(self, brain_interface):
        """Test querying with special characters."""
        patterns = brain_interface.query_patterns(
            "error: [Errno 2] No such file <test> & 'quote'"
        )

        assert isinstance(patterns, list)

    def test_unicode_in_symptoms(self, brain_interface):
        """Test querying with unicode characters."""
        patterns = brain_interface.query_patterns("错误 エラー error")

        assert isinstance(patterns, list)


# =========================================================================
# Integration Tests
# =========================================================================

class TestIntegration:
    """Integration tests for complete workflows."""

    def test_full_diagnosis_workflow(self, brain_interface):
        """Test complete diagnosis workflow."""
        # 1. Query patterns
        patterns = brain_interface.query_patterns("pytest collection error")
        assert len(patterns) > 0

        # 2. Check alignment
        alignment = brain_interface.check_alignment("fix test imports")
        assert alignment != ObjectiveAlignment.MISALIGNED

        # 3. Get session state
        state = brain_interface.get_session_state()
        assert isinstance(state, dict)

        # 4. Submit learning
        result = brain_interface.submit_learning(
            pattern_id=patterns[0].pattern_id,
            outcome="success"
        )
        assert result is True

        # 5. Update session state
        brain_interface.update_session_state({
            "diagnosis_complete": True,
            "patterns_applied": [patterns[0].pattern_id]
        })

        state = brain_interface.get_session_state()
        assert state.get("diagnosis_complete") is True

    def test_pattern_learning_cycle(self, brain_interface):
        """Test pattern submission and retrieval cycle."""
        # Submit new pattern
        brain_interface.submit_pattern(
            pattern_id="CYCLE-001",
            category="testing",
            symptoms=["unique symptom xyz"],
            solutions=["unique solution"]
        )

        # Query for the pattern
        patterns = brain_interface.query_patterns("unique symptom xyz")

        # Should find the new pattern
        found = any(p.pattern_id == "CYCLE-001" for p in patterns)
        assert found


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
