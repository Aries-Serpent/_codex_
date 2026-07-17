"""Test configuration and fixtures for cognitive brain tests."""

import asyncio

import pytest

from src.codex.cognitive_brain.calibration import ConfidenceCalibrator
from src.codex.cognitive_brain.knowledge_base import KnowledgeBase
from src.codex.cognitive_brain.reasoning_engine import (
    AgentContext,
    ReasoningEngine,
)


@pytest.fixture
def temp_dir(tmp_path):
    """Create temporary directory for test artifacts."""
    reasoning_dir = tmp_path / ".codex" / "reasoning"
    reasoning_dir.mkdir(parents=True, exist_ok=True)
    return tmp_path


@pytest.fixture
def calibrator(temp_dir):
    """Create test calibrator."""
    return ConfidenceCalibrator(
        storage_path=temp_dir / ".codex" / "reasoning" / "calibration.json"
    )


@pytest.fixture
def knowledge_base(temp_dir):
    """Create test knowledge base."""
    kb = KnowledgeBase(kb_path=temp_dir / ".codex" / "reasoning" / "kb.json")

    # Add test patterns
    kb.add_pattern(
        category="coverage",
        decision_type="coverage_increase",
        success_rate=0.92,
        frequency=150,
        tags=["coverage", "optimization"],
    )
    kb.add_pattern(
        category="performance",
        decision_type="latency_reduction",
        success_rate=0.88,
        frequency=120,
        tags=["performance", "optimization"],
    )
    kb.add_pattern(
        category="security",
        decision_type="vulnerability_patch",
        success_rate=0.95,
        frequency=45,
        tags=["security", "critical"],
    )

    return kb


@pytest.fixture
def reasoning_engine(knowledge_base):
    """Create test reasoning engine."""
    return ReasoningEngine(knowledge_base=knowledge_base)


@pytest.fixture
def sample_context():
    """Create sample agent context."""
    return AgentContext(
        goal="Increase test coverage while maintaining performance",
        constraints=[
            "coverage must increase by at least 5%",
            "no regression in p99 latency",
            "security constraints must be met",
        ],
        decision_history=[
            {
                "timestamp": "2026-07-14T10:00:00Z",
                "option": "add_unit_tests",
                "success": True,
                "coverage_delta": 3.2,
            },
            {
                "timestamp": "2026-07-14T10:15:00Z",
                "option": "add_integration_tests",
                "success": True,
                "coverage_delta": 2.1,
            },
        ],
        current_state={
            "coverage": 73.5,
            "p99_latency_ms": 245.0,
            "test_count": 850,
            "security_score": 8.7,
        },
        category="coverage",
    )


@pytest.fixture
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()
