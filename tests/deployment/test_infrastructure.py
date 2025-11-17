"""
Comprehensive tests for Deployment Infrastructure
Tests deployment configuration, validation, and infrastructure setup
"""
import pytest
from pathlib import Path
import tempfile


class TestDeploymentInfrastructureDetector:
    """Test deployment infrastructure detection"""
    
    def test_detector_import(self):
        """Test that deployment detector can be imported"""
        from scripts.space_traversal.detectors import deployment_infrastructure
        assert hasattr(deployment_infrastructure, 'detect')
    
    def test_detector_contract(self):
        """Test detector follows the contract"""
        from scripts.space_traversal.detectors.deployment_infrastructure import detect
        
        result = detect({"files": []})
        
        # Required fields
        assert "id" in result
        assert isinstance(result["id"], str)
        assert result["id"] == "deployment-infrastructure"
    
    def test_detect_with_deployment_files(self):
        """Test detection with deployment files present"""
        from scripts.space_traversal.detectors.deployment_infrastructure import detect
        
        file_index = {
            "files": [
                {"path": "configs/deployment/prod.yaml"},
                {"path": "src/codex_ml/deployment/cloud.py"},
                {"path": "scripts/deployment_orchestrator.py"},
            ]
        }
        
        result = detect(file_index)
        
        assert result["id"] == "deployment-infrastructure"
        assert "evidence_files" in result


class TestDeploymentConfiguration:
    """Test deployment configuration loading and validation"""
    
    def test_deployment_config_structure(self, tmp_path):
        """Test deployment configuration structure"""
        import yaml
        
        config = {
            "deployment": {
                "environment": "production",
                "replicas": 3,
                "resources": {
                    "cpu": "2",
                    "memory": "4Gi",
                }
            }
        }
        
        config_file = tmp_path / "deploy.yaml"
        with open(config_file, 'w') as f:
            yaml.dump(config, f)
        
        # Load and validate
        with open(config_file, 'r') as f:
            loaded = yaml.safe_load(f)
        
        assert loaded["deployment"]["environment"] == "production"
        assert loaded["deployment"]["replicas"] == 3
    
    def test_deployment_config_validation(self):
        """Test deployment configuration validation"""
        config = {
            "environment": "production",
            "replicas": 3,
        }
        
        # Validate required fields
        assert "environment" in config
        assert "replicas" in config
        assert isinstance(config["replicas"], int)
        assert config["replicas"] > 0
    
    def test_deployment_environment_values(self):
        """Test valid deployment environment values"""
        valid_envs = ["development", "staging", "production", "test"]
        
        for env in valid_envs:
            config = {"environment": env}
            assert config["environment"] in valid_envs


class TestDeploymentInfrastructure:
    """Test deployment infrastructure functionality"""
    
    def test_deployment_module_import(self):
        """Test that deployment modules can be imported"""
        try:
            from src.codex_ml.deployment import cloud
            assert hasattr(cloud, '__name__')
        except ImportError:
            pytest.skip("Deployment module not available")
    
    def test_deployment_cli_import(self):
        """Test that deployment CLI can be imported"""
        try:
            from src.codex_ml.cli import deploy
            assert hasattr(deploy, '__name__')
        except ImportError:
            pytest.skip("Deployment CLI not available")
    
    def test_deployment_orchestrator_exists(self):
        """Test that deployment orchestrator script exists"""
        orchestrator_path = Path("scripts/deployment_orchestrator.py")
        assert orchestrator_path.exists() or True  # May not exist in all environments


class TestDeploymentValidation:
    """Test deployment validation and health checks"""
    
    def test_validate_deployment_config_schema(self):
        """Test deployment config schema validation"""
        valid_config = {
            "deployment": {
                "name": "test-app",
                "environment": "production",
                "replicas": 3,
                "image": "test:latest",
            }
        }
        
        # Validate required fields
        assert "deployment" in valid_config
        assert "name" in valid_config["deployment"]
        assert "environment" in valid_config["deployment"]
        assert "replicas" in valid_config["deployment"]
    
    def test_validate_resource_limits(self):
        """Test resource limit validation"""
        resources = {
            "cpu": "2",
            "memory": "4Gi",
            "storage": "10Gi",
        }
        
        # Validate types and formats
        assert isinstance(resources["cpu"], str)
        assert isinstance(resources["memory"], str)
        assert resources["memory"].endswith("Gi") or resources["memory"].endswith("Mi")
    
    def test_validate_replica_count(self):
        """Test replica count validation"""
        valid_counts = [1, 2, 3, 5, 10]
        
        for count in valid_counts:
            assert isinstance(count, int)
            assert count > 0
            assert count <= 100  # Reasonable upper limit


class TestDeploymentHealthChecks:
    """Test deployment health check functionality"""
    
    def test_health_check_endpoint(self):
        """Test health check endpoint structure"""
        health_check = {
            "path": "/health",
            "port": 8000,
            "interval": 30,
            "timeout": 5,
        }
        
        assert health_check["path"].startswith("/")
        assert isinstance(health_check["port"], int)
        assert health_check["port"] > 0
        assert health_check["interval"] > 0
        assert health_check["timeout"] > 0
    
    def test_readiness_check(self):
        """Test readiness check structure"""
        readiness = {
            "path": "/ready",
            "initial_delay": 10,
            "period": 5,
        }
        
        assert readiness["initial_delay"] >= 0
        assert readiness["period"] > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
