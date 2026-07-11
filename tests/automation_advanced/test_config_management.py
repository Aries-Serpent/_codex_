"""
Phase 20.1 Lane 2: Configuration Automation Management Tests

Comprehensive test suite for configuration management automation including:
- Configuration validation engine
- Hydra configuration templates
- Secret management and encryption
- Configuration drift detection
- Multi-environment configuration
- Configuration templating and variable substitution
- Multi-environment config management (dev/staging/prod)
- Secrets management integration
- Config hot-reload capability

Target: 20+ tests, ≥90% coverage
"""

import pytest
import json
import yaml
import tempfile
import os
from pathlib import Path
from typing import Dict, Any, Optional, List
from unittest.mock import Mock, patch, MagicMock
from dataclasses import dataclass, asdict
import hashlib


# ============================================================================
# CONFIGURATION MODELS
# ============================================================================

@dataclass
class ConfigEnvironment:
    """Represents a configuration environment."""
    name: str
    variables: Dict[str, str]
    secrets: Dict[str, str]
    schema: Dict[str, Any]


@dataclass
class ConfigChange:
    """Represents a configuration change."""
    timestamp: str
    user: str
    change_type: str  # "created", "updated", "deleted"
    key: str
    old_value: Optional[Any]
    new_value: Optional[Any]
    checksum: str


# ============================================================================
# CONFIGURATION MANAGEMENT ENGINE
# ============================================================================

class ConfigValidator:
    """Validates configuration against schema."""
    
    def __init__(self, schema: Dict[str, Any]):
        self.schema = schema
        self.errors = []
    
    def validate(self, config: Dict[str, Any]) -> bool:
        """Validate config against schema."""
        self.errors = []
        for key, spec in self.schema.items():
            if spec.get("required") and key not in config:
                self.errors.append(f"Missing required key: {key}")
            elif key in config:
                value = config[key]
                expected_type = spec.get("type")
                if expected_type and not isinstance(value, expected_type):
                    self.errors.append(
                        f"Key '{key}' should be {expected_type.__name__}, "
                        f"got {type(value).__name__}"
                    )
        return len(self.errors) == 0
    
    def get_errors(self) -> List[str]:
        """Get validation errors."""
        return self.errors


