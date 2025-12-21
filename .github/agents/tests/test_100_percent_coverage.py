"""
Comprehensive Test Suite for 100% Coverage

Tests all modules, edge cases, and integration scenarios.
"""

import pytest
import asyncio
from datetime import datetime
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from pathlib import Path
import sys

AGENTS_DIR = Path(__file__).resolve().parents[1]
if str(AGENTS_DIR) not in sys.path:
    sys.path.insert(0, str(AGENTS_DIR))

from codex_reviewer.main import CodexQuantumReviewer, ReviewContext, ReviewResult
from codex_reviewer.security import SecurityValidator
from codex_reviewer.secret_patterns import SecretPatterns, calculate_entropy, has_high_entropy
from codex_reviewer.analyzers import QuantumPatternAnalyzer
from codex_reviewer.orchestration import WorkflowOrchestrator
from codex_reviewer.knowledge import KnowledgeGapDetector
from codex_reviewer.learning import SelfEvolutionSystem
from codex_reviewer.metrics import MetricsCollector, ReviewMetrics
from codex_reviewer.github_client import GitHubAPIClient


class TestSecretPatternsComplete:
    """Complete coverage of secret pattern detection."""
    
    def test_all_pattern_types(self):
        """Test all 14+ secret pattern types."""
        patterns = SecretPatterns.PATTERNS
        
        # Verify all expected patterns exist
        expected = [
            'api_key', 'password', 'token', 'secret',
            'aws_access_key', 'aws_secret_key', 'github_token',
            'private_key', 'slack_token', 'stripe_key',
            'jwt', 'bearer_token'
        ]
        
        for pattern_name in expected:
            assert pattern_name in patterns, f"Missing pattern: {pattern_name}"
    
    def test_placeholder_patterns(self):
        """Test placeholder detection patterns."""
        placeholders = SecretPatterns.PLACEHOLDER_PATTERNS
        
        assert len(placeholders) > 0
        assert any('example' in p.lower() for p in placeholders)
        assert any('placeholder' in p.lower() for p in placeholders)
    
    def test_high_risk_files(self):
        """Test high-risk file detection."""
        high_risk = SecretPatterns.HIGH_RISK_FILES
        
        assert '.env' in high_risk
        assert 'id_rsa' in high_risk
        assert 'credentials' in high_risk
    
    def test_compiled_patterns(self):
        """Test pattern compilation."""
        compiled = SecretPatterns.get_compiled_patterns()
        
        assert len(compiled) > 10
        for name, pattern in compiled.items():
            assert hasattr(pattern, 'search')
            assert hasattr(pattern, 'match')
    
    def test_entropy_edge_cases(self):
        """Test entropy calculation edge cases."""
        assert calculate_entropy("") == 0.0
        assert calculate_entropy("a") == 0.0
        assert calculate_entropy("aa") == 0.0
        assert calculate_entropy("ab") > 0.0
        assert calculate_entropy("abcdefghij") > calculate_entropy("aaaaaaaaaa")
    
    def test_high_entropy_threshold(self):
        """Test high entropy detection with various thresholds."""
        random_string = "Xy9kL2mN8pQ4rT6vW3zB1cF5gH7jK0oP"
        
        assert has_high_entropy(random_string, threshold=4.0)
        assert has_high_entropy(random_string, threshold=4.5)
        assert not has_high_entropy("short", threshold=4.5)
        assert not has_high_entropy("a" * 30, threshold=4.5)


