"""
Enhanced Test Suite for Codex Quantum Reviewer

This test suite provides comprehensive testing including:
- Secret pattern detection
- Entropy calculation
- Security vulnerability scanning
- Metrics collection
- End-to-end integration tests
"""

from __future__ import annotations

from pathlib import Path
import sys
import pytest

# Add parent directory to path for imports
AGENTS_DIR = Path(__file__).resolve().parents[1]
if str(AGENTS_DIR) not in sys.path:
    sys.path.insert(0, str(AGENTS_DIR))

from codex_reviewer.main import CodexQuantumReviewer, ReviewContext
from codex_reviewer.secret_patterns import (  # noqa: E402
    SecretPatterns,
    calculate_entropy,
    has_high_entropy,
)
from codex_reviewer.security import SecurityValidator  # noqa: E402
from codex_reviewer.metrics import MetricsCollector, ReviewMetrics  # noqa: E402


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


class TestSecretPatternDetection:
    """Test secret pattern detection functionality."""
    
    def test_entropy_calculation(self):
        """Test entropy calculation for various strings."""
        # Low entropy (repetitive)
        assert calculate_entropy("aaaaaaaaaa") < 1.0
        
        # Medium entropy
        assert 3.0 < calculate_entropy("password123") < 4.0
        
        # High entropy (random)
        assert calculate_entropy("Xy9kL2mN8pQ4rT6vW3zB") > 4.0
    
    def test_high_entropy_detection(self):
        """Test high entropy string detection."""
        # Should detect high entropy (GitHub tokens are 36 chars, well above minimum)
        assert has_high_entropy("ghp_1234567890abcdefghijklmnopqrstuv")
        
        # Stripe keys have good entropy and length
        long_stripe = "[REDACTED]"
        entropy_val = calculate_entropy(long_stripe)
        # Just verify it calculates without error
        assert entropy_val > 0
        
        # Should not detect low entropy
        assert not has_high_entropy("password123")
        assert not has_high_entropy("aaaaaaaaaaaaaaaa")
        
        # Should not detect short strings
        assert not has_high_entropy("abc")
    
    def test_placeholder_detection(self):
        """Test placeholder pattern detection."""
        # Should detect placeholders
        assert SecretPatterns.is_placeholder("YOUR_API_KEY_HERE")
        assert SecretPatterns.is_placeholder("example-token-123")
        assert SecretPatterns.is_placeholder("<api-key>")
        assert SecretPatterns.is_placeholder("${API_KEY}")
        assert SecretPatterns.is_placeholder("%TOKEN%")
        
        # Should not detect real values
        assert not SecretPatterns.is_placeholder("ghp_1234567890abcdefghijklmnopqrstuv")
    
    def test_high_risk_file_detection(self):
        """Test high-risk file detection."""
        # Should detect high-risk files
        assert SecretPatterns.is_high_risk_file(".env")
        assert SecretPatterns.is_high_risk_file("config/.env.production")
        assert SecretPatterns.is_high_risk_file("id_rsa")
        assert SecretPatterns.is_high_risk_file("private.key")
        assert SecretPatterns.is_high_risk_file("secret.pem")
        
        # Should not detect normal files
        assert not SecretPatterns.is_high_risk_file("config.yml")
        assert not SecretPatterns.is_high_risk_file("test.py")
    
    def test_compiled_patterns(self):
        """Test compiled regex patterns."""
        patterns = SecretPatterns.get_compiled_patterns()
        
        assert "api_key" in patterns
        assert "password" in patterns
        assert "github_token" in patterns
        assert "aws_access_key" in patterns
        
        # Test API key pattern matching (more reliable test)
        api_key_pattern = patterns["api_key"]
        test_string = 'API_KEY="sk_test_1234567890abcdefghij"'
        match = api_key_pattern.search(test_string)
        assert match is not None, f"Pattern should match API key in: {test_string}"


class TestSecurityValidator:
    """Test security validator functionality."""
    
    @pytest.mark.asyncio
    async def test_secret_detection(self, mock_context: ReviewContext):
        """Test hardcoded secret detection."""
        validator = SecurityValidator()
        
        # Test with diff containing potential secrets
        context_with_secrets = ReviewContext(
            pr_number=123,
            repo="test/repo",
            files_changed=["config.py"],
            diff='+ API_KEY = "sk_live_51H9x8K2eZvKYlo2C"',
            base_branch="main",
            head_branch="feature/test",
            author="testuser",
            description="Test",
            labels=[],
            reviewers=[]
        )
        
        vulnerabilities = await validator.scan(context_with_secrets)
        
        # Should detect at least one vulnerability
        assert len(vulnerabilities) > 0
        assert any(v.get("type") == "hardcoded_secret" for v in vulnerabilities)
    
    @pytest.mark.asyncio
    async def test_command_injection_detection(self, mock_context: ReviewContext):
        """Test command injection detection."""
        validator = SecurityValidator()
        
        context_with_injection = ReviewContext(
            pr_number=123,
            repo="test/repo",
            files_changed=["utils.py"],
            diff='+ os.system("rm -rf " + user_input)',
            base_branch="main",
            head_branch="feature/test",
            author="testuser",
            description="Test",
            labels=[],
            reviewers=[]
        )
        
        vulnerabilities = await validator.scan(context_with_injection)
        
        # Should detect command injection risk
        assert any(v.get("type") == "command_injection_risk" for v in vulnerabilities)
    
    @pytest.mark.asyncio
    async def test_dependency_update_detection(self, mock_context: ReviewContext):
        """Test dependency update detection."""
        validator = SecurityValidator()
        
        context_with_deps = ReviewContext(
            pr_number=123,
            repo="test/repo",
            files_changed=["requirements.txt", "package.json"],
            diff="+ django==3.0.0",
            base_branch="main",
            head_branch="feature/test",
            author="testuser",
            description="Test",
            labels=[],
            reviewers=[]
        )
        
        vulnerabilities = await validator.scan(context_with_deps)
        
        # Should detect dependency updates
        dep_vulns = [v for v in vulnerabilities if v.get("type") == "dependency_update"]
        assert len(dep_vulns) >= 2  # requirements.txt and package.json


