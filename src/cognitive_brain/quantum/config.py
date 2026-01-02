"""
Quantum Configuration Management

Provides centralized configuration for quantum-inspired features with
environment variable-based feature flags and validation.
"""

import os
from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class QuantumConfig:
    """
    Configuration for quantum-inspired features.
    
    All features are disabled by default for backward compatibility.
    Enable via environment variables:
    - CODEX_QUANTUM_MODE: Master toggle for all quantum features
    - CODEX_QUANTUM_SUPERPOSITION: Enable parallel decision exploration
    - CODEX_QUANTUM_ENTANGLEMENT: Enable correlated agent state management
    - CODEX_QUANTUM_UNCERTAINTY: Enable adaptive test coverage
    - CODEX_QUANTUM_WAVE_COLLAPSE: Enable accelerated pattern learning
    
    Example:
        >>> config = QuantumConfig.from_env()
        >>> if config.is_enabled("superposition"):
        ...     # Use quantum superposition
        ...     pass
    """
    
    # Master toggle - if False, all features are disabled
    quantum_mode: bool = False
    
    # Individual feature flags
    superposition: bool = False
    entanglement: bool = False
    uncertainty: bool = False
    wave_collapse: bool = False
    
    # Rollout percentage (0-100) for gradual feature enablement
    rollout_percentage: int = 0
    
    def __post_init__(self):
        """Validate configuration after initialization."""
        self._validate()
    
    def _validate(self) -> None:
        """
        Validate configuration values.
        
        Raises:
            ValueError: If configuration is invalid
        """
        # Validate rollout percentage
        if not 0 <= self.rollout_percentage <= 100:
            raise ValueError(
                f"rollout_percentage must be 0-100, got {self.rollout_percentage}"
            )
        
        # If quantum_mode is False, all features should be disabled
        if not self.quantum_mode:
            if any([self.superposition, self.entanglement, 
                   self.uncertainty, self.wave_collapse]):
                raise ValueError(
                    "Cannot enable individual features when quantum_mode is False. "
                    "Set CODEX_QUANTUM_MODE=true first."
                )
    
    @classmethod
    def from_env(cls) -> "QuantumConfig":
        """
        Load configuration from environment variables.
        
        Returns:
            QuantumConfig instance with values from environment
            
        Environment Variables:
            CODEX_QUANTUM_MODE: Master toggle (default: false)
            CODEX_QUANTUM_SUPERPOSITION: Enable superposition (default: false)
            CODEX_QUANTUM_ENTANGLEMENT: Enable entanglement (default: false)
            CODEX_QUANTUM_UNCERTAINTY: Enable uncertainty (default: false)
            CODEX_QUANTUM_WAVE_COLLAPSE: Enable wave collapse (default: false)
            CODEX_QUANTUM_ROLLOUT_PCT: Rollout percentage 0-100 (default: 0)
        """
        def parse_bool(value: Optional[str], default: bool = False) -> bool:
            """Parse boolean from environment variable string."""
            if value is None:
                return default
            return value.lower() in ("true", "1", "yes", "on", "enabled")
        
        def parse_int(value: Optional[str], default: int) -> int:
            """Parse integer from environment variable string."""
            if value is None:
                return default
            try:
                return int(value)
            except ValueError:
                return default
        
        # Read environment variables
        quantum_mode = parse_bool(os.getenv("CODEX_QUANTUM_MODE"), False)
        
        return cls(
            quantum_mode=quantum_mode,
            superposition=parse_bool(
                os.getenv("CODEX_QUANTUM_SUPERPOSITION"), 
                False
            ) if quantum_mode else False,
            entanglement=parse_bool(
                os.getenv("CODEX_QUANTUM_ENTANGLEMENT"),
                False
            ) if quantum_mode else False,
            uncertainty=parse_bool(
                os.getenv("CODEX_QUANTUM_UNCERTAINTY"),
                False
            ) if quantum_mode else False,
            wave_collapse=parse_bool(
                os.getenv("CODEX_QUANTUM_WAVE_COLLAPSE"),
                False
            ) if quantum_mode else False,
            rollout_percentage=parse_int(
                os.getenv("CODEX_QUANTUM_ROLLOUT_PCT"),
                0
            ),
        )
    
    def is_enabled(self, feature: str) -> bool:
        """
        Check if a specific quantum feature is enabled.
        
        Args:
            feature: Feature name ("superposition", "entanglement", 
                    "uncertainty", "wave_collapse")
        
        Returns:
            True if feature is enabled, False otherwise
            
        Raises:
            ValueError: If feature name is invalid
        """
        if not self.quantum_mode:
            return False
        
        feature_map = {
            "superposition": self.superposition,
            "entanglement": self.entanglement,
            "uncertainty": self.uncertainty,
            "wave_collapse": self.wave_collapse,
        }
        
        if feature not in feature_map:
            raise ValueError(
                f"Invalid feature: {feature}. "
                f"Valid features: {list(feature_map.keys())}"
            )
        
        return feature_map[feature]
    
    def to_dict(self) -> Dict[str, any]:
        """
        Convert configuration to dictionary.
        
        Returns:
            Dictionary representation of configuration
        """
        return {
            "quantum_mode": self.quantum_mode,
            "superposition": self.superposition,
            "entanglement": self.entanglement,
            "uncertainty": self.uncertainty,
            "wave_collapse": self.wave_collapse,
            "rollout_percentage": self.rollout_percentage,
        }
    
    def __repr__(self) -> str:
        """String representation of configuration."""
        enabled_features = [
            feature for feature in ["superposition", "entanglement", 
                                   "uncertainty", "wave_collapse"]
            if self.is_enabled(feature)
        ]
        return (
            f"QuantumConfig(mode={self.quantum_mode}, "
            f"features={enabled_features}, "
            f"rollout={self.rollout_percentage}%)"
        )
