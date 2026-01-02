"""
Tests for QuantumConfig class.

This test suite validates the quantum configuration management system,
including environment variable parsing, feature flag validation, and
backward compatibility.
"""

import os
import pytest
from cognitive_brain.quantum.config import QuantumConfig


class TestQuantumConfigDefaults:
    """Test default configuration values."""
    
    def test_default_all_disabled(self):
        """Test that all features are disabled by default."""
        config = QuantumConfig()
        
        assert config.quantum_mode is False
        assert config.superposition is False
        assert config.entanglement is False
        assert config.uncertainty is False
        assert config.wave_collapse is False
        assert config.rollout_percentage == 0
    
    def test_from_env_empty_environment(self, monkeypatch):
        """Test from_env() with no environment variables set."""
        # Clear all quantum-related env vars
        for key in list(os.environ.keys()):
            if key.startswith("CODEX_QUANTUM"):
                monkeypatch.delenv(key, raising=False)
        
        config = QuantumConfig.from_env()
        
        assert config.quantum_mode is False
        assert config.superposition is False
        assert config.entanglement is False
        assert config.uncertainty is False
        assert config.wave_collapse is False
        assert config.rollout_percentage == 0


class TestQuantumConfigEnvironmentParsing:
    """Test environment variable parsing."""
    
    def test_parse_quantum_mode_true(self, monkeypatch):
        """Test parsing CODEX_QUANTUM_MODE=true."""
        monkeypatch.setenv("CODEX_QUANTUM_MODE", "true")
        config = QuantumConfig.from_env()
        
        assert config.quantum_mode is True
    
    def test_parse_quantum_mode_various_true_values(self, monkeypatch):
        """Test that various true-like values are accepted."""
        true_values = ["true", "True", "TRUE", "1", "yes", "Yes", "on", "ON", "enabled"]
        
        for value in true_values:
            monkeypatch.setenv("CODEX_QUANTUM_MODE", value)
            config = QuantumConfig.from_env()
            assert config.quantum_mode is True, f"Failed for value: {value}"
    
    def test_parse_quantum_mode_false_values(self, monkeypatch):
        """Test that false-like values result in disabled mode."""
        false_values = ["false", "False", "FALSE", "0", "no", "off", "disabled", "random"]
        
        for value in false_values:
            monkeypatch.setenv("CODEX_QUANTUM_MODE", value)
            config = QuantumConfig.from_env()
            assert config.quantum_mode is False, f"Failed for value: {value}"
    
    def test_parse_individual_features(self, monkeypatch):
        """Test parsing individual feature flags."""
        monkeypatch.setenv("CODEX_QUANTUM_MODE", "true")
        monkeypatch.setenv("CODEX_QUANTUM_SUPERPOSITION", "true")
        monkeypatch.setenv("CODEX_QUANTUM_ENTANGLEMENT", "1")
        monkeypatch.setenv("CODEX_QUANTUM_UNCERTAINTY", "yes")
        monkeypatch.setenv("CODEX_QUANTUM_WAVE_COLLAPSE", "on")
        
        config = QuantumConfig.from_env()
        
        assert config.quantum_mode is True
        assert config.superposition is True
        assert config.entanglement is True
        assert config.uncertainty is True
        assert config.wave_collapse is True
    
    def test_parse_rollout_percentage(self, monkeypatch):
        """Test parsing CODEX_QUANTUM_ROLLOUT_PCT."""
        monkeypatch.setenv("CODEX_QUANTUM_MODE", "true")
        monkeypatch.setenv("CODEX_QUANTUM_ROLLOUT_PCT", "50")
        
        config = QuantumConfig.from_env()
        
        assert config.rollout_percentage == 50
    
    def test_parse_rollout_percentage_invalid(self, monkeypatch):
        """Test parsing invalid rollout percentage falls back to default."""
        monkeypatch.setenv("CODEX_QUANTUM_MODE", "true")
        monkeypatch.setenv("CODEX_QUANTUM_ROLLOUT_PCT", "invalid")
        
        config = QuantumConfig.from_env()
        
        assert config.rollout_percentage == 0


class TestQuantumConfigValidation:
    """Test configuration validation."""
    
    def test_invalid_rollout_percentage_above_100(self):
        """Test that rollout percentage > 100 raises ValueError."""
        with pytest.raises(ValueError, match="rollout_percentage must be 0-100"):
            QuantumConfig(quantum_mode=True, rollout_percentage=101)
    
    def test_invalid_rollout_percentage_negative(self):
        """Test that negative rollout percentage raises ValueError."""
        with pytest.raises(ValueError, match="rollout_percentage must be 0-100"):
            QuantumConfig(quantum_mode=True, rollout_percentage=-1)
    
    def test_features_enabled_without_quantum_mode(self):
        """Test that individual features cannot be enabled without quantum_mode."""
        with pytest.raises(ValueError, match="Cannot enable individual features"):
            QuantumConfig(
                quantum_mode=False,
                superposition=True
            )
    
    def test_features_disabled_when_quantum_mode_false(self, monkeypatch):
        """Test that features remain disabled when quantum_mode is false."""
        monkeypatch.setenv("CODEX_QUANTUM_MODE", "false")
        monkeypatch.setenv("CODEX_QUANTUM_SUPERPOSITION", "true")
        monkeypatch.setenv("CODEX_QUANTUM_ENTANGLEMENT", "true")
        
        config = QuantumConfig.from_env()
        
        assert config.quantum_mode is False
        assert config.superposition is False
        assert config.entanglement is False


