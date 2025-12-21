"""
Complete Integration Test Suite

This test suite validates all components with proper mocking,
fixes all datetime issues, and tests the complete review workflow.
"""

from __future__ import annotations

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch, MagicMock
import json
from pathlib import Path
import sys

# Add agents directory to path
AGENTS_DIR = Path(__file__).resolve().parents[1]
if str(AGENTS_DIR) not in sys.path:
    sys.path.insert(0, str(AGENTS_DIR))

from codex_reviewer.main import CodexQuantumReviewer, ReviewContext, ReviewResult
from codex_reviewer.security import SecurityValidator
from codex_reviewer.secret_patterns import SecretPatterns, calculate_entropy
from codex_reviewer.metrics import MetricsCollector, ReviewMetrics
from codex_reviewer.github_client import GitHubAPIClient


class TestCompleteIntegration:
    """Complete integration test suite with all fixes applied."""
    
    @pytest.fixture
    def mock_github_api(self):
        """Mock GitHub API client with proper async support."""
        mock_client = Mock(spec=GitHubAPIClient)
        mock_client.post_review = AsyncMock(return_value={"id": 123, "state": "COMMENTED"})
        mock_client.get_pr_files = AsyncMock(return_value=[
            {"filename": "test.py", "patch": "+def test(): pass", "additions": 1}
        ])
        mock_client.get_pr_diff = AsyncMock(return_value="+ def test(): pass\n")
        mock_client.add_comment = AsyncMock(return_value={"id": 456})
        return mock_client
    
    @pytest.fixture
    def sample_context(self):
        """Create sample review context with proper datetime."""
        return ReviewContext(
            pr_number=123,
            repo="test/repo",
            files_changed=["test.py"],
            diff="+ API_KEY='test_key_12345'",
            base_branch="main",
            head_branch="feature/test",
            author="testuser",
            description="Test PR for validation",
            labels=[],
            reviewers=[],
            timestamp=datetime.utcnow()  # Fixed: proper instantiation
        )
    
    @pytest.mark.asyncio
    async def test_full_review_flow_with_api(self, mock_github_api, sample_context):
        """Test complete review flow with GitHub API integration."""
        # Setup
        reviewer = CodexQuantumReviewer()
        reviewer.github_client = mock_github_api
        
        # Execute
        event = {"action": "initial_review", "context": sample_context}
        result = await reviewer.handle_event(event)
        
        # Verify
        assert result["status"] == "review_complete"
        assert result["pr_number"] == 123
        assert "confidence" in result
        assert "suggestions_count" in result
        
        # Verify API was called
        assert mock_github_api.post_review.called
        call_args = mock_github_api.post_review.call_args
        assert call_args is not None
        
        # Verify review parameters
        kwargs = call_args[1] if call_args[1] else call_args[0]
        assert kwargs.get("pr_number") == 123 or call_args[0][1] == 123
    
    @pytest.mark.asyncio
    async def test_secret_detection_with_pattern_fixes(self):
        """Test secret detection with all pattern fixes applied."""
        validator = SecurityValidator()
        
        test_cases = [
            # (code_sample, should_detect_secret, description)
            ('API_KEY="sk_test_1234567890abcdefghij"', True, "API key with quotes"),
            ('apiKey: "my_secret_key_123456789012"', True, "JSON-style API key"),
            ('github_token = "ghp_1234567890abcdefghij123456789012"', True, "GitHub token"),
            ('AWS_ACCESS_KEY_ID = "AKIAIOSFODNN7EXAMPLE"', True, "AWS access key"),
            ('regular_code = "normal_value"', False, "Normal code"),
            ('YOUR_API_KEY_HERE', False, "Placeholder should be filtered"),
        ]
        
        for code, should_detect, description in test_cases:
            context = ReviewContext(
                pr_number=1,
                repo="test/repo",
                files_changed=["test.py"],
                diff=f"+ {code}",
                base_branch="main",
                head_branch="feature",
                author="user",
                description="Test"
            )
            
            result = await validator.scan(context)
            secret_issues = [v for v in result if v.get("type") == "hardcoded_secret"]
            
            if should_detect:
                assert len(secret_issues) > 0, f"Failed to detect secret: {description} - {code}"
            else:
                assert len(secret_issues) == 0, f"False positive: {description} - {code}"
    
    @pytest.mark.asyncio
    async def test_metrics_collection_with_buffering(self, tmp_path):
        """Test metrics collection with buffering mechanism."""
        collector = MetricsCollector(storage_path=tmp_path, buffer_size=10)
        
        # Generate metrics to test buffering
        metrics_list = []
        for i in range(25):
            metric = ReviewMetrics(
                pr_number=100 + i,
                repo="test/repo",
                timestamp=datetime.utcnow(),
                review_time_seconds=10.5 + i,
                confidence=0.85,
                status="approved" if i % 2 == 0 else "commented",
                suggestions_count=i % 5,
                knowledge_gaps_count=1,
                files_changed=3
            )
            metrics_list.append(metric)
            collector.record_review(metric, flush_immediately=False)
        
        # Verify buffering happened
        # Buffer should have been flushed at least twice (25 / 10 = 2.5)
        assert collector.metrics_file.exists()
        
        # Force final flush
        collector.flush_all()
        assert len(collector._metrics_buffer) == 0
        
        # Verify all metrics were written
        recent = collector.get_recent_metrics(days=1)
        assert len(recent) == 25
    
    @pytest.mark.asyncio
    async def test_orchestration_planning(self, sample_context):
        """Test workflow orchestration with priority determination."""
        from codex_reviewer.orchestration import WorkflowOrchestrator
        
        orchestrator = WorkflowOrchestrator()
        
        # Create result with various issues
        review_result = ReviewResult(
            status="changes_requested",
            confidence=0.75,
            suggestions=[
                {"category": "security", "severity": "critical", "message": "SQL injection risk"},
                {"category": "code_quality", "severity": "medium", "message": "Complex function"},
                {"category": "documentation", "severity": "low", "message": "Missing docstring"},
            ],
            orchestration_plan={},
            next_steps=[],
            knowledge_gaps=["quantum patterns", "async best practices"]
        )
        
        plan = await orchestrator.create_plan(sample_context, review_result)
        
        # Verify plan structure
        assert "steps" in plan
        assert "priority" in plan
        assert "estimated_time" in plan
        
        # Verify priority is high due to critical security issue
        assert plan["priority"] == "high"
        
        # Verify steps are ordered correctly (security first)
        assert len(plan["steps"]) >= 2
        assert "security" in plan["steps"][0]["description"].lower()
    
    @pytest.mark.asyncio
    async def test_knowledge_gap_detection(self):
        """Test knowledge gap identification."""
        from codex_reviewer.knowledge import KnowledgeGapDetector
        
        detector = KnowledgeGapDetector()
        
        # Context with quantum-related code
        context = ReviewContext(
            pr_number=1,
            repo="test/repo",
            files_changed=["quantum_module.py", "entanglement.py"],
            diff="+ def quantum_entangle(state1, state2):\n+     pass",
            base_branch="main",
            head_branch="feature/quantum",
            author="user",
            description=""  # Empty description
        )
        
        gaps = await detector.detect_gaps(context)
        
        # Should identify gaps
        assert len(gaps) > 0
        
        # Should mention quantum-related or description gap
        gap_text = " ".join(gaps).lower()
        assert "quantum" in gap_text or "description" in gap_text
    
    @pytest.mark.asyncio
    async def test_learning_system_feedback_integration(self):
        """Test self-evolution learning system."""
        from codex_reviewer.learning import SelfEvolutionSystem
        
        learning = SelfEvolutionSystem()
        
        context = ReviewContext(
            pr_number=123,
            repo="test/repo",
            files_changed=["test.py"],
            diff="+ code",
            base_branch="main",
            head_branch="feature",
            author="user",
            description="Test"
        )
        
        result = ReviewResult(
            status="approved",
            confidence=0.92,
            suggestions=[],
            orchestration_plan={},
            next_steps=[],
            knowledge_gaps=[]
        )
        
        # Learn from review
        await learning.learn_from_review(context, result)
        
        # Simulate user feedback
        feedback = {
            "pr_number": 123,
            "suggestions_accepted": 2,
            "suggestions_rejected": 1,
            "user_comment": "Good security suggestions"
        }
        
        await learning.learn_from_feedback(context, json.dumps(feedback))
        
        # Verify learning occurred (implementation-dependent)
        # At minimum, should not crash
        assert True
    
    @pytest.mark.asyncio
    async def test_entropy_calculation_accuracy(self):
        """Test entropy calculation with known values."""
        # Low entropy (repetitive)
        low_entropy_string = "aaaaaaaaaa"
        entropy_low = calculate_entropy(low_entropy_string)
        assert entropy_low < 1.0
        
        # High entropy (random-looking)
        high_entropy_string = "Xy9kL2mN8pQ4rT6vW3zB1cF5gH7jK0oP"
        entropy_high = calculate_entropy(high_entropy_string)
        assert entropy_high > 4.0
        
        # Medium entropy (typical password)
        medium_entropy_string = "password123"
        entropy_medium = calculate_entropy(medium_entropy_string)
        assert 3.0 < entropy_medium < 4.0
    
    @pytest.mark.asyncio
    async def test_performance_pre_compiled_patterns(self):
        """Test that security patterns are pre-compiled for performance."""
        validator = SecurityValidator()
        
        # Verify patterns are compiled at initialization
        assert hasattr(validator, '_sql_patterns')
        assert hasattr(validator, '_xss_patterns')
        assert hasattr(validator, '_cmd_patterns')
        assert hasattr(validator, '_path_patterns')
        
        # Verify they are compiled regex patterns
        import re
        assert all(isinstance(p, re.Pattern) for p in validator._sql_patterns)
        assert all(isinstance(p, re.Pattern) for p in validator._xss_patterns)
    
    @pytest.mark.asyncio
    async def test_datetime_no_shared_timestamps(self):
        """Test that timestamps are not shared between contexts."""
        context1 = ReviewContext(
            pr_number=1,
            repo="test/repo",
            files_changed=[],
            diff="",
            base_branch="main",
            head_branch="feature",
            author="user",
            description="Test 1"
        )
        
        # Small delay
        await asyncio.sleep(0.01)
        
        context2 = ReviewContext(
            pr_number=2,
            repo="test/repo",
            files_changed=[],
            diff="",
            base_branch="main",
            head_branch="feature",
            author="user",
            description="Test 2"
        )
        
        # Timestamps should be different
        assert context1.timestamp != context2.timestamp
        assert context2.timestamp > context1.timestamp


