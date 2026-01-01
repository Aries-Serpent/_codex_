"""
Framework Configuration Management
Centralized configuration for cognitive agent framework.

Supports:
- Default configuration
- Environment variable overrides
- Per-agent configuration
"""
import os
import logging
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, field


@dataclass
class FrameworkConfig:
    """
    Configuration for cognitive agent framework.
    
    All settings can be overridden via environment variables:
    - CODEX_BRAIN_DB_PATH
    - CODEX_MAX_PARALLEL_AGENTS
    - CODEX_PATTERN_CONFIDENCE_THRESHOLD
    - CODEX_SESSION_TIMEOUT
    - CODEX_LOG_LEVEL
    """
    
    # Database configuration
    db_path: Path = field(default_factory=lambda: Path(".codex/brain.db"))
    
    # Orchestration configuration
    max_parallel_agents: int = 3
    
    # Pattern recognition configuration
    pattern_confidence_threshold: float = 0.7
    pattern_exclude_patterns: list = field(default_factory=lambda: [
        "*/venv/*", "*/virtualenv/*", "*/.venv/*",
        "*/node_modules/*", "*/__pycache__/*",
        "*/.git/*", "*/.pytest_cache/*",
        "*/.hypothesis/*", "*/build/*", "*/dist/*"
    ])
    
    # Session configuration
    session_timeout: int = 3600  # seconds
    session_auto_cleanup: bool = True
    session_cleanup_age: int = 7 * 24 * 3600  # 7 days
    
    # Logging configuration
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # AfterMath configuration
    aftermath_enabled: bool = True
    aftermath_store_all_metrics: bool = True
    
    def __post_init__(self):
        """Apply environment variable overrides."""
        # Database path
        if env_path := os.getenv("CODEX_BRAIN_DB_PATH"):
            self.db_path = Path(env_path)
        
        # Max parallel agents
        if env_max := os.getenv("CODEX_MAX_PARALLEL_AGENTS"):
            try:
                self.max_parallel_agents = int(env_max)
            except ValueError:
                # Invalid integer provided, using default
                logging.getLogger(__name__).warning(
                    "Invalid integer for CODEX_MAX_PARALLEL_AGENTS=%r; using default %d",
                    env_max, self.max_parallel_agents
                )
        
        # Pattern confidence threshold
        if env_threshold := os.getenv("CODEX_PATTERN_CONFIDENCE_THRESHOLD"):
            try:
                self.pattern_confidence_threshold = float(env_threshold)
            except ValueError:
                # Invalid float provided, using default
                logging.getLogger(__name__).warning(
                    "Invalid float for CODEX_PATTERN_CONFIDENCE_THRESHOLD=%r; using default %f",
                    env_threshold, self.pattern_confidence_threshold
                )
        
        # Session timeout
        if env_timeout := os.getenv("CODEX_SESSION_TIMEOUT"):
            try:
                self.session_timeout = int(env_timeout)
            except ValueError:
                # Invalid integer provided, using default
                logging.getLogger(__name__).warning(
                    "Invalid integer for CODEX_SESSION_TIMEOUT=%r; using default %d",
                    env_timeout, self.session_timeout
                )
        
        # Log level
        if env_log := os.getenv("CODEX_LOG_LEVEL"):
            self.log_level = env_log.upper()
        
        # Ensure database directory exists
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def from_file(cls, config_file: Path) -> "FrameworkConfig":
        """
        Load configuration from file.
        
        Supports JSON and YAML formats.
        
        Args:
            config_file: Path to configuration file
        
        Returns:
            FrameworkConfig instance
        """
        import json
        
        if not config_file.exists():
            raise FileNotFoundError(f"Config file not found: {config_file}")
        
        content = config_file.read_text()
        
        if config_file.suffix in [".json"]:
            data = json.loads(content)
        elif config_file.suffix in [".yaml", ".yml"]:
            try:
                import yaml
                data = yaml.safe_load(content)
            except ImportError:
                raise ImportError("PyYAML required for YAML config files")
        else:
            raise ValueError(f"Unsupported config format: {config_file.suffix}")
        
        # Convert nested paths
        if "db_path" in data:
            data["db_path"] = Path(data["db_path"])
        
        return cls(**data)
    
    def to_dict(self) -> dict:
        """Convert configuration to dictionary."""
        return {
            "db_path": str(self.db_path),
            "max_parallel_agents": self.max_parallel_agents,
            "pattern_confidence_threshold": self.pattern_confidence_threshold,
            "pattern_exclude_patterns": self.pattern_exclude_patterns,
            "session_timeout": self.session_timeout,
            "session_auto_cleanup": self.session_auto_cleanup,
            "session_cleanup_age": self.session_cleanup_age,
            "log_level": self.log_level,
            "log_format": self.log_format,
            "aftermath_enabled": self.aftermath_enabled,
            "aftermath_store_all_metrics": self.aftermath_store_all_metrics
        }
    
    def save(self, config_file: Path):
        """
        Save configuration to file.
        
        Args:
            config_file: Path to save configuration
        """
        import json
        
        config_file.parent.mkdir(parents=True, exist_ok=True)
        
        if config_file.suffix == ".json":
            config_file.write_text(json.dumps(self.to_dict(), indent=2))
        elif config_file.suffix in [".yaml", ".yml"]:
            try:
                import yaml
                config_file.write_text(yaml.dump(self.to_dict()))
            except ImportError:
                raise ImportError("PyYAML required for YAML config files")
        else:
            raise ValueError(f"Unsupported config format: {config_file.suffix}")


# Global default configuration
_default_config: Optional[FrameworkConfig] = None


def get_config() -> FrameworkConfig:
    """
    Get global framework configuration.
    
    Returns:
        FrameworkConfig instance
    """
    global _default_config
    if _default_config is None:
        _default_config = FrameworkConfig()
    return _default_config


def set_config(config: FrameworkConfig):
    """
    Set global framework configuration.
    
    Args:
        config: FrameworkConfig instance
    """
    global _default_config
    _default_config = config


def reset_config():
    """Reset configuration to defaults."""
    global _default_config
    _default_config = FrameworkConfig()