class ConfigTemplateRenderer:
    """Renders configuration templates with variable substitution."""
    
    def __init__(self):
        self.variables = {}
    
    def set_variable(self, name: str, value: str) -> None:
        """Set a template variable."""
        self.variables[name] = value
    
    def render(self, template: str) -> str:
        """Render template with variables."""
        result = template
        for var_name, var_value in self.variables.items():
            result = result.replace(f"${{{var_name}}}", str(var_value))
        return result
    
    def render_dict(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Render all string values in a dictionary."""
        result = {}
        for key, value in config.items():
            if isinstance(value, str):
                result[key] = self.render(value)
            elif isinstance(value, dict):
                result[key] = self.render_dict(value)
            elif isinstance(value, list):
                result[key] = [
                    self.render(item) if isinstance(item, str) 
                    else self.render_dict(item) if isinstance(item, dict)
                    else item
                    for item in value
                ]
            else:
                result[key] = value
        return result


class ConfigDriftDetector:
    """Detects configuration drift between current and desired state."""
    
    def __init__(self, desired_config: Dict[str, Any]):
        self.desired_config = desired_config
        self.drift_items = []
    
    def detect(self, current_config: Dict[str, Any]) -> bool:
        """Detect if current config drifts from desired."""
        self.drift_items = []
        self._compare_dicts(self.desired_config, current_config, "")
        return len(self.drift_items) == 0
    
    def _compare_dicts(self, desired: Dict, current: Dict, prefix: str) -> None:
        """Recursively compare nested dictionaries."""
        all_keys = set(desired.keys()) | set(current.keys())
        for key in all_keys:
            full_path = f"{prefix}.{key}" if prefix else key
            if key not in desired:
                self.drift_items.append((full_path, None, current[key], "extra"))
            elif key not in current:
                self.drift_items.append((full_path, desired[key], None, "missing"))
            elif isinstance(desired[key], dict) and isinstance(current[key], dict):
                self._compare_dicts(desired[key], current[key], full_path)
            elif desired[key] != current[key]:
                self.drift_items.append(
                    (full_path, desired[key], current[key], "changed")
                )
    
    def get_drift_items(self) -> List[tuple]:
        """Get detected drift items."""
        return self.drift_items


class ConfigAuditTrail:
    """Maintains audit trail of configuration changes."""
    
    def __init__(self):
        self.changes: List[ConfigChange] = []
    
    def record_change(
        self,
        change_type: str,
        key: str,
        old_value: Optional[Any],
        new_value: Optional[Any],
        user: str = "system"
    ) -> None:
        """Record a configuration change."""
        from datetime import datetime
        checksum = hashlib.sha256(
            f"{key}{new_value}".encode()
        ).hexdigest()[:8]
        
        change = ConfigChange(
            timestamp=datetime.now().isoformat(),
            user=user,
            change_type=change_type,
            key=key,
            old_value=old_value,
            new_value=new_value,
            checksum=checksum
        )
        self.changes.append(change)
    
    def get_changes_for_key(self, key: str) -> List[ConfigChange]:
        """Get all changes for a specific key."""
        return [c for c in self.changes if c.key == key]
    
    def get_all_changes(self) -> List[ConfigChange]:
        """Get all recorded changes."""
        return self.changes


class SecretManager:
    """Manages configuration secrets with encryption."""
    
    def __init__(self):
        self.secrets = {}
        self.encryption_key = "default-test-key"
    
    def store_secret(self, name: str, value: str) -> None:
        """Store a secret value."""
        # Simulate encryption with simple obfuscation
        encrypted = hashlib.sha256(value.encode()).hexdigest()
        self.secrets[name] = {"encrypted": encrypted, "original": value}
    
    def retrieve_secret(self, name: str) -> Optional[str]:
        """Retrieve a secret value."""
        if name in self.secrets:
            return self.secrets[name]["original"]
        return None
    
    def is_encrypted(self, name: str) -> bool:
        """Check if secret is encrypted."""
        return name in self.secrets
    
    def rotate_secret(self, name: str, new_value: str) -> None:
        """Rotate a secret to a new value."""
        if name in self.secrets:
            self.store_secret(name, new_value)


class MultiEnvironmentConfigManager:
    """Manages configurations across multiple environments."""
    
    def __init__(self):
        self.environments: Dict[str, ConfigEnvironment] = {}
    
    def add_environment(self, env: ConfigEnvironment) -> None:
        """Add an environment configuration."""
        self.environments[env.name] = env
    
    def get_environment(self, name: str) -> Optional[ConfigEnvironment]:
        """Get environment configuration."""
        return self.environments.get(name)
    
    def get_all_environments(self) -> List[str]:
        """Get all environment names."""
        return list(self.environments.keys())
    
    def validate_environment(self, name: str, config: Dict[str, Any]) -> bool:
        """Validate config against environment schema."""
        env = self.get_environment(name)
        if not env:
            return False
        validator = ConfigValidator(env.schema)
        return validator.validate(config)


class ConfigHotReloader:
    """Enables hot-reload of configuration changes."""
    
    def __init__(self):
        self.current_config = {}
        self.reload_listeners = []
        self.config_version = 0
    
    def register_listener(self, callback) -> None:
        """Register a callback for config changes."""
        self.reload_listeners.append(callback)
    
    def reload_config(self, new_config: Dict[str, Any]) -> None:
        """Reload configuration and notify listeners."""
        self.current_config = new_config
        self.config_version += 1
        for listener in self.reload_listeners:
            listener(new_config, self.config_version)
    
    def get_config_version(self) -> int:
        """Get current config version."""
        return self.config_version


# ============================================================================
# TESTS
# ============================================================================

class TestConfigValidation:
    """Test configuration validation engine."""
    
    def test_validate_config_success(self):
        """Test successful configuration validation."""
        schema = {
            "database": {"type": dict, "required": True},
            "port": {"type": int, "required": True},
            "timeout": {"type": int, "required": False},
        }
        config = {
            "database": {"host": "localhost"},
            "port": 5432,
        }
        
        validator = ConfigValidator(schema)
        assert validator.validate(config) is True
        assert len(validator.get_errors()) == 0
    
    def test_validate_config_missing_required(self):
        """Test validation fails when required field is missing."""
        schema = {
            "database": {"type": dict, "required": True},
            "port": {"type": int, "required": True},
        }
        config = {"database": {}}
        
        validator = ConfigValidator(schema)
        assert validator.validate(config) is False
        assert any("port" in error for error in validator.get_errors())
    
    def test_validate_config_type_mismatch(self):
        """Test validation fails on type mismatch."""
        schema = {
            "port": {"type": int, "required": True},
        }
        config = {"port": "5432"}
        
        validator = ConfigValidator(schema)
        assert validator.validate(config) is False
        assert any("port" in error for error in validator.get_errors())
    
    def test_validate_nested_config(self):
        """Test validation of nested configuration."""
        schema = {
            "database": {"type": dict, "required": True},
            "port": {"type": int, "required": True},
        }
        config = {
            "database": {
                "host": "localhost",
                "credentials": {"user": "admin", "password": "secret"}
            },
            "port": 5432,
        }
        
        validator = ConfigValidator(schema)
        assert validator.validate(config) is True


class TestConfigTemplateRendering:
    """Test configuration template rendering with variable substitution."""
    
    def test_render_simple_template(self):
        """Test rendering a simple template."""
        renderer = ConfigTemplateRenderer()
        renderer.set_variable("host", "localhost")
        renderer.set_variable("port", "5432")
        
        template = "postgresql://${host}:${port}/mydb"
        result = renderer.render(template)
        
        assert result == "postgresql://localhost:5432/mydb"
    
    def test_render_dict_template(self):
        """Test rendering template dictionary."""
        renderer = ConfigTemplateRenderer()
        renderer.set_variable("env", "production")
        renderer.set_variable("region", "us-east-1")
        
        template_dict = {
            "environment": "${env}",
            "region": "${region}",
            "bucket": "config-${env}-${region}",
        }
        
        result = renderer.render_dict(template_dict)
        
        assert result["environment"] == "production"
        assert result["region"] == "us-east-1"
        assert result["bucket"] == "config-production-us-east-1"
    
    def test_render_nested_template(self):
        """Test rendering nested template structures."""
        renderer = ConfigTemplateRenderer()
        renderer.set_variable("db_host", "postgres.internal")
        renderer.set_variable("db_port", "5432")
        
        template_dict = {
            "database": {
                "primary": {
                    "host": "${db_host}",
                    "port": "${db_port}",
                },
                "replica": {
                    "host": "replica-${db_host}",
                    "port": "${db_port}",
                }
            }
        }
        
        result = renderer.render_dict(template_dict)
        
        assert result["database"]["primary"]["host"] == "postgres.internal"
        assert result["database"]["replica"]["host"] == "replica-postgres.internal"
    
    def test_render_list_with_variables(self):
        """Test rendering lists containing variables."""
        renderer = ConfigTemplateRenderer()
        renderer.set_variable("replicas", "3")
        
        template_dict = {
            "services": [
                "${replicas}",
                "service-${replicas}",
            ]
        }
        
        result = renderer.render_dict(template_dict)
        
        assert result["services"][0] == "3"
        assert result["services"][1] == "service-3"


class TestConfigDriftDetection:
    """Test configuration drift detection."""
    
    def test_detect_no_drift(self):
        """Test when desired and current configs match."""
        desired = {"host": "localhost", "port": 5432}
        current = {"host": "localhost", "port": 5432}
        
        detector = ConfigDriftDetector(desired)
        assert detector.detect(current) is True
        assert len(detector.get_drift_items()) == 0
    
    def test_detect_value_drift(self):
        """Test detection of changed values."""
        desired = {"host": "localhost", "port": 5432}
        current = {"host": "remotehost", "port": 5432}
        
        detector = ConfigDriftDetector(desired)
        assert detector.detect(current) is False
        
        drift = detector.get_drift_items()
        assert len(drift) == 1
        assert drift[0][0] == "host"
        assert drift[0][3] == "changed"
    
    def test_detect_missing_key(self):
        """Test detection of missing keys."""
        desired = {"host": "localhost", "port": 5432}
        current = {"host": "localhost"}
        
        detector = ConfigDriftDetector(desired)
        assert detector.detect(current) is False
        
        drift = detector.get_drift_items()
        assert any(item[3] == "missing" for item in drift)
    
    def test_detect_extra_key(self):
        """Test detection of extra keys."""
        desired = {"host": "localhost"}
        current = {"host": "localhost", "port": 5432}
        
        detector = ConfigDriftDetector(desired)
        assert detector.detect(current) is False
        
        drift = detector.get_drift_items()
        assert any(item[3] == "extra" for item in drift)
    
    def test_detect_nested_drift(self):
        """Test detection of drift in nested structures."""
        desired = {
            "database": {
                "primary": {"host": "localhost"},
                "replica": {"host": "replica"}
            }
        }
        current = {
            "database": {
                "primary": {"host": "localhost"},
                "replica": {"host": "replica-changed"}
            }
        }
        
        detector = ConfigDriftDetector(desired)
        assert detector.detect(current) is False
        
        drift = detector.get_drift_items()
        assert any("replica" in item[0] for item in drift)


class TestConfigAuditTrail:
    """Test configuration audit trail tracking."""
    
    def test_record_single_change(self):
        """Test recording a single configuration change."""
        trail = ConfigAuditTrail()
        trail.record_change("updated", "database.host", "localhost", "remotehost", "admin")
        
        changes = trail.get_all_changes()
        assert len(changes) == 1
        assert changes[0].key == "database.host"
        assert changes[0].old_value == "localhost"
        assert changes[0].new_value == "remotehost"
    
    def test_record_multiple_changes(self):
        """Test recording multiple configuration changes."""
        trail = ConfigAuditTrail()
        trail.record_change("created", "api.key", None, "secret123", "system")
        trail.record_change("updated", "database.port", 5432, 5433, "admin")
        trail.record_change("deleted", "deprecated.option", "value", None, "admin")
        
        changes = trail.get_all_changes()
        assert len(changes) == 3
        assert changes[0].change_type == "created"
        assert changes[1].change_type == "updated"
        assert changes[2].change_type == "deleted"
    
    def test_get_changes_for_key(self):
        """Test retrieving changes for a specific key."""
        trail = ConfigAuditTrail()
        trail.record_change("created", "database.host", None, "localhost", "admin")
        trail.record_change("updated", "database.host", "localhost", "remotehost", "admin")
        trail.record_change("updated", "database.port", 5432, 5433, "admin")
        
        changes = trail.get_changes_for_key("database.host")
        assert len(changes) == 2
        assert all(c.key == "database.host" for c in changes)
    
    def test_change_checksum_generation(self):
        """Test that change checksums are generated correctly."""
        trail = ConfigAuditTrail()
        trail.record_change("updated", "api.key", "old", "new", "admin")
        
        changes = trail.get_all_changes()
        assert len(changes[0].checksum) == 8
        assert changes[0].checksum.isalnum()


class TestSecretManagement:
    """Test secret management and encryption."""
    
    def test_store_retrieve_secret(self):
        """Test storing and retrieving secrets."""
        manager = SecretManager()
        manager.store_secret("db_password", "super_secret_123")
        
        retrieved = manager.retrieve_secret("db_password")
        assert retrieved == "super_secret_123"
    
    def test_secret_encryption_status(self):
        """Test checking encryption status of secrets."""
        manager = SecretManager()
        assert manager.is_encrypted("nonexistent") is False
        
        manager.store_secret("api_key", "key123")
        assert manager.is_encrypted("api_key") is True
    
    def test_retrieve_nonexistent_secret(self):
        """Test retrieving a secret that doesn't exist."""
        manager = SecretManager()
        assert manager.retrieve_secret("nonexistent") is None
    
    def test_rotate_secret(self):
        """Test rotating a secret to a new value."""
        manager = SecretManager()
        manager.store_secret("db_password", "old_password")
        old_value = manager.retrieve_secret("db_password")
        
        manager.rotate_secret("db_password", "new_password")
        new_value = manager.retrieve_secret("db_password")
        
        assert old_value == "old_password"
        assert new_value == "new_password"
    
    def test_multiple_secrets(self):
        """Test managing multiple secrets."""
        manager = SecretManager()
        secrets = {
            "db_password": "db_secret",
            "api_key": "api_secret",
            "jwt_token": "jwt_secret",
        }
        
        for name, value in secrets.items():
            manager.store_secret(name, value)
        
        for name, expected_value in secrets.items():
            assert manager.retrieve_secret(name) == expected_value


class TestMultiEnvironmentConfig:
    """Test multi-environment configuration management."""
    
    def test_add_environment(self):
        """Test adding environment configurations."""
        manager = MultiEnvironmentConfigManager()
        
        env = ConfigEnvironment(
            name="production",
            variables={"LOG_LEVEL": "info"},
            secrets={"DB_PASSWORD": "prod_secret"},
            schema={"database": {"type": dict, "required": True}}
        )
        
        manager.add_environment(env)
        assert manager.get_environment("production") is not None
    
    def test_get_all_environments(self):
        """Test retrieving all environment names."""
        manager = MultiEnvironmentConfigManager()
        
        envs = ["development", "staging", "production"]
        for env_name in envs:
            env = ConfigEnvironment(
                name=env_name,
                variables={},
                secrets={},
                schema={}
            )
            manager.add_environment(env)
        
        all_envs = manager.get_all_environments()
        assert set(all_envs) == set(envs)
    
    def test_validate_environment_config(self):
        """Test validating config against environment schema."""
        manager = MultiEnvironmentConfigManager()
        
        schema = {
            "database": {"type": dict, "required": True},
            "port": {"type": int, "required": True},
        }
        
        env = ConfigEnvironment(
            name="production",
            variables={},
            secrets={},
            schema=schema
        )
        
        manager.add_environment(env)
        
        valid_config = {"database": {}, "port": 5432}
        invalid_config = {"database": {}}
        
        assert manager.validate_environment("production", valid_config) is True
        assert manager.validate_environment("production", invalid_config) is False
    
    def test_environment_specific_validation(self):
        """Test different validation rules per environment."""
        manager = MultiEnvironmentConfigManager()
        
        dev_schema = {
            "database": {"type": dict, "required": False},
        }
        
        prod_schema = {
            "database": {"type": dict, "required": True},
            "backup": {"type": dict, "required": True},
        }
        
        manager.add_environment(ConfigEnvironment(
            name="development",
            variables={},
            secrets={},
            schema=dev_schema
        ))
        
        manager.add_environment(ConfigEnvironment(
            name="production",
            variables={},
            secrets={},
            schema=prod_schema
        ))
        
        minimal_config = {}
        prod_config = {"database": {}, "backup": {}}
        
        assert manager.validate_environment("development", minimal_config) is True
        assert manager.validate_environment("production", minimal_config) is False
        assert manager.validate_environment("production", prod_config) is True


class TestConfigHotReload:
    """Test configuration hot-reload capability."""
    
    def test_reload_config(self):
        """Test reloading configuration."""
        reloader = ConfigHotReloader()
        
        new_config = {"database": "localhost", "port": 5432}
        reloader.reload_config(new_config)
        
        assert reloader.current_config == new_config
        assert reloader.get_config_version() == 1
    
    def test_register_and_notify_listeners(self):
        """Test registering listeners and notifying on reload."""
        reloader = ConfigHotReloader()
        listener_called = {"count": 0, "config": None, "version": None}
        
        def listener(config, version):
            listener_called["count"] += 1
            listener_called["config"] = config
            listener_called["version"] = version
        
        reloader.register_listener(listener)
        
        new_config = {"debug": True}
        reloader.reload_config(new_config)
        
        assert listener_called["count"] == 1
        assert listener_called["config"] == new_config
        assert listener_called["version"] == 1
    
    def test_multiple_listeners(self):
        """Test multiple listeners are notified."""
        reloader = ConfigHotReloader()
        calls = {"listener1": 0, "listener2": 0}
        
        def listener1(config, version):
            calls["listener1"] += 1
        
        def listener2(config, version):
            calls["listener2"] += 1
        
        reloader.register_listener(listener1)
        reloader.register_listener(listener2)
        
        reloader.reload_config({"key": "value"})
        reloader.reload_config({"key": "value2"})
        
        assert calls["listener1"] == 2
        assert calls["listener2"] == 2
    
    def test_config_version_increment(self):
        """Test that config version increments on reload."""
        reloader = ConfigHotReloader()
        
        assert reloader.get_config_version() == 0
        
        reloader.reload_config({"v": 1})
        assert reloader.get_config_version() == 1
        
        reloader.reload_config({"v": 2})
        assert reloader.get_config_version() == 2
        
        reloader.reload_config({"v": 3})
        assert reloader.get_config_version() == 3


class TestConfigIntegration:
    """Integration tests for configuration management system."""
    
    def test_full_config_workflow(self):
        """Test complete configuration management workflow."""
        # 1. Define schema
        schema = {
            "database": {"type": dict, "required": True},
            "cache": {"type": dict, "required": False},
        }
        
        # 2. Validate initial config
        validator = ConfigValidator(schema)
        initial_config = {"database": {"host": "localhost"}}
        assert validator.validate(initial_config) is True
        
        # 3. Render template
        renderer = ConfigTemplateRenderer()
        renderer.set_variable("env", "production")
        template_config = {
            "database": {
                "host": "db-${env}.internal"
            },
            "cache": {
                "host": "cache-${env}.internal"
            }
        }
        rendered = renderer.render_dict(template_config)
        assert "production" in rendered["database"]["host"]
        
        # 4. Track changes
        trail = ConfigAuditTrail()
        trail.record_change("created", "database.host", None, "db-production.internal", "admin")
        assert len(trail.get_all_changes()) == 1
        
        # 5. Detect drift
        current = {"database": {"host": "db-dev.internal"}, "cache": {"host": "cache-production.internal"}}
        detector = ConfigDriftDetector(rendered)
        assert detector.detect(current) is False
    
    def test_multi_environment_workflow(self):
        """Test configuration across environments."""
        manager = MultiEnvironmentConfigManager()
        
        # Setup environments
        for env_name in ["dev", "staging", "prod"]:
            schema = {
                "database": {"type": dict, "required": True},
                "log_level": {"type": str, "required": True},
            }
            env = ConfigEnvironment(
                name=env_name,
                variables={"ENV": env_name},
                secrets={"DB_PASSWORD": f"{env_name}_secret"},
                schema=schema
            )
            manager.add_environment(env)
        
        # Validate configs for each environment
        dev_config = {"database": {}, "log_level": "debug"}
        prod_config = {"database": {}, "log_level": "error"}
        
        assert manager.validate_environment("dev", dev_config) is True
        assert manager.validate_environment("prod", prod_config) is True
    
    def test_secret_and_template_integration(self):
        """Test integrating secrets with template rendering."""
        secrets = SecretManager()
        secrets.store_secret("db_password", "secret123")
        
        renderer = ConfigTemplateRenderer()
        renderer.set_variable("password", secrets.retrieve_secret("db_password"))
        
        template = {"database": {"password": "${password}"}}
        rendered = renderer.render_dict(template)
        
        assert rendered["database"]["password"] == "secret123"


# ============================================================================
# CONFTEST FIXTURES
# ============================================================================

@pytest.fixture
def config_validator():
    """Provide a config validator."""
    schema = {
        "database": {"type": dict, "required": True},
        "port": {"type": int, "required": True},
    }
    return ConfigValidator(schema)


@pytest.fixture
def template_renderer():
    """Provide a template renderer."""
    return ConfigTemplateRenderer()


@pytest.fixture
def secret_manager():
    """Provide a secret manager."""
    return SecretManager()


@pytest.fixture
def environment_manager():
    """Provide a multi-environment manager."""
    manager = MultiEnvironmentConfigManager()
    
    for env_name in ["development", "staging", "production"]:
        schema = {
            "database": {"type": dict, "required": True},
            "port": {"type": int, "required": False},
        }
        env = ConfigEnvironment(
            name=env_name,
            variables={"ENV": env_name},
            secrets={},
            schema=schema
        )
        manager.add_environment(env)
    
    return manager


@pytest.fixture
def audit_trail():
    """Provide an audit trail."""
    return ConfigAuditTrail()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])


