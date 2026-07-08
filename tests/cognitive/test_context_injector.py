#!/usr/bin/env python3
"""
Tests for Context Injection System - Phase 10.3 Days 4-5

Target: > 95% code coverage
Test Categories:
- Pattern retrieval and similarity matching
- Session context assembly
- Confidence scoring
- Multi-source context fusion
- Graceful degradation (timeout handling)
- Performance constraints (< 50ms total)
- Integration with OODA loop
"""

import asyncio
import time
from datetime import datetime, timedelta

import numpy as np
import pytest

from scripts.cognitive.context_injector import (
    ConfidenceMetrics,
    ContextFusionEngine,
    ContextInjector,
    ContextMetadata,
    MockPatternStore,
    MockSessionStore,
    PatternStore,
    SessionStore,
    VectorEncoder,
)


class TestVectorEncoder:
    """Test vector encoding of observations."""
    
    def test_encode_observation_returns_vector(self):
        """Test that observation encoding returns a vector."""
        encoder = VectorEncoder(vector_size=128)
        
        observation = {
            "task": {"type": "ci_fix", "priority": "P1"},
            "agent_state": {"queue_depth": 5, "performance": {"success_rate": 0.9}},
            "environment": {"ci_health": 0.85},
        }
        
        vector = encoder.encode_observation(observation)
        
        assert isinstance(vector, np.ndarray)
        assert len(vector) == 128
    
    def test_encode_observation_normalizes_to_unit_vector(self):
        """Test that encoded vector is normalized."""
        encoder = VectorEncoder(vector_size=128)
        
        observation = {
            "task": {"type": "ci_fix", "priority": "P1"},
            "agent_state": {"queue_depth": 5, "performance": {"success_rate": 0.9}},
            "environment": {"ci_health": 0.85},
        }
        
        vector = encoder.encode_observation(observation)
        norm = np.linalg.norm(vector)
        
        assert abs(norm - 1.0) < 0.01, f"Vector norm should be ~1.0, got {norm}"
    
    def test_encode_observation_reflects_task_type(self):
        """Test that different task types produce different vectors."""
        encoder = VectorEncoder(vector_size=128)
        
        obs_ci = {
            "task": {"type": "ci_fix", "priority": "P1"},
            "agent_state": {"queue_depth": 5, "performance": {"success_rate": 0.9}},
            "environment": {"ci_health": 0.85},
        }
        
        obs_ml = {
            "task": {"type": "ml_pattern", "priority": "P1"},
            "agent_state": {"queue_depth": 5, "performance": {"success_rate": 0.9}},
            "environment": {"ci_health": 0.85},
        }
        
        vec_ci = encoder.encode_observation(obs_ci)
        vec_ml = encoder.encode_observation(obs_ml)
        
        # Vectors should be different
        distance = np.linalg.norm(vec_ci - vec_ml)
        assert distance > 0.1, "Task type should affect vector representation"
    
    def test_encode_observation_reflects_priority(self):
        """Test that priority level affects vector."""
        encoder = VectorEncoder(vector_size=128)
        
        obs_p0 = {
            "task": {"type": "ci_fix", "priority": "P0"},
            "agent_state": {"queue_depth": 5, "performance": {"success_rate": 0.9}},
            "environment": {"ci_health": 0.85},
        }
        
        obs_p3 = {
            "task": {"type": "ci_fix", "priority": "P3"},
            "agent_state": {"queue_depth": 5, "performance": {"success_rate": 0.9}},
            "environment": {"ci_health": 0.85},
        }
        
        vec_p0 = encoder.encode_observation(obs_p0)
        vec_p3 = encoder.encode_observation(obs_p3)
        
        # Priority is encoded in specific dimension
        assert vec_p0[16] > vec_p3[16], "P0 should have higher priority score"


# ============================================================================
# Pattern Retrieval Tests
# ============================================================================

@pytest.mark.asyncio
async def test_get_patterns_retrieves_similar_patterns():
    """Test pattern retrieval from LTM."""
    pattern_store = MockPatternStore()
    injector = ContextInjector(pattern_store, MockSessionStore())
    
    observation = {
        "task": {"type": "ci_fix", "priority": "P1"},
        "agent_state": {"queue_depth": 5, "performance": {"success_rate": 0.9}},
        "environment": {"ci_health": 0.85},
    }
    
    patterns = await injector._get_patterns(observation, top_k=5)
    
    assert len(patterns) > 0
    assert all("similarity" in p for p in patterns)