class TestSecurityValidatorComplete:
    """Complete coverage of security validator."""
    
    @pytest.mark.asyncio
    async def test_sql_injection_patterns(self):
        """Test SQL injection detection."""
        validator = SecurityValidator()
        
        test_cases = [
            "SELECT * FROM users WHERE id = " + str(1),
            "query = f'SELECT * FROM {table}'",
            "UNION SELECT password FROM users",
            "'; DROP TABLE users; --"
        ]
        
        for code in test_cases:
            context = ReviewContext(
                pr_number=1, repo="test/repo", files_changed=["test.py"],
                diff=code, base_branch="main", head_branch="feature",
                author="user", description="Test"
            )
            result = await validator.scan(context)
            sql_issues = [i for i in result if 'sql' in str(i).lower()]
            assert len(sql_issues) > 0, f"Failed to detect SQL injection in: {code}"
    
    @pytest.mark.asyncio
    async def test_xss_detection(self):
        """Test XSS vulnerability detection."""
        validator = SecurityValidator()
        
        xss_code = "<script>alert('xss')</script>"
        context = ReviewContext(
            pr_number=1, repo="test/repo", files_changed=["test.html"],
            diff=xss_code, base_branch="main", head_branch="feature",
            author="user", description="Test"
        )
        
        result = await validator.scan(context)
        xss_issues = [i for i in result if 'xss' in str(i).lower() or 'script' in str(i).lower()]
        assert len(xss_issues) > 0
    
    @pytest.mark.asyncio
    async def test_command_injection(self):
        """Test command injection detection."""
        validator = SecurityValidator()
        
        cmd_code = "os.system(user_input)"
        context = ReviewContext(
            pr_number=1, repo="test/repo", files_changed=["test.py"],
            diff=cmd_code, base_branch="main", head_branch="feature",
            author="user", description="Test"
        )
        
        result = await validator.scan(context)
        cmd_issues = [i for i in result if 'command' in str(i).lower() or 'injection' in str(i).lower()]
        assert len(cmd_issues) > 0
    
    @pytest.mark.asyncio
    async def test_path_traversal(self):
        """Test path traversal detection."""
        validator = SecurityValidator()
        
        path_code = "open('../../../etc/passwd')"
        context = ReviewContext(
            pr_number=1, repo="test/repo", files_changed=["test.py"],
            diff=path_code, base_branch="main", head_branch="feature",
            author="user", description="Test"
        )
        
        result = await validator.scan(context)
        path_issues = [i for i in result if 'path' in str(i).lower() or 'traversal' in str(i).lower()]
        assert len(path_issues) > 0


class TestQuantumPatternAnalyzerComplete:
    """Complete coverage of quantum pattern analyzer."""
    
    @pytest.mark.asyncio
    async def test_superposition_detection(self):
        """Test superposition opportunity detection."""
        analyzer = QuantumPatternAnalyzer()
        
        code_with_many_branches = """
if condition1:
    pass
elif condition2:
    pass
elif condition3:
    pass
elif condition4:
    pass
"""
        
        context = ReviewContext(
            pr_number=1, repo="test/repo", files_changed=["test.py"],
            diff=code_with_many_branches, base_branch="main", head_branch="feature",
            author="user", description="Test"
        )
        
        patterns = await analyzer.analyze(context)
        superposition = [p for p in patterns if p['type'] == 'superposition_opportunity']
        assert len(superposition) > 0
    
    @pytest.mark.asyncio
    async def test_entanglement_detection(self):
        """Test entanglement candidate detection."""
        analyzer = QuantumPatternAnalyzer()
        
        context = ReviewContext(
            pr_number=1, repo="test/repo",
            files_changed=["file1.py", "file2.py", "file3.py"],
            diff="code", base_branch="main", head_branch="feature",
            author="user", description="Test"
        )
        
        patterns = await analyzer.analyze(context)
        entanglement = [p for p in patterns if p['type'] == 'entanglement_candidate']
        assert len(entanglement) > 0
    
    @pytest.mark.asyncio
    async def test_tunneling_detection(self):
        """Test tunneling opportunity detection."""
        analyzer = QuantumPatternAnalyzer()
        
        code_with_sleep = "time.sleep(10)"
        context = ReviewContext(
            pr_number=1, repo="test/repo", files_changed=["test.py"],
            diff=code_with_sleep, base_branch="main", head_branch="feature",
            author="user", description="Test"
        )
        
        patterns = await analyzer.analyze(context)
        tunneling = [p for p in patterns if p['type'] == 'tunneling_opportunity']
        assert len(tunneling) > 0


