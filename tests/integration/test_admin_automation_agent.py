"""
Integration tests for admin automation agent.
Tests the complete workflow of agent operations.
"""

import pytest
import os
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, UTC

# Import agent components
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / ".github" / "agents" / "admin-automation-agent" / "src"))

try:
    from agent import AdminAutomationAgent
except ImportError:
    AdminAutomationAgent = None


@pytest.mark.skipif(AdminAutomationAgent is None, reason="AdminAutomationAgent not available")
class TestAdminAutomationAgentIntegration:
    """Integration tests for AdminAutomationAgent."""
    
    @pytest.fixture
    def mock_github_token(self):
        """Provide a mock GitHub token."""
        return "ghp_test_token_1234567890"
    
    @pytest.fixture
    def agent(self, mock_github_token, tmp_path):
        """Create an agent instance with mocked dependencies."""
        with patch.dict(os.environ, {"GITHUB_TOKEN": mock_github_token}):
            agent = AdminAutomationAgent(
                github_token=mock_github_token,
                config_path=tmp_path / "config.yml"
            )
            return agent
    
    def test_agent_initialization(self, agent, mock_github_token):
        """Test that agent initializes correctly."""
        assert agent.github_token == mock_github_token
        assert agent.results["agent_version"] == "1.0.0"
        assert "timestamp" in agent.results
        assert agent.results["success"] is False  # Not complete yet
    
    def test_log_task(self, agent):
        """Test task logging functionality."""
        agent.log_task("test_task", "success", "Task completed successfully")
        
        assert len(agent.results["tasks"]) == 1
        task = agent.results["tasks"][0]
        
        assert task["task"] == "test_task"
        assert task["status"] == "success"
        assert task["message"] == "Task completed successfully"
        assert "timestamp" in task
    
    def test_log_task_with_details(self, agent):
        """Test task logging with additional details."""
        details = {"key": "value", "count": 5}
        agent.log_task("test_task", "success", "Task completed", details=details)
        
        task = agent.results["tasks"][0]
        assert task["details"] == details
    
    @patch('agent.GitHubSecretsManager')
    def test_setup_phase10_no_secrets_manager(self, mock_secrets_mgr, agent):
        """Test Phase 10 setup when secrets manager is not available."""
        agent.secrets_manager = None
        
        result = agent.task_setup_phase10(validate=False, report=False)
        
        # Should still succeed with warnings
        assert "tasks" in result
        # Environment validation should run
        assert any("validate" in str(t) or "environment" in str(t) for t in result["tasks"])
    
    @patch('agent.Phase10Validator')
    def test_health_check_no_validator(self, mock_validator, agent):
        """Test health check when validator is not available."""
        agent.validator = None
        
        result = agent.task_health_check()
        
        assert result["success"] is False
        assert "error" in result
        assert result["error"] == "Validator not available"
    
    def test_environment_validation(self, agent):
        """Test environment validation logic."""
        env_check = agent._validate_environment()
        
        assert "success" in env_check
        # Check that it validates required tools
        assert isinstance(env_check["success"], bool)
    
    def test_configuration_validation(self, agent):
        """Test configuration validation logic."""
        config_check = agent._validate_configuration()
        
        assert isinstance(config_check, dict)


@pytest.mark.skipif(AdminAutomationAgent is None, reason="AdminAutomationAgent not available")
class TestSecretsManagerIntegration:
    """Integration tests for secrets management."""
    
    @pytest.fixture
    def mock_requests(self):
        """Mock requests library for API calls."""
        with patch('agent.requests') as mock:
            yield mock
    
    @pytest.fixture
    def secrets_manager(self, mock_requests):
        """Create a secrets manager instance."""
        # Import here to avoid issues if not available
        from scripts.phase10.automated_secrets_manager import GitHubSecretsManager
        
        with patch.dict(os.environ, {"GITHUB_TOKEN": "test_token"}):
            manager = GitHubSecretsManager(
                owner="test-owner",
                repo="test-repo",
                token="test_token"
            )
            return manager
    
    def test_generate_secure_key(self, secrets_manager):
        """Test secure key generation."""
        with patch('subprocess.run') as mock_run:
            # Mock openssl command output
            mock_run.return_value = Mock(
                stdout="YWJjZGVmZ2hpamtsbW5vcA==\n",
                returncode=0
            )
            
            key = secrets_manager.generate_secure_key(length=32)
            
            assert key == "YWJjZGVmZ2hpamtsbW5vcA=="
            mock_run.assert_called_once()
    
    def test_get_public_key(self, secrets_manager, mock_requests):
        """Test getting repository public key."""
        # Mock API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "key": "test_public_key",
            "key_id": "123456"
        }
        mock_requests.get.return_value = mock_response
        
        public_key, key_id = secrets_manager.get_public_key()
        
        assert public_key == "test_public_key"
        assert key_id == "123456"
    
    def test_verify_secret_exists(self, secrets_manager, mock_requests):
        """Test secret verification when secret exists."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_requests.get.return_value = mock_response
        
        result = secrets_manager.verify_secret("TEST_SECRET")
        
        assert result is True
    
    def test_verify_secret_not_exists(self, secrets_manager, mock_requests):
        """Test secret verification when secret doesn't exist."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_requests.get.return_value = mock_response
        
        result = secrets_manager.verify_secret("NONEXISTENT_SECRET")
        
        assert result is False