class TestQuantumConfigMethods:
    """Test configuration methods."""
    
    def test_is_enabled_all_features(self):
        """Test is_enabled() for all features."""
        config = QuantumConfig(
            quantum_mode=True,
            superposition=True,
            entanglement=True,
            uncertainty=True,
            wave_collapse=True
        )
        
        assert config.is_enabled("superposition") is True
        assert config.is_enabled("entanglement") is True
        assert config.is_enabled("uncertainty") is True
        assert config.is_enabled("wave_collapse") is True
    
    def test_is_enabled_mixed_features(self):
        """Test is_enabled() with some features enabled."""
        config = QuantumConfig(
            quantum_mode=True,
            superposition=True,
            entanglement=False,
            uncertainty=True,
            wave_collapse=False
        )
        
        assert config.is_enabled("superposition") is True
        assert config.is_enabled("entanglement") is False
        assert config.is_enabled("uncertainty") is True
        assert config.is_enabled("wave_collapse") is False
    
    def test_is_enabled_invalid_feature(self):
        """Test is_enabled() with invalid feature name."""
        config = QuantumConfig(quantum_mode=True)
        
        with pytest.raises(ValueError, match="Invalid feature"):
            config.is_enabled("nonexistent_feature")
    
    def test_is_enabled_when_quantum_mode_false(self):
        """Test is_enabled() always returns False when quantum_mode is False."""
        config = QuantumConfig(quantum_mode=False)
        
        assert config.is_enabled("superposition") is False
        assert config.is_enabled("entanglement") is False
        assert config.is_enabled("uncertainty") is False
        assert config.is_enabled("wave_collapse") is False
    
    def test_to_dict(self):
        """Test to_dict() conversion."""
        config = QuantumConfig(
            quantum_mode=True,
            superposition=True,
            entanglement=False,
            uncertainty=True,
            wave_collapse=False,
            rollout_percentage=50
        )
        
        result = config.to_dict()
        
        assert result == {
            "quantum_mode": True,
            "superposition": True,
            "entanglement": False,
            "uncertainty": True,
            "wave_collapse": False,
            "rollout_percentage": 50,
        }
    
    def test_repr(self):
        """Test __repr__() string representation."""
        config = QuantumConfig(
            quantum_mode=True,
            superposition=True,
            entanglement=True,
            rollout_percentage=25
        )
        
        repr_str = repr(config)
        
        assert "QuantumConfig" in repr_str
        assert "mode=True" in repr_str
        assert "rollout=25%" in repr_str
        assert "superposition" in repr_str
        assert "entanglement" in repr_str


class TestBackwardCompatibility:
    """Test backward compatibility guarantees."""
    
    def test_default_config_has_no_impact(self):
        """Test that default config with all features disabled is safe."""
        config = QuantumConfig()
        
        # Should not raise any exceptions
        assert not config.quantum_mode
        assert not any([
            config.superposition,
            config.entanglement,
            config.uncertainty,
            config.wave_collapse
        ])
    
    def test_from_env_without_vars_has_no_impact(self, monkeypatch):
        """Test that from_env() without env vars is backward compatible."""
        # Ensure no quantum env vars are set
        for key in list(os.environ.keys()):
            if key.startswith("CODEX_QUANTUM"):
                monkeypatch.delenv(key, raising=False)
        
        config = QuantumConfig.from_env()
        
        # Should behave exactly like default config
        assert not config.quantum_mode
        assert config.rollout_percentage == 0


class TestIntegrationScenarios:
    """Test realistic integration scenarios."""
    
    def test_gradual_rollout_scenario(self, monkeypatch):
        """Test gradual rollout with 10% traffic."""
        monkeypatch.setenv("CODEX_QUANTUM_MODE", "true")
        monkeypatch.setenv("CODEX_QUANTUM_SUPERPOSITION", "true")
        monkeypatch.setenv("CODEX_QUANTUM_ROLLOUT_PCT", "10")
        
        config = QuantumConfig.from_env()
        
        assert config.quantum_mode is True
        assert config.superposition is True
        assert config.rollout_percentage == 10
    
    def test_full_production_scenario(self, monkeypatch):
        """Test full production with all features enabled."""
        monkeypatch.setenv("CODEX_QUANTUM_MODE", "true")
        monkeypatch.setenv("CODEX_QUANTUM_SUPERPOSITION", "true")
        monkeypatch.setenv("CODEX_QUANTUM_ENTANGLEMENT", "true")
        monkeypatch.setenv("CODEX_QUANTUM_UNCERTAINTY", "true")
        monkeypatch.setenv("CODEX_QUANTUM_WAVE_COLLAPSE", "true")
        monkeypatch.setenv("CODEX_QUANTUM_ROLLOUT_PCT", "100")
        
        config = QuantumConfig.from_env()
        
        assert config.quantum_mode is True
        assert all([
            config.superposition,
            config.entanglement,
            config.uncertainty,
            config.wave_collapse
        ])
        assert config.rollout_percentage == 100
    
    def test_emergency_disable_scenario(self, monkeypatch):
        """Test emergency disable by setting quantum_mode=false."""
        monkeypatch.setenv("CODEX_QUANTUM_MODE", "false")
        monkeypatch.setenv("CODEX_QUANTUM_SUPERPOSITION", "true")
        monkeypatch.setenv("CODEX_QUANTUM_ENTANGLEMENT", "true")
        
        config = QuantumConfig.from_env()
        
        # All features should be disabled due to quantum_mode=false
        assert config.quantum_mode is False
        assert config.superposition is False
        assert config.entanglement is False