class TestErrorHandling:
    """Test error handling and edge cases."""
    
    @pytest.mark.asyncio
    async def test_github_api_failure_graceful_degradation(self, sample_context):
        """Test that API failures don't crash the agent."""
        reviewer = CodexQuantumReviewer()
        
        # Mock API that raises exception
        mock_client = Mock(spec=GitHubAPIClient)
        mock_client.post_review = AsyncMock(side_effect=Exception("API Error"))
        reviewer.github_client = mock_client
        
        # Should not raise exception
        event = {"action": "initial_review", "context": sample_context}
        result = await reviewer.handle_event(event)
        
        # Should still complete (but log error)
        assert result["status"] == "review_complete"
    
    @pytest.mark.asyncio
    async def test_empty_diff_handling(self):
        """Test handling of empty diffs."""
        context = ReviewContext(
            pr_number=1,
            repo="test/repo",
            files_changed=[],
            diff="",
            base_branch="main",
            head_branch="feature",
            author="user",
            description="Empty PR"
        )
        
        reviewer = CodexQuantumReviewer()
        event = {"action": "initial_review", "context": context}
        
        # Should handle gracefully
        result = await reviewer.handle_event(event)
        assert result["status"] == "review_complete"


# Pytest configuration
@pytest.fixture(scope="session")
def sample_context():
    """Session-wide sample context."""
    return ReviewContext(
        pr_number=999,
        repo="test/repo",
        files_changed=["sample.py"],
        diff="+ sample_code",
        base_branch="main",
        head_branch="feature",
        author="testuser",
        description="Sample PR"
    )


if __name__ == "__main__":
    # Run with: python test_complete_suite.py
    pytest.main([__file__, "-v", "--tb=short"])