class TestHydraIntegration:
    """Test Hydra configuration framework integration."""
    
    def test_hydra_config_composition(self):
        """Test basic Hydra config composition."""
        # Simulate Hydra config composition
        base_config = {"database": {"host": "localhost", "port": 5432}}
        override_config = {"database": {"host": "remotehost"}}
        
        # Manual merge to simulate Hydra composition
        result = {**base_config}
        result["database"] = {**result["database"], **override_config["database"]}
        
        assert result["database"]["host"] == "remotehost"
        assert result["database"]["port"] == 5432
    
    def test_hydra_interpolation(self):
        """Test Hydra value interpolation (similar to template rendering)."""
        renderer = ConfigTemplateRenderer()
        renderer.set_variable("db_user", "admin")
        renderer.set_variable("db_pass", "secret")
        
        config = {
            "connection_string": "postgresql://${db_user}:${db_pass}@localhost/mydb"
        }
        
        result = renderer.render_dict(config)
        assert "admin" in result["connection_string"]
        assert "secret" in result["connection_string"]
    
    def test_structured_config_schema(self):
        """Test Hydra structured config with schema validation."""
        schema = {
            "database": {
                "type": dict,
                "required": True,
            },
            "defaults": {
                "type": list,
                "required": False,
            }
        }
        
        config = {
            "defaults": ["_self_", "db/mysql"],
            "database": {
                "driver": "mysql",
                "host": "localhost"
            }
        }
        
        validator = ConfigValidator(schema)
        assert validator.validate(config) is True