@pytest.mark.asyncio
async def test_get_patterns_respects_top_k():
    """Test that pattern retrieval respects top_k limit."""
    
    class MultiPatternStore(PatternStore):
        async def search_similar(self, query_vector, top_k=5, min_similarity=0.5):
            return [
                {"pattern_id": f"pat_{i}", "similarity": 0.9 - i*0.1}
                for i in range(10)
            ]
        
        async def get_pattern(self, pattern_id):
            return None
        
        async def get_patterns_by_tag(self, tag, limit=10):
            return []
    
    injector = ContextInjector(MultiPatternStore(), MockSessionStore())
    
    observation = {
        "task": {"type": "ci_fix", "priority": "P1"},
        "agent_state": {"queue_depth": 5, "performance": {"success_rate": 0.9}},
        "environment": {"ci_health": 0.85},
    }
    
    patterns = await injector._get_patterns(observation, top_k=3)
    
    assert len(patterns) <= 3


@pytest.mark.asyncio
async def test_get_patterns_timeout_handling():
    """Test graceful handling of pattern retrieval timeout."""
    
    class SlowPatternStore(PatternStore):
        async def search_similar(self, query_vector, top_k=5, min_similarity=0.5):
            await asyncio.sleep(1)  # Simulate slow operation
            return []
        
        async def get_pattern(self, pattern_id):
            return None
        
        async def get_patterns_by_tag(self, tag, limit=10):
            return []
    
    injector = ContextInjector(SlowPatternStore(), MockSessionStore())
    
    observation = {
        "task": {"type": "ci_fix", "priority": "P1"},
        "agent_state": {"queue_depth": 5, "performance": {"success_rate": 0.9}},
        "environment": {"ci_health": 0.85},
    }
    
    # Should timeout gracefully
    patterns = await injector._get_patterns(observation, top_k=5)
    
    # Should return empty list on timeout
    assert patterns == []


# ============================================================================
# Session Retrieval Tests
# ============================================================================

@pytest.mark.asyncio
async def test_get_sessions_retrieves_successful_sessions():
    """Test session retrieval from checkpoint storage."""
    session_store = MockSessionStore()
    injector = ContextInjector(MockPatternStore(), session_store)
    
    observation = {
        "task": {"type": "ci_fix", "priority": "P1"},
        "agent_state": {"queue_depth": 5, "performance": {"success_rate": 0.9}},
        "environment": {"ci_health": 0.85},
    }
    
    sessions = await injector._get_sessions(observation, top_k=3)
    
    assert len(sessions) > 0
    assert all(s.get("success", False) for s in sessions)


@pytest.mark.asyncio
async def test_get_sessions_respects_top_k():
    """Test that session retrieval respects top_k limit."""
    
    class MultiSessionStore(SessionStore):
        async def get_sessions(self, task_type, limit=3, success_only=True, max_age_days=30):
            return [
                {
                    "session_id": f"sess_{i}",
                    "created_at": (datetime.now() - timedelta(hours=i)).isoformat(),
                    "success": True,
                }
                for i in range(10)
            ]
        
        async def get_decision_history(self, task_type, limit=10):
            return []
    
    injector = ContextInjector(MockPatternStore(), MultiSessionStore())
    
    observation = {
        "task": {"type": "ci_fix", "priority": "P1"},
        "agent_state": {"queue_depth": 5, "performance": {"success_rate": 0.9}},
        "environment": {"ci_health": 0.85},
    }
    
    sessions = await injector._get_sessions(observation, top_k=2)
    
    assert len(sessions) <= 2


@pytest.mark.asyncio
async def test_get_sessions_timeout_handling():
    """Test graceful handling of session retrieval timeout."""
    
    class SlowSessionStore(SessionStore):
        async def get_sessions(self, task_type, limit=3, success_only=True, max_age_days=30):
            await asyncio.sleep(1)  # Simulate slow operation
            return []
        
        async def get_decision_history(self, task_type, limit=10):
            return []
    
    injector = ContextInjector(MockPatternStore(), SlowSessionStore())
    
    observation = {
        "task": {"type": "ci_fix", "priority": "P1"},
        "agent_state": {"queue_depth": 5, "performance": {"success_rate": 0.9}},
        "environment": {"ci_health": 0.85},
    }
    
    # Should timeout gracefully
    sessions = await injector._get_sessions(observation, top_k=3)
    
    # Should return empty list on timeout
    assert sessions == []


# ============================================================================
# Context Injection Tests
# ============================================================================