class TestWorkflowOrchestratorComplete:
    """Complete coverage of workflow orchestrator."""
    
    @pytest.mark.asyncio
    async def test_priority_determination(self):
        """Test priority determination logic."""
        orchestrator = WorkflowOrchestrator()
        
        # High priority (critical security)
        critical_result = ReviewResult(
            status="changes_requested", confidence=0.5,
            suggestions=[{"category": "security", "severity": "critical"}],
            orchestration_plan={}, next_steps=[], knowledge_gaps=[]
        )
        
        plan = await orchestrator.create_plan(None, critical_result)
        assert plan["priority"] == "high"
        
        # Medium priority (some suggestions)
        medium_result = ReviewResult(
            status="commented", confidence=0.7,
            suggestions=[{"category": "code_quality", "severity": "medium"}],
            orchestration_plan={}, next_steps=[], knowledge_gaps=[]
        )
        
        plan = await orchestrator.create_plan(None, medium_result)
        assert plan["priority"] == "medium"
        
        # Low priority (no issues)
        low_result = ReviewResult(
            status="approved", confidence=0.95,
            suggestions=[], orchestration_plan={},
            next_steps=[], knowledge_gaps=[]
        )
        
        plan = await orchestrator.create_plan(None, low_result)
        assert plan["priority"] == "low"
    
    @pytest.mark.asyncio
    async def test_step_ordering(self):
        """Test that steps are ordered by priority."""
        orchestrator = WorkflowOrchestrator()
        
        result = ReviewResult(
            status="changes_requested", confidence=0.6,
            suggestions=[
                {"category": "security", "severity": "critical"},
                {"category": "code_quality", "severity": "medium"},
                {"category": "documentation", "severity": "low"}
            ],
            orchestration_plan={}, next_steps=[], knowledge_gaps=[]
        )
        
        plan = await orchestrator.create_plan(None, result)
        
        # Security should be first
        assert plan["steps"][0]["description"].lower().find("security") >= 0
        
        # Should have multiple steps
        assert len(plan["steps"]) >= 2


class TestKnowledgeGapDetectorComplete:
    """Complete coverage of knowledge gap detector."""
    
    @pytest.mark.asyncio
    async def test_empty_description_gap(self):
        """Test detection of empty PR description."""
        detector = KnowledgeGapDetector()
        
        context = ReviewContext(
            pr_number=1, repo="test/repo", files_changed=["test.py"],
            diff="code", base_branch="main", head_branch="feature",
            author="user", description=""
        )
        
        gaps = await detector.detect_gaps(context)
        assert any("description" in gap.lower() for gap in gaps)
    
    @pytest.mark.asyncio
    async def test_workflow_file_gap(self):
        """Test detection when workflow files are changed."""
        detector = KnowledgeGapDetector()
        
        context = ReviewContext(
            pr_number=1, repo="test/repo",
            files_changed=[".github/workflows/ci.yml"],
            diff="code", base_branch="main", head_branch="feature",
            author="user", description="Test"
        )
        
        gaps = await detector.detect_gaps(context)
        assert any("workflow" in gap.lower() for gap in gaps)
    
    @pytest.mark.asyncio
    async def test_no_gaps(self):
        """Test when no knowledge gaps exist."""
        detector = KnowledgeGapDetector()
        
        context = ReviewContext(
            pr_number=1, repo="test/repo",
            files_changed=["simple.py"],
            diff="+ def hello(): return 'world'",
            base_branch="main", head_branch="feature",
            author="user",
            description="Add hello function with proper documentation and tests"
        )
        
        gaps = await detector.detect_gaps(context)
        # Should have minimal or no gaps for well-documented simple change
        assert len(gaps) <= 1