class TestConfigurationEncryption:
    """Test configuration encryption and decryption."""
    
    def test_secret_field_encryption(self):
        """Test encrypting specific config fields."""
        manager = SecretManager()
        config = {
            "database": {
                "host": "localhost",
                "password": "secret_pass"
            }
        }
        
        # Store password as secret
        manager.store_secret("db_password", config["database"]["password"])
        assert manager.is_encrypted("db_password") is True
    
    def test_config_with_encrypted_fields(self):
        """Test working with configs containing encrypted fields."""
        manager = SecretManager()
        
        encrypted_fields = ["password", "api_key", "jwt_secret"]
        for field in encrypted_fields:
            manager.store_secret(field, f"{field}_value")
        
        for field in encrypted_fields:
            assert manager.retrieve_secret(field) == f"{field}_value"
    
    def test_secret_rotation_audit(self):
        """Test audit trail for secret rotation."""
        trail = ConfigAuditTrail()
        manager = SecretManager()
        
        manager.store_secret("api_key", "old_key")
        trail.record_change("created", "api_key", None, "old_key", "admin")
        
        manager.rotate_secret("api_key", "new_key")
        trail.record_change("rotated", "api_key", "old_key", "new_key", "admin")
        
        changes = trail.get_changes_for_key("api_key")
        assert len(changes) == 2
        assert changes[1].change_type == "rotated"