@pytest.mark.asyncio
async def test_inject_context_full_context():
    """Test complete context injection with all sources."""
    injector = ContextInjector(MockPatternStore(), MockSessionStore())
    
    observation = {
        "task": {"type": "ci_fix", "priority": "P1"},
        "agent_state": {"queue_depth": 5, "performance": {"success_rate": 0.9}},
        "environment": {"ci_health": 0.85},
    }
    
    context, confidence, metadata = await injector.inject_context(observation)
    
    assert context is not None
    assert "patterns" in context
    assert "sessions" in context
    assert "external" in context
    assert isinstance(confidence, ConfidenceMetrics)
    assert isinstance(metadata, ContextMetadata)


@pytest.mark.asyncio
async def test_inject_context_respects_timeout():
    """Test that context injection respects timeout."""
    
    class SlowContextInjector(ContextInjector):
        async def _get_patterns(self, observation, top_k):
            await asyncio.sleep(0.1)  # 100ms
            return []
    
    injector = SlowContextInjector(MockPatternStore(), MockSessionStore())
    
    observation = {
        "task": {"type": "ci_fix", "priority": "P1"},
        "agent_state": {"queue_depth": 5, "performance": {"success_rate": 0.9}},
        "environment": {"ci_health": 0.85},
    }
    
    start_time = time.time()
    context, confidence, metadata = await injector.inject_context(
        observation,
        timeout_ms=50,  # 50ms timeout
    )
    elapsed_ms = (time.time() - start_time) * 1000
    
    # Should return within reasonable time (allowing some overhead)
    assert elapsed_ms < 200, f"Context injection took {elapsed_ms:.1f}ms"


@pytest.mark.asyncio
async def test_inject_context_overhead():
    """Test that context injection overhead is < 5% of cycle time."""
    injector = ContextInjector(MockPatternStore(), MockSessionStore())
    
    observation = {
        "task": {"type": "ci_fix", "priority": "P1"},
        "agent_state": {"queue_depth": 5, "performance": {"success_rate": 0.9}},
        "environment": {"ci_health": 0.85},
    }
    
    # Measure context injection time
    start_time = time.time()
    context, confidence, metadata = await injector.inject_context(observation)
    injection_ms = (time.time() - start_time) * 1000
    
    # 5% of 200ms cycle time = 10ms
    assert injection_ms < 10, f"Context injection took {injection_ms:.1f}ms (should be < 10ms)"


# ============================================================================
# Confidence Scoring Tests
# ============================================================================

def test_calculate_confidence_full_context():
    """Test confidence calculation with full context."""
    injector = ContextInjector(MockPatternStore(), MockSessionStore())
    
    context = {
        "patterns": [
            {"pattern_id": "pat_001", "similarity": 0.92, "success_rate": 0.88, "sample_size": 150}
        ],
        "sessions": [
            {"session_id": "sess_001", "created_at": datetime.now().isoformat(), "success": True}
        ],
        "external": {"ci_health": 0.85},
    }
    
    observation = {
        "task": {"type": "ci_fix", "priority": "P1"},
    }
    
    confidence = injector._calculate_confidence(context, observation)
    
    assert confidence.overall_confidence > 0.5
    assert confidence.pattern_similarity_score > 0
    assert confidence.session_recency_score > 0
    assert confidence.external_reliability > 0


def test_calculate_confidence_patterns_only():
    """Test confidence calculation with patterns only."""
    injector = ContextInjector(MockPatternStore(), MockSessionStore())
    
    context = {
        "patterns": [
            {"pattern_id": "pat_001", "similarity": 0.92, "success_rate": 0.88, "sample_size": 150}
        ],
        "sessions": [],
        "external": {},
    }
    
    observation = {"task": {"type": "ci_fix", "priority": "P1"}}
    
    confidence = injector._calculate_confidence(context, observation)
    
    assert confidence.overall_confidence > 0
    assert confidence.pattern_similarity_score > 0
    assert confidence.session_recency_score == 0


def test_calculate_confidence_empty_context():
    """Test confidence calculation with no context."""
    injector = ContextInjector(MockPatternStore(), MockSessionStore())
    
    context = {
        "patterns": [],
        "sessions": [],
        "external": {},
    }
    
    observation = {"task": {"type": "ci_fix", "priority": "P1"}}
    
    confidence = injector._calculate_confidence(context, observation)
    
    # Should still return valid confidence (0.0 in this case)
    assert confidence.overall_confidence == 0.0


def test_confidence_metrics_breakdown():
    """Test that confidence metrics include breakdown."""
    injector = ContextInjector(MockPatternStore(), MockSessionStore())
    
    context = {
        "patterns": [
            {"pattern_id": "pat_001", "similarity": 0.92, "success_rate": 0.88, "sample_size": 150}
        ],
        "sessions": [
            {"session_id": "sess_001", "created_at": datetime.now().isoformat(), "success": True}
        ],
        "external": {},
    }
    
    observation = {"task": {"type": "ci_fix", "priority": "P1"}}
    
    confidence = injector._calculate_confidence(context, observation)
    
    assert "breakdown" in confidence.__dict__
    assert isinstance(confidence.breakdown, dict)
    assert len(confidence.breakdown) > 0


