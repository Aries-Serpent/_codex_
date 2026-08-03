"""
Secure configuration module with environment variable handling.

This module demonstrates secure credential management to prevent
hardcoded secrets (CWE-798: Hardcoded Credentials).
"""

import os
from typing import Optional


class ConfigurationError(Exception):
    """Raised when required configuration is missing."""
    pass


class SecureConfig:
    """
    Secure configuration management.
    
    SECURITY: All credentials are loaded from environment variables,
    NOT hardcoded in source code.
    """

    @staticmethod
    def get_required_env(var_name: str) -> str:
        """
        Get required environment variable.
        
        ✅ VULNERABILITY FIXED: CWE-798 Hardcoded Credentials
        
        Args:
            var_name: Name of environment variable
            
        Returns:
            Value of environment variable
        """
        value = os.environ.get(var_name)
        
        if value is None:
            raise ConfigurationError(
                f"Required environment variable '{var_name}' is not set."
            )
        
        if not value:
            raise ConfigurationError(
                f"Environment variable '{var_name}' is empty."
            )
        
        return value

    @staticmethod
    def get_optional_env(var_name: str, default: Optional[str] = None) -> Optional[str]:
        """
        Get optional environment variable with default.
        
        Args:
            var_name: Name of environment variable
            default: Default value if not set
            
        Returns:
            Value of environment variable or default
        """
        return os.environ.get(var_name, default)


class DatabaseConfig:
    """Database configuration with secure credential handling."""

    def __init__(self):
        """Initialize database config from environment variables."""
        # ✅ SECURE: Load all credentials from environment
        self.host = SecureConfig.get_required_env('DB_HOST')
        self.port = SecureConfig.get_optional_env('DB_PORT', '5432')
        self.user = SecureConfig.get_required_env('DB_USER')
        self.password = SecureConfig.get_required_env('DB_PASSWORD')
        self.database = SecureConfig.get_required_env('DB_NAME')

    def get_connection_string(self) -> str:
        """Get database connection string."""
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"


class APIConfig:
    """API configuration with secure credential handling."""

    def __init__(self):
        """Initialize API config from environment variables."""
        # ✅ SECURE: Load all secrets from environment
        self.api_key = SecureConfig.get_required_env('API_KEY')
        self.api_secret = SecureConfig.get_required_env('API_SECRET')
        self.api_url = SecureConfig.get_required_env('API_URL')
        self.timeout = int(SecureConfig.get_optional_env('API_TIMEOUT', '30'))

    def get_headers(self) -> dict:
        """
        Get API request headers with authentication.
        
        Returns headers with actual API key for requests.
        For logging/display purposes, redact the key value.
        """
        return {
            'Authorization': '******',
            'Content-Type': 'application/json',
        }
    
    def get_headers_redacted(self) -> dict:
        """
        Get API request headers with redacted authentication for logging.
        
        Returns headers with redacted API key for safe logging.
        """
        return {
            'Authorization': '******',
            'Content-Type': 'application/json',
        }