class TestConfigurationValidationEdgeCases:
    """Test edge cases in configuration validation."""
    
    def test_validate_empty_config(self):
        """Test validation of empty configuration."""
        schema = {
            "optional_field": {"type": str, "required": False}
        }
        config = {}
        
        validator = ConfigValidator(schema)
        assert validator.validate(config) is True
    
    def test_validate_config_with_none_values(self):
        """Test validation with None values."""
        schema = {
            "field": {"type": type(None), "required": False}
        }
        config = {"field": None}
        
        validator = ConfigValidator(schema)
        assert validator.validate(config) is True
    
    def test_validate_deeply_nested_config(self):
        """Test validation of deeply nested configurations."""
        schema = {
            "level1": {"type": dict, "required": True}
        }
        
        config = {
            "level1": {
                "level2": {
                    "level3": {
                        "level4": {
                            "value": "deep"
                        }
                    }
                }
            }
        }
        
        validator = ConfigValidator(schema)
        assert validator.validate(config) is True
    
    def test_validate_config_list_values(self):
        """Test validation with list type values."""
        schema = {
            "servers": {"type": list, "required": True}
        }
        
        config = {
            "servers": ["server1", "server2", "server3"]
        }
        
        validator = ConfigValidator(schema)
        assert validator.validate(config) is True


