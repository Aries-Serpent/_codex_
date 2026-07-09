"""Configuration module with secure credential handling - SECURE VERSION.

This module demonstrates how to handle configuration securely
to prevent hardcoded credentials vulnerabilities (CWE-798).

Security Model:
- Credentials are loaded from environment variables, not hardcoded
- Configuration files don't contain secrets
- Secrets are injected at runtime from secure sources
- Sensible defaults don't expose security-critical information
"""

import logging
import os
from typing import Optional

logger = logging.getLogger(__name__)


# SECURE: Load credentials from environment, not hardcoded
class Config:
    """Application configuration with secure credential handling."""

    def __init__(self):
        """Initialize configuration from environment variables."""
        # SECURE: Database credentials come from environment, not hardcoded
        self.db_host = os.environ.get("DB_HOST", "localhost")
        self.db_port = os.environ.get("DB_PORT", "5432")
        # IMPORTANT: Required credentials must be provided via environment variables
        self.db_user = os.environ.get("DB_USER")  # No default; validation enforces requirement
        self.db_password = os.environ.get("DB_PASSWORD")  # No default; validation enforces requirement
 
        # SECURE: API keys come from environment
        self.api_key = os.environ.get("API_KEY")  # No default; validation enforces requirement
        self.secret_key = os.environ.get("SECRET_KEY")  # No default; validation enforces requirement

        # SECURE: Non-sensitive configuration can have defaults
        self.debug = os.environ.get("DEBUG", "false").lower() == "true"
        self.log_level = os.environ.get("LOG_LEVEL", "INFO")
        self.max_connections = int(os.environ.get("MAX_CONNECTIONS", "10"))

    def validate(self) -> bool:
        """Validate that all required configuration is present.

        Returns:
            True if valid, raises ValueError otherwise

        Raises:
            ValueError: If required environment variables are missing
        """
        required_vars = ["DB_USER", "DB_PASSWORD", "API_KEY", "SECRET_KEY"]
        missing = []

        for var in required_vars:
            if not os.environ.get(var):
                missing.append(var)

        if missing:
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")

        return True

    def get_db_connection_string(self) -> str:
        """Get database connection string safely.

        Returns:
            Connection string (password is loaded from environment)

        Raises:
            ValueError: If required credentials are missing
        """
        if not self.db_user or not self.db_password:
            raise ValueError("Database credentials not configured")

        # SECURE: Password comes from environment, not hardcoded
        return f"postgresql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/mydb"

    def __str__(self) -> str:
        """Return string representation without exposing secrets.

        Returns:
            String representation (passwords are masked)
        """
        return (
            f"Config("
            f"db_host={self.db_host}, "
            f"db_port={self.db_port}, "
            f"db_user={self.db_user}, "
            f"debug={self.debug})"
        )

    def __repr__(self) -> str:
        """Return representation without exposing secrets.

        Returns:
            String representation (passwords are masked)
        """
        return self.__str__()


# Singleton instance
_config: Optional[Config] = None


def get_config() -> Config:
    """Get configuration singleton.

    Returns:
        Global Config instance

    Raises:
        ValueError: If required environment variables are not set
    """
    global _config
    if _config is None:
        _config = Config()
        _config.validate()
        logger.info("Configuration loaded successfully")
    return _config


# SECURITY BEST PRACTICES
# =======================
#
# 1. NEVER hardcode credentials:
#    ✗ WRONG:
#        DB_PASSWORD = "my-secret-password"
#        API_KEY = "sk-1234567890"
#
#    ✓ CORRECT:
#        DB_PASSWORD = os.environ.get("DB_PASSWORD")
#        API_KEY = os.environ.get("API_KEY")
#
# 2. Use environment-specific configuration files (not in git):
#    - .env (local development) - ADD TO .gitignore
#    - .env.production (production, pull from secure vault)
#    - Never commit .env files
#
# 3. Use secrets management systems:
#    - GitHub Secrets (for CI/CD)
#    - AWS Secrets Manager
#    - HashiCorp Vault
#    - Kubernetes Secrets
#
# 4. Rotate secrets regularly:
#    - Change passwords/keys periodically
#    - Immediately rotate compromised credentials
#
# 5. Audit credential access:
#    - Log who accessed credentials and when
#    - Never log the actual credential values
#    - Monitor for unauthorized access attempts