class TestSelfEvolutionSystemComplete:
    """Complete coverage of learning system."""
    
    @pytest.mark.asyncio
    async def test_learn_from_review(self):
        """Test learning from review results."""
        system = SelfEvolutionSystem()
        
        context = ReviewContext(
            pr_number=1, repo="test/repo", files_changed=["test.py"],
            diff="code", base_branch="main", head_branch="feature",
            author="user", description="Test"
        )
        
        result = ReviewResult(
            status="approved", confidence=0.9,
            suggestions=[], orchestration_plan={},
            next_steps=[], knowledge_gaps=[]
        )
        
        # Should not raise exception
        await system.learn_from_review(context, result)
    
    @pytest.mark.asyncio
    async def test_learn_from_feedback(self):
        """Test learning from user feedback."""
        system = SelfEvolutionSystem()
        
        context = ReviewContext(
            pr_number=1, repo="test/repo", files_changed=["test.py"],
            diff="code", base_branch="main", head_branch="feature",
            author="user", description="Test"
        )
        
        feedback = "Great suggestions on security issues!"
        
        # Should not raise exception
        await system.learn_from_feedback(context, feedback)
    
    @pytest.mark.asyncio
    async def test_respond_to_prompt(self):
        """Test responding to user prompts."""
        system = SelfEvolutionSystem()
        
        context = ReviewContext(
            pr_number=1, repo="test/repo", files_changed=["test.py"],
            diff="code", base_branch="main", head_branch="feature",
            author="user", description="Test"
        )
        
        prompt = "Please explain the security suggestions"
        response = await system.respond_to_prompt(context, prompt)
        
        assert isinstance(response, str)
        assert len(response) > 0


class TestMetricsCollectorComplete:
    """Complete coverage of metrics collector."""
    
    def test_metrics_creation(self, tmp_path):
        """Test creating metrics."""
        metric = ReviewMetrics(
            pr_number=123,
            repo="test/repo",
            timestamp=datetime.utcnow(),
            review_time_seconds=15.5,
            confidence=0.85,
            status="approved",
            suggestions_count=0,
            knowledge_gaps_count=0,
            files_changed=3
        )
        
        assert metric.pr_number == 123
        assert metric.confidence == 0.85
        assert metric.status == "approved"
    
    def test_metrics_buffering(self, tmp_path):
        """Test metrics buffering mechanism."""
        collector = MetricsCollector(storage_path=tmp_path, buffer_size=5)
        
        # Add metrics
        for i in range(3):
            metric = ReviewMetrics(
                pr_number=i, repo="test/repo", timestamp=datetime.utcnow(),
                review_time_seconds=10.0, confidence=0.8, status="approved",
                suggestions_count=0, knowledge_gaps_count=0, files_changed=1
            )
            collector.record_review(metric, flush_immediately=False)
        
        # Buffer should have 3 items
        assert len(collector._metrics_buffer) == 3
        
        # Flush
        collector.flush_all()
        assert len(collector._metrics_buffer) == 0
    
    def test_metrics_aggregation(self, tmp_path):
        """Test metrics aggregation."""
        collector = MetricsCollector(storage_path=tmp_path)
        
        # Record multiple metrics
        for i in range(5):
            metric = ReviewMetrics(
                pr_number=i, repo="test/repo", timestamp=datetime.utcnow(),
                review_time_seconds=10.0 + i, confidence=0.8 + (i * 0.02),
                status="approved", suggestions_count=i, knowledge_gaps_count=0,
                files_changed=1
            )
            collector.record_review(metric)
        
        # Get aggregates
        stats = collector.get_aggregate_stats(days=1)
        
        assert stats['total_reviews'] == 5
        assert stats['avg_confidence'] > 0.8
        assert stats['avg_review_time'] > 10.0