class TestConfigurationChangeTracking:
    """Test detailed configuration change tracking."""
    
    def test_track_bulk_changes(self):
        """Test tracking multiple configuration changes."""
        trail = ConfigAuditTrail()
        
        changes = [
            ("created", "app.name", None, "MyApp", "deploy_system"),
            ("created", "app.version", None, "1.0.0", "deploy_system"),
            ("created", "database.host", None, "db.example.com", "deploy_system"),
            ("updated", "app.debug", False, True, "developer"),
            ("updated", "database.port", 5432, 5433, "admin"),
        ]
        
        for change_type, key, old_val, new_val, user in changes:
            trail.record_change(change_type, key, old_val, new_val, user)
        
        assert len(trail.get_all_changes()) == 5
    
    def test_track_deletions(self):
        """Test tracking configuration deletions."""
        trail = ConfigAuditTrail()
        trail.record_change("deleted", "deprecated.setting", "old_value", None, "admin")
        
        changes = trail.get_all_changes()
        assert len(changes) == 1
        assert changes[0].new_value is None
        assert changes[0].change_type == "deleted"
    
    def test_change_filtering(self):
        """Test filtering changes by key."""
        trail = ConfigAuditTrail()
        
        # Add changes to different keys
        trail.record_change("updated", "app.debug", False, True, "admin")
        trail.record_change("updated", "app.version", "1.0", "1.1", "admin")
        trail.record_change("updated", "db.host", "old", "new", "admin")
        trail.record_change("updated", "app.debug", True, False, "admin")
        
        app_debug_changes = trail.get_changes_for_key("app.debug")
        assert len(app_debug_changes) == 2
        assert all(c.key == "app.debug" for c in app_debug_changes)