# ============================================================================
# Context Fusion Tests
# ============================================================================

def test_fuse_patterns_sorts_by_score():
    """Test that pattern fusion sorts by combined score."""
    patterns = [
        {"pattern_id": "pat_001", "similarity": 0.7, "success_rate": 0.7, "sample_size": 10},
        {"pattern_id": "pat_002", "similarity": 0.9, "success_rate": 0.9, "sample_size": 100},
        {"pattern_id": "pat_003", "similarity": 0.8, "success_rate": 0.8, "sample_size": 50},
    ]
    
    fused = ContextFusionEngine.fuse_patterns(patterns, top_k=3)
    
    # Should be sorted with highest scores first
    assert fused[0]["pattern_id"] == "pat_002"


def test_fuse_patterns_respects_top_k():
    """Test that pattern fusion respects top_k limit."""
    patterns = [
        {"pattern_id": f"pat_{i}", "similarity": 0.9, "success_rate": 0.8, "sample_size": 50}
        for i in range(10)
    ]
    
    fused = ContextFusionEngine.fuse_patterns(patterns, top_k=3)
    
    assert len(fused) == 3


def test_fuse_sessions_filters_successful():
    """Test that session fusion filters for successful sessions."""
    sessions = [
        {"session_id": "sess_001", "created_at": datetime.now().isoformat(), "success": True},
        {"session_id": "sess_002", "created_at": datetime.now().isoformat(), "success": False},
        {"session_id": "sess_003", "created_at": datetime.now().isoformat(), "success": True},
    ]
    
    fused = ContextFusionEngine.fuse_sessions(sessions, top_k=3)
    
    # Should only include successful sessions
    assert all(s.get("success") for s in fused)
    assert len(fused) == 2


def test_fuse_sessions_respects_top_k():
    """Test that session fusion respects top_k limit."""
    sessions = [
        {"session_id": f"sess_{i}", "created_at": datetime.now().isoformat(), "success": True}
        for i in range(10)
    ]
    
    fused = ContextFusionEngine.fuse_sessions(sessions, top_k=2)
    
    assert len(fused) <= 2


# ============================================================================
# Metrics Tests
# ============================================================================

@pytest.mark.asyncio
async def test_metrics_aggregation():
    """Test that metrics are correctly aggregated."""
    injector = ContextInjector(MockPatternStore(), MockSessionStore())
    
    observation = {
        "task": {"type": "ci_fix", "priority": "P1"},
        "agent_state": {"queue_depth": 5, "performance": {"success_rate": 0.9}},
        "environment": {"ci_health": 0.85},
    }
    
    # Execute multiple injections
    for _ in range(5):
        await injector.inject_context(observation)
    
    metrics = injector.get_metrics()
    
    assert metrics["total_context_requests"] == 5
    assert "avg_confidence" in metrics
    assert "median_confidence" in metrics
    assert "p99_confidence" in metrics


# ============================================================================
# Integration Tests
# ============================================================================

@pytest.mark.asyncio
async def test_context_injector_with_executor_integration():
    """Test context injector integration with OODA executor."""
    from scripts.cognitive.ooda_loop_executor import OODAExecutor, StateProvider
    
    class TestStateProvider(StateProvider):
        def get_repo_state(self):
            return {"branch": "main"}
        
        def get_agent_state(self):
            return {"health": 0.9, "queue_depth": 5}
        
        def get_environment_state(self):
            return {"ci_health": 0.85}
        
        def get_task_context(self, task_id):
            return {"id": task_id, "priority": "P1"}
    
    # Create context provider from injector
    injector = ContextInjector(MockPatternStore(), MockSessionStore())
    
    class TestContextProvider:
        async def get_patterns(self, observation, top_k=5):
            context, _, _ = await injector.inject_context(observation, top_k_patterns=top_k)
            return context.get("patterns", [])
        
        async def get_sessions(self, task_type, limit=3):
            observation = {"task": {"type": task_type}}
            context, _, _ = await injector.inject_context(observation, top_k_sessions=limit)
            return context.get("sessions", [])
        
        async def get_external_context(self):
            return {}
    
    executor = OODAExecutor(
        state_provider=TestStateProvider(),
        context_provider=TestContextProvider(),
    )
    
    # Execute cycle should use context injection
    state = await executor.execute_cycle("task_001", "ci_fix", "P1")
    
    assert state is not None
    assert state.orientation is not None
    assert state.decision is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