class TestGitHubAPIClientComplete:
    """Complete coverage of GitHub API client."""
    
    @pytest.mark.asyncio
    async def test_client_initialization(self):
        """Test client initialization."""
        client = GitHubAPIClient(token="test_token")
        
        assert client.token == "test_token"
        assert client.base_url == "https://api.github.com"
    
    @pytest.mark.asyncio
    async def test_post_review_structure(self):
        """Test review posting structure."""
        client = GitHubAPIClient(token="test_token")
        
        # Mock the HTTP client
        with patch.object(client, '_make_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {"id": 123, "state": "COMMENTED"}
            
            result = await client.post_review(
                repo="test/repo",
                pr_number=1,
                body="Review body",
                event="COMMENT",
                comments=[]
            )
            
            assert result["id"] == 123
            mock_request.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_error_handling(self):
        """Test API error handling."""
        client = GitHubAPIClient(token="test_token")
        
        with patch.object(client, '_make_request', new_callable=AsyncMock) as mock_request:
            mock_request.side_effect = Exception("API Error")
            
            with pytest.raises(Exception):
                await client.post_review("test/repo", 1, "body", "COMMENT", [])


class TestReviewContextComplete:
    """Complete coverage of ReviewContext."""
    
    def test_context_creation(self):
        """Test creating review context."""
        context = ReviewContext(
            pr_number=123,
            repo="owner/repo",
            files_changed=["file1.py", "file2.py"],
            diff="+ added line\n- removed line",
            base_branch="main",
            head_branch="feature/test",
            author="testuser",
            description="Test PR description"
        )
        
        assert context.pr_number == 123
        assert context.repo == "owner/repo"
        assert len(context.files_changed) == 2
        assert "added line" in context.diff
    
    def test_context_with_defaults(self):
        """Test context with optional fields."""
        context = ReviewContext(
            pr_number=1,
            repo="test/repo",
            files_changed=[],
            diff="",
            base_branch="main",
            head_branch="feature",
            author="user",
            description=""
        )
        
        assert context.pr_number == 1
        assert len(context.files_changed) == 0
        assert context.diff == ""


class TestCodexQuantumReviewerComplete:
    """Complete coverage of main reviewer."""
    
    @pytest.mark.asyncio
    async def test_all_event_types(self):
        """Test handling all event types."""
        reviewer = CodexQuantumReviewer()
        
        context = ReviewContext(
            pr_number=1, repo="test/repo", files_changed=["test.py"],
            diff="code", base_branch="main", head_branch="feature",
            author="user", description="Test"
        )
        
        # Test each event type
        events = [
            {"action": "initial_review", "context": context},
            {"action": "incremental_review", "context": context},
            {"action": "analyze_human_feedback", "context": context, "feedback": "Good"},
            {"action": "respond_to_mention", "context": context, "comment": "Question"},
            {"action": "unknown_action", "context": context}
        ]
        
        for event in events:
            result = await reviewer.handle_event(event)
            assert "status" in result
    
    @pytest.mark.asyncio
    async def test_confidence_scoring(self):
        """Test confidence score calculation."""
        reviewer = CodexQuantumReviewer()
        
        # High confidence scenario
        context = ReviewContext(
            pr_number=1, repo="test/repo",
            files_changed=["simple.py"],
            diff="+ def hello(): return 'world'",
            base_branch="main", head_branch="feature",
            author="user", description="Simple change"
        )
        
        event = {"action": "initial_review", "context": context}
        result = await reviewer.handle_event(event)
        
        assert "confidence" in result
        assert 0.0 <= result["confidence"] <= 1.0
    
    @pytest.mark.asyncio
    async def test_review_formatting(self):
        """Test review body formatting."""
        reviewer = CodexQuantumReviewer()
        
        result = ReviewResult(
            status="changes_requested",
            confidence=0.75,
            suggestions=[
                {"category": "security", "severity": "high", "message": "Issue 1"},
                {"category": "code_quality", "severity": "medium", "message": "Issue 2"}
            ],
            orchestration_plan={"steps": [{"description": "Fix security"}]},
            next_steps=["Step 1", "Step 2"],
            knowledge_gaps=["Gap 1"]
        )
        
        body = reviewer._format_review_body(result)
        
        assert "Codex Quantum Review" in body
        assert "75.0%" in body or "75%" in body
        assert "security" in body.lower()
        assert "Step 1" in body


# Run all tests
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=codex_reviewer", "--cov-report=term-missing"])