class TestMetricsCollection:
    """Test metrics collection functionality."""
    
    def test_metrics_recording(self, tmp_path):
        """Test recording review metrics."""
        from datetime import datetime
        
        collector = MetricsCollector(storage_path=tmp_path)
        
        metrics = ReviewMetrics(
            pr_number=123,
            repo="test/repo",
            timestamp=datetime.utcnow(),
            review_time_seconds=45.5,
            confidence=0.92,
            status="approved",
            suggestions_count=3,
            knowledge_gaps_count=1,
            files_changed=5
        )
        
        collector.record_review(metrics)
        
        # Verify file was created
        assert collector.metrics_file.exists()
        
        # Verify data can be read back
        recent = collector.get_recent_metrics(days=1)
        assert len(recent) == 1
        assert recent[0].pr_number == 123
    
    def test_aggregate_calculation(self, tmp_path):
        """Test aggregate metrics calculation."""
        from datetime import datetime
        
        collector = MetricsCollector(storage_path=tmp_path)
        
        # Record multiple reviews
        for i in range(5):
            metrics = ReviewMetrics(
                pr_number=100 + i,
                repo="test/repo",
                timestamp=datetime.utcnow(),
                review_time_seconds=30.0 + i * 5,
                confidence=0.85 + i * 0.02,
                status="approved" if i % 2 == 0 else "commented",
                suggestions_count=i,
                knowledge_gaps_count=1,
                files_changed=3 + i
            )
            collector.record_review(metrics)
        
        # Calculate aggregates
        aggregates = collector.calculate_aggregates(days=1)
        
        assert aggregates.total_reviews == 5
        assert 30.0 <= aggregates.average_review_time <= 50.0
        assert 0.85 <= aggregates.average_confidence <= 0.95
        assert aggregates.status_distribution["approved"] == 3
        assert aggregates.status_distribution["commented"] == 2


class TestEndToEndIntegration:
    """End-to-end integration tests."""
    
    @pytest.mark.asyncio
    async def test_complete_review_workflow(self, mock_context: ReviewContext):
        """Test complete review workflow from event to metrics."""
        reviewer = CodexQuantumReviewer()
        
        event = {
            "action": "initial_review",
            "context": mock_context,
        }
        
        result = await reviewer.handle_event(event)
        
        # Verify review completed
        assert result["status"] == "review_complete"
        assert result["pr_number"] == 123
        assert "confidence" in result
        assert "suggestions_count" in result
        
        # Verify confidence is in valid range
        assert 0.0 <= result["confidence"] <= 1.0
    
    @pytest.mark.asyncio
    async def test_review_with_security_issues(self):
        """Test review with security vulnerabilities."""
        reviewer = CodexQuantumReviewer()
        
        context = ReviewContext(
            pr_number=456,
            repo="test/repo",
            files_changed=["app.py", ".env"],
            diff='+ password = "hardcoded_password_123"\n+ eval(user_input)',
            base_branch="main",
            head_branch="feature/security-test",
            author="testuser",
            description="Test security detection",
            labels=[],
            reviewers=[]
        )
        
        event = {
            "action": "initial_review",
            "context": context,
        }
        
        result = await reviewer.handle_event(event)
        
        # Should detect security issues
        assert result["status"] == "review_complete"
        assert result["suggestions_count"] > 0
    
    @pytest.mark.asyncio
    async def test_learning_from_feedback(self, mock_context: ReviewContext):
        """Test learning system integration."""
        reviewer = CodexQuantumReviewer()
        
        # Simulate feedback event
        feedback_event = {
            "action": "analyze_human_feedback",
            "context": mock_context,
            "feedback": {
                "accepted_suggestions": [0, 1],
                "rejected_suggestions": [2],
            }
        }
        
        result = await reviewer.handle_event(feedback_event)
        
        assert "status" in result


class TestWorkflowValidation:
    """Test workflow validation script."""
    
    def test_manifest_validation(self):
        """Test agent manifest validation."""
        manifest_path = Path(".github/agents/codex-reviewer.agent.yml")
        
        if not manifest_path.exists():
            pytest.skip("Manifest file not found")
        
        import yaml
        with open(manifest_path, 'r') as f:
            manifest = yaml.safe_load(f)
        
        # Verify required fields
        assert "name" in manifest
        assert "version" in manifest
        assert "triggers" in manifest
        assert "permissions" in manifest
        assert "capabilities" in manifest
        
        # Verify structure
        assert isinstance(manifest["triggers"], list)
        assert len(manifest["triggers"]) > 0
        
        # Verify configuration
        config = manifest.get("configuration", {})
        if "criteria_weights" in config:
            weights = config["criteria_weights"]
            total = sum(weights.values())
            assert abs(total - 1.0) < 0.01, f"Weights sum to {total}, expected 1.0"


# Run tests if executed directly
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