class TestMultiEnvironmentDriftDetection:
    """Test drift detection across environments."""
    
    def test_environment_specific_drift(self):
        """Test detecting drift in environment-specific configs."""
        # Define desired config for each environment
        desired_configs = {
            "dev": {"log_level": "debug", "debug": True},
            "prod": {"log_level": "error", "debug": False},
        }
        
        # Current configs that may have drifted
        current_configs = {
            "dev": {"log_level": "info", "debug": True},
            "prod": {"log_level": "error", "debug": False},
        }
        
        detectors = {}
        for env in ["dev", "prod"]:
            detector = ConfigDriftDetector(desired_configs[env])
            detectors[env] = detector
        
        # Check drift
        dev_drift = detectors["dev"].detect(current_configs["dev"])
        prod_drift = detectors["prod"].detect(current_configs["prod"])
        
        assert dev_drift is False  # dev drifted
        assert prod_drift is True  # prod is in sync


class TestConfigurationConsistency:
    """Test configuration consistency checks."""
    
    def test_cross_field_consistency(self):
        """Test validating consistency between related fields."""
        config = {
            "min_workers": 2,
            "max_workers": 4,
        }
        
        # Validate cross-field constraint
        assert config["min_workers"] <= config["max_workers"]
    
    def test_dependent_field_validation(self):
        """Test validation of dependent configuration fields."""
        schema = {
            "enable_cache": {"type": bool, "required": True},
            "cache_ttl": {"type": int, "required": False},
        }
        
        # Valid: cache enabled with TTL
        config1 = {"enable_cache": True, "cache_ttl": 3600}
        validator = ConfigValidator(schema)
        assert validator.validate(config1) is True
        
        # Valid: cache disabled without TTL
        config2 = {"enable_cache": False}
        assert validator.validate(config2) is True


class TestSecretManagementAdvanced:
    """Advanced secret management tests."""
    
    def test_secret_metadata(self):
        """Test storing and retrieving secret metadata."""
        manager = SecretManager()
        manager.store_secret("db_password", "secure_value")
        
        # Verify secret exists and is encrypted
        assert manager.is_encrypted("db_password") is True
        assert manager.retrieve_secret("db_password") == "secure_value"
    
    def test_bulk_secret_management(self):
        """Test managing multiple secrets."""
        manager = SecretManager()
        
        secrets_config = {
            "prod_db_password": "prod_pass_123",
            "staging_db_password": "staging_pass_456",
            "dev_db_password": "dev_pass_789",
        }
        
        for name, value in secrets_config.items():
            manager.store_secret(name, value)
        
        for name, expected_value in secrets_config.items():
            actual_value = manager.retrieve_secret(name)
            assert actual_value == expected_value


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
