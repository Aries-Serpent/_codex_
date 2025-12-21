"""Test suite for Codex Quantum Reviewer."""

from __future__ import annotations

from pathlib import Path
import sys

import pytest

# Add parent directory to path for imports
AGENTS_DIR = Path(__file__).resolve().parents[1]
if str(AGENTS_DIR) not in sys.path:
    sys.path.append(str(AGENTS_DIR))

from codex_reviewer.main import (  # noqa: E402
    CodexQuantumReviewer,
    ReviewContext,
    ReviewResult,
)
from codex_reviewer.analyzers import QuantumPatternAnalyzer  # noqa: E402
from codex_reviewer.orchestration import WorkflowOrchestrator  # noqa: E402


@pytest.fixture
def mock_context() -> ReviewContext:
    """Create mock review context."""
    return ReviewContext(
        pr_number=123,
        repo="Aries-Serpent/_codex_",
        files_changed=["quantum_logic.py", "security_scanner.py"],
        diff="+ def new_function():\n+     pass",
        base_branch="main",
        head_branch="feature/test",
        author="testuser",
        description="Test PR",
        labels=[],
        reviewers=[]
    )


class TestCodexReviewer:
    """Test reviewer functionality."""

    @pytest.mark.asyncio
    async def test_initial_review(self, mock_context: ReviewContext) -> None:
        """Test initial PR review."""
        reviewer = CodexQuantumReviewer()

        event = {
            "action": "initial_review",
            "context": mock_context,
        }

        result = await reviewer.handle_event(event)

        assert result["status"] == "review_complete"
        assert result["pr_number"] == 123
        assert "confidence" in result

    @pytest.mark.asyncio
    async def test_quantum_pattern_detection(self, mock_context: ReviewContext) -> None:
        """Test quantum pattern analysis."""
        analyzer = QuantumPatternAnalyzer()

        patterns = await analyzer.analyze(mock_context)

        assert isinstance(patterns, list)
        for pattern in patterns:
            assert "type" in pattern
            assert "description" in pattern

    @pytest.mark.asyncio
    async def test_orchestration_plan(self, mock_context: ReviewContext) -> None:
        """Test workflow orchestration."""
        orchestrator = WorkflowOrchestrator()

        review_result = ReviewResult(
            status="changes_requested",
            confidence=0.85,
            suggestions=[
                {"category": "security", "severity": "high"},
                {"category": "code_quality", "severity": "medium"},
            ],
            orchestration_plan={},
            next_steps=[],
            knowledge_gaps=[],
        )

        plan = await orchestrator.create_plan(mock_context, review_result)

        assert "steps" in plan
        assert len(plan["steps"]) > 0
        assert "priority" in plan
        assert plan["priority"] in ["low", "medium", "high", "critical"]

    @pytest.mark.asyncio
    async def test_review_formatting(self) -> None:
        """Test review comment formatting."""
        reviewer = CodexQuantumReviewer()

        result = ReviewResult(
            status="approved",
            confidence=0.96,
            suggestions=[],
            orchestration_plan={"steps": []},
            next_steps=["Deploy to staging"],
            knowledge_gaps=[],
        )

        body = reviewer._format_review_body(result)

        assert "Codex Quantum Review" in body
        assert "96.0%" in body
        assert "Deploy to staging" in body
        assert "Codex Quantum Reviewer" in body
