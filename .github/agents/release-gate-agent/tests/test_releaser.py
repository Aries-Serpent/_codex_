"""
Tests for Release Gate Agent - Releaser Module (ACT Phase)

#AFTERMATH_PATTERN_IDENTIFIED: release_gate_testing_act
"""

import pytest
from unittest.mock import Mock, patch
from agent.releaser import ReleaseExecutor, ReleaseStatus, ReleaseResult


class TestReleaseStatus:
    """Test ReleaseStatus enum."""
    
    def test_release_status_values(self):
        """Test ReleaseStatus enum has correct values."""
        assert ReleaseStatus.SUCCESS.value == "success"
        assert ReleaseStatus.FAILED.value == "failed"
        assert ReleaseStatus.BLOCKED.value == "blocked"
        assert ReleaseStatus.PARTIAL.value == "partial"


class TestReleaseResult:
    """Test ReleaseResult dataclass."""
    
    def test_result_creation(self):
        """Test creating ReleaseResult with all fields."""
        result = ReleaseResult(
            status=ReleaseStatus.SUCCESS,
            released=True,
            release_url="https://github.com/test/repo/releases/tag/v1.0.0",
            git_tag="v1.0.0",
            deployment_status="deployed",
            health_status="healthy",
            duration_seconds=120.5
        )
        
        assert result.status == ReleaseStatus.SUCCESS
        assert result.released is True
        assert result.duration_seconds == 120.5
        assert result.metadata == {}
    
    def test_result_default_metadata(self):
        """Test ReleaseResult creates empty metadata by default."""
        result = ReleaseResult(
            status=ReleaseStatus.SUCCESS,
            released=True,
            release_url="",
            git_tag="",
            deployment_status="",
            health_status=""
        )
        
        assert result.metadata == {}