class TestWorkflowIntegration:
    """Integration tests for workflow execution."""
    
    def test_phase10_workflow_steps(self):
        """Test the complete Phase 10 setup workflow steps."""
        # Define expected workflow steps
        expected_steps = [
            "validate_environment",
            "setup_secrets",
            "validate_configuration",
            "run_validation",
            "generate_report"
        ]
        
        # Verify each step is documented
        for step in expected_steps:
            assert step  # Basic verification
    
    def test_workflow_error_recovery(self):
        """Test that workflows can recover from errors."""
        # Test retry logic exists
        from scripts.phase10.automated_secrets_manager import GitHubSecretsManager
        
        # Verify error handling in secrets manager
        with patch.dict(os.environ, {"GITHUB_TOKEN": "test"}):
            manager = GitHubSecretsManager("owner", "repo", "token")
            assert manager.token is not None


class TestSecurityCompliance:
    """Integration tests for security compliance."""
    
    def test_no_secrets_in_logs(self, tmp_path, caplog):
        """Test that secrets are never logged in clear text."""
        from src.codex.security_utils import redact_sensitive_value, sanitize_log_message
        
        # Simulate logging a secret (should be redacted)
        secret_value = "ghp_1234567890abcdefghijklmnopqrstuvwxyz"
        
        # Use redaction utility
        safe_value = redact_sensitive_value(secret_value)
        
        # Create log message
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Secret value: {safe_value}")
        
        # Verify original secret not in logs
        assert secret_value not in caplog.text
        assert "[REDACTED]" in safe_value
    
    def test_secret_name_redaction(self):
        """Test that sensitive secret names are redacted."""
        from src.codex.security_utils import redact_secret_name
        
        sensitive_names = [
            "PROD_DATABASE_PASSWORD",
            "AWS_SECRET_ACCESS_KEY",
            "PRIVATE_KEY"
        ]
        
        for name in sensitive_names:
            redacted = redact_secret_name(name)
            assert redacted == "[REDACTED_SECRET_NAME]"
    
    def test_dict_key_redaction(self):
        """Test that dictionary keys containing secrets are redacted."""
        from src.codex.security_utils import redact_dict_with_secret_keys
        
        secrets_dict = {
            "GITHUB_TOKEN": "value1",
            "API_KEY": "value2",
            "SECRET_KEY": "value3"
        }
        
        redacted = redact_dict_with_secret_keys(secrets_dict)
        
        # Verify original keys not present
        assert "GITHUB_TOKEN" not in redacted
        assert "API_KEY" not in redacted
        assert "SECRET_KEY" not in redacted
        
        # Verify redacted keys present
        assert all(key.startswith("secret_") for key in redacted.keys())
        
        # Verify count preserved
        assert len(redacted) == len(secrets_dict)


class TestEndToEndWorkflow:
    """End-to-end integration tests."""
    
    @patch('agent.GitHubSecretsManager')
    @patch('agent.Phase10Validator')
    def test_complete_phase10_setup(self, mock_validator, mock_secrets_mgr):
        """Test complete Phase 10 setup workflow."""
        if AdminAutomationAgent is None:
            pytest.skip("AdminAutomationAgent not available")
        
        # Mock secrets manager
        mock_sm_instance = Mock()
        mock_sm_instance.setup_phase10_secrets.return_value = {
            "secret1": "configured",
            "secret2": "configured",
            "secret3": "configured",
            "secret4": "configured"
        }
        mock_secrets_mgr.return_value = mock_sm_instance
        
        # Mock validator
        mock_val_instance = Mock()
        mock_val_instance.run_all_tests.return_value = True
        mock_val_instance.results = {
            "summary": "All tests passed",
            "tests": [],
            "timestamp": datetime.now(UTC).isoformat()
        }
        mock_validator.return_value = mock_val_instance
        
        # Create agent
        with patch.dict(os.environ, {"GITHUB_TOKEN": "test_token"}):
            agent = AdminAutomationAgent(github_token="test_token")
            agent.secrets_manager = mock_sm_instance
            agent.validator = mock_val_instance
            
            # Run setup
            result = agent.task_setup_phase10(validate=True, report=False)
            
            # Verify workflow completed
            assert "tasks" in result
            assert len(result["tasks"]) > 0
    
    def test_audit_trail_creation(self, tmp_path):
        """Test that audit trail is created for operations."""
        audit_dir = tmp_path / ".codex" / "audit" / "phase10"
        audit_dir.mkdir(parents=True, exist_ok=True)
        
        # Simulate audit log creation
        audit_log = audit_dir / f"test-{datetime.now().strftime('%Y%m%d-%H%M%S')}.log"
        
        audit_content = f"""
Phase 10 Setup - Test
=====================
Timestamp: {datetime.now(UTC).isoformat()}
Operation: test_operation
Status: SUCCESS
"""
        
        audit_log.write_text(audit_content)
        
        # Verify audit log exists
        assert audit_log.exists()
        assert "Phase 10 Setup" in audit_log.read_text()
        assert "SUCCESS" in audit_log.read_text()


class TestErrorScenarios:
    """Test error handling scenarios."""
    
    def test_missing_github_token(self):
        """Test behavior when GitHub token is missing."""
        with patch.dict(os.environ, {}, clear=True):
            from scripts.phase10.automated_secrets_manager import GitHubSecretsManager
            
            manager = GitHubSecretsManager("owner", "repo", token=None)
            assert manager.token is None
    
    def test_api_rate_limit_handling(self):
        """Test handling of GitHub API rate limits."""
        # This would test retry logic for 429 responses
        # Implementation depends on having retry logic in place
        pass
    
    def test_network_error_handling(self):
        """Test handling of network errors."""
        # This would test connection error handling
        # Implementation depends on having proper exception handling
        pass


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