class TestReleaseExecutor:
    """Test ReleaseExecutor class."""
    
    @pytest.fixture
    def mock_brain(self):
        """Mock CognitiveBrain."""
        with patch('agent.releaser.CognitiveBrain') as mock:
            yield mock
    
    @pytest.fixture
    def executor(self, mock_brain, tmp_path):
        """Create ReleaseExecutor instance with mocked brain."""
        return ReleaseExecutor(tmp_path, repo_owner="test-org", repo_name="test-repo")
    
    def test_executor_initialization(self, executor, tmp_path):
        """Test ReleaseExecutor initializes correctly."""
        assert executor.repo_path == tmp_path
        assert executor.repo_owner == "test-org"
        assert executor.repo_name == "test-repo"
    
    def test_act_blocked_release(self, executor):
        """Test act() with blocked decision."""
        decision_result = {
            "decision": "block",
            "risk_score": 0.8,
            "blockers": ["CI failed", "Security issue"],
            "reasoning": "Critical issues detected"
        }
        release_info = {"version": "v1.0.0"}
        
        result = executor.act(decision_result, release_info)
        
        assert result["status"] == "blocked"
        assert result["released"] is False
        assert result["error_message"] == "Critical issues detected"
    
    def test_act_successful_release(self, executor):
        """Test act() with successful release execution."""
        decision_result = {
            "decision": "approve",
            "risk_score": 0.1
        }
        release_info = {"version": "v1.0.0", "release_notes": "Initial release"}
        
        with patch.object(executor, '_create_git_tag', return_value="v1.0.0") as mock_tag, \
             patch.object(executor, '_create_github_release', return_value="https://github.com/test/repo/releases/tag/v1.0.0") as mock_release, \
             patch.object(executor, '_trigger_deployment', return_value="deployed") as mock_deploy, \
             patch.object(executor, '_monitor_release_health', return_value="healthy") as mock_health:
            
            result = executor.act(decision_result, release_info)
        
        assert result["status"] == "success"
        assert result["released"] is True
        assert result["release_url"].startswith("https://github.com")
        assert result["git_tag"] == "v1.0.0"
        assert result["health_status"] == "healthy"
    
    def test_act_with_monitoring(self, executor):
        """Test act() enables monitoring for risky releases."""
        decision_result = {
            "decision": "approve_with_monitoring",
            "risk_score": 0.5
        }
        release_info = {"version": "v1.0.0"}
        
        with patch.object(executor, '_enable_enhanced_monitoring') as mock_monitor, \
             patch.object(executor, '_create_git_tag', return_value="v1.0.0"), \
             patch.object(executor, '_create_github_release', return_value="https://url"), \
             patch.object(executor, '_trigger_deployment', return_value="deployed"), \
             patch.object(executor, '_monitor_release_health', return_value="healthy"):
            
            result = executor.act(decision_result, release_info)
        
        mock_monitor.assert_called_once()
        assert result["metadata"]["monitoring_enabled"] is True
    
    def test_act_handles_failure(self, executor):
        """Test act() handles execution failures gracefully."""
        decision_result = {
            "decision": "approve",
            "risk_score": 0.1
        }
        release_info = {"version": "v1.0.0"}
        
        with patch.object(executor, '_create_git_tag', side_effect=Exception("Git error")):
            result = executor.act(decision_result, release_info)
        
        assert result["status"] == "failed"
        assert result["released"] is False
        assert "Git error" in result["error_message"]
    
    def test_create_blocking_result(self, executor):
        """Test _create_blocking_result() creates proper blocked result."""
        decision_result = {
            "reasoning": "Test blocked",
            "blockers": ["Issue 1", "Issue 2"],
            "risk_score": 0.9
        }
        
        result = executor._create_blocking_result(decision_result, 0.0)
        
        assert result["status"] == "blocked"
        assert result["released"] is False
        assert result["error_message"] == "Test blocked"
        assert result["metadata"]["blockers"] == ["Issue 1", "Issue 2"]
    
    def test_create_git_tag_success(self, executor):
        """Test _create_git_tag() creates git tag successfully."""
        release_info = {"version": "v1.0.0"}
        
        mock_result = Mock()
        mock_result.returncode = 0
        
        with patch('subprocess.run', return_value=mock_result):
            tag = executor._create_git_tag(release_info)
        
        assert tag == "v1.0.0"
    
    def test_create_git_tag_failure(self, executor):
        """Test _create_git_tag() handles failure gracefully."""
        release_info = {"version": "v1.0.0"}
        
        with patch('subprocess.run', side_effect=Exception("Git error")):
            tag = executor._create_git_tag(release_info)
        
        # Should still return version even on failure
        assert tag == "v1.0.0"
    
    def test_create_github_release_success(self, executor):
        """Test _create_github_release() creates release successfully."""
        release_info = {"version": "v1.0.0", "release_notes": "Release notes"}
        
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = b"https://github.com/test-org/test-repo/releases/tag/v1.0.0"
        
        with patch('subprocess.run', return_value=mock_result):
            url = executor._create_github_release(release_info, "v1.0.0")
        
        assert url.startswith("https://github.com")
        assert "v1.0.0" in url
    
    def test_create_github_release_uses_repo_params(self, executor):
        """Test _create_github_release() uses configured repo parameters."""
        release_info = {"version": "v1.0.0"}
        
        with patch('subprocess.run', side_effect=Exception("gh error")):
            url = executor._create_github_release(release_info, "v1.0.0")
        
        assert "test-org" in url
        assert "test-repo" in url
    
    def test_trigger_deployment(self, executor):
        """Test _trigger_deployment() returns status."""
        release_info = {"version": "v1.0.0"}
        status = executor._trigger_deployment(release_info)
        
        # Placeholder returns "pending"
        assert status == "pending"
    
    def test_monitor_release_health(self, executor):
        """Test _monitor_release_health() returns health status."""
        health = executor._monitor_release_health(60)
        
        # Placeholder returns "healthy"
        assert health == "healthy"
    
    def test_enable_enhanced_monitoring(self, executor):
        """Test _enable_enhanced_monitoring() executes without error."""
        # Should not raise any exception
        executor._enable_enhanced_monitoring()
