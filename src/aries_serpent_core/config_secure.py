"""
Secure configuration module with environment variable handling.

This module demonstrates secure credential management to prevent
hardcoded secrets (CWE-798: Hardcoded Credentials).
"""

import os
import logging
from typing import Optional
from pathlib import Path

logger = logging.getLogger(__name__)


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
        
        Previous vulnerable code:
            DB_PASSWORD = "super_secret_password_123"  # ❌ EXPOSED!
            API_KEY = "sk-1234567890abcdef"            # ❌ EXPOSED!
        
        Secure implementation:
            DB_PASSWORD = os.environ['DB_PASSWORD']    # ✅ SECURE
            API_KEY = os.environ['API_KEY']            # ✅ SECURE
        
        Args:
            var_name: Name of environment variable
            
        Returns:
            Value of environment variable
            
        Raises:
            ConfigurationError: If environment variable is not set
        """
        value = os.environ.get(var_name)
        
        if value is None:
            raise ConfigurationError(
                f"Required environment variable '{var_name}' is not set. "
                f"Please set it before running the application."
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
        self.password = SecureConfig.get_required_env('DB_PASSWORD')  # ✅ NOT hardcoded
        self.database = SecureConfig.get_required_env('DB_NAME')

    def get_connection_string(self) -> str:
        """
        Get database connection string.
        
        Returns:
            Connection string for database connection
        """
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"


class APIConfig:
    """API configuration with secure credential handling."""

    def __init__(self):
        """Initialize API config from environment variables."""
        # ✅ SECURE: Load all secrets from environment
        self.api_key = SecureConfig.get_required_env('API_KEY')  # ✅ NOT hardcoded
        self.api_secret = SecureConfig.get_required_env('API_SECRET')  # ✅ NOT hardcoded
        self.api_url = SecureConfig.get_required_env('API_URL')
        self.timeout = int(SecureConfig.get_optional_env('API_TIMEOUT', '30'))

    def get_headers(self) -> dict:
        """
        Get API request headers with authentication.
        
        Returns:
            Headers dictionary with API key
        """
        return {
            'Authorization': f'******',
            'Content-Type': 'application/json',
        }


class AWSConfig:
    """AWS configuration with secure credential handling."""

    def __init__(self):
        """Initialize AWS config from environment variables."""
        # ✅ SECURE: Use AWS environment variables (standard AWS SDK approach)
        self.access_key = SecureConfig.get_required_env('AWS_ACCESS_KEY_ID')
        self.secret_key = SecureConfig.get_required_env('AWS_SECRET_ACCESS_KEY')
        self.region = SecureConfig.get_optional_env('AWS_REGION', 'us-east-1')
        self.s3_bucket = SecureConfig.get_optional_env('AWS_S3_BUCKET')

    def get_boto3_session(self):
        """
        Get boto3 session with credentials.
        
        Returns:
            Configured boto3 Session object
        """
        import boto3
        
        return boto3.Session(
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            region_name=self.region,
        )


class DotenvLoader:
    """
    Load environment variables from .env file (development only).
    
    ⚠️ IMPORTANT: Only use for development!
    - NEVER commit .env to version control
    - Add .env to .gitignore
    - Use environment variables or secrets manager in production
    """

    @staticmethod
    def load_dotenv(dotenv_path: str = '.env') -> None:
        """
        Load environment variables from .env file.
        
        Args:
            dotenv_path: Path to .env file
        """
        try:
            from dotenv import load_dotenv as _load_dotenv
            
            if Path(dotenv_path).exists():
                _load_dotenv(dotenv_path)
                logger.info(f"Loaded environment variables from {dotenv_path}")
            else:
                logger.warning(f".env file not found at {dotenv_path}")
        except ImportError:
            logger.warning(
                "python-dotenv not installed. "
                "Install with: pip install python-dotenv"
            )


class SecretsManagerConfig:
    """
    Configuration using AWS Secrets Manager (production).
    
    BEST PRACTICE for production environments:
    - Centralized secret management
    - Automatic rotation
    - Audit logging
    - IAM-based access control
    """

    def __init__(self, secret_name: str, region: str = 'us-east-1'):
        """
        Initialize secrets manager config.
        
        Args:
            secret_name: Name of secret in AWS Secrets Manager
            region: AWS region
        """
        self.secret_name = secret_name
        self.region = region
        self._cached_secret = None

    def get_secret(self) -> dict:
        """
        Retrieve secret from AWS Secrets Manager.
        
        Returns:
            Secret dictionary
            
        Raises:
            ConfigurationError: If secret cannot be retrieved
        """
        if self._cached_secret is not None:
            return self._cached_secret

        try:
            import boto3
            
            client = boto3.client('secretsmanager', region_name=self.region)
            response = client.get_secret_value(SecretId=self.secret_name)
            
            # Handle both binary and string secrets
            if 'SecretString' in response:
                import json
                secret = json.loads(response['SecretString'])
            else:
                secret = response['SecretBinary']
            
            self._cached_secret = secret
            return secret
        
        except Exception as e:
            raise ConfigurationError(
                f"Failed to retrieve secret '{self.secret_name}' from AWS Secrets Manager: {e}"
            ) from e

    def get_credential(self, key: str) -> str:
        """
        Get specific credential from secret.
        
        Args:
            key: Credential key
            
        Returns:
            Credential value
        """
        secret = self.get_secret()
        
        if key not in secret:
            raise ConfigurationError(
                f"Credential '{key}' not found in secret '{self.secret_name}'"
            )
        
        return secret[key]


# ============================================================================
# VULNERABILITY ANALYSIS: CWE-798 Hardcoded Credentials
# ============================================================================

# VULNERABLE PATTERN (❌ DO NOT USE):
# ----
# DB_PASSWORD = "super_secret_password_123"
# API_KEY = "sk-1234567890abcdef"
# AWS_SECRET = "aws_secret_1234567890abcdef"
#
# Risks:
#   - Exposed in source code repositories
#   - Visible in version control history
#   - Exposed in build artifacts
#   - Compromised if repository is leaked
#   - Cannot be rotated without code changes
#   - Compliance violations (PCI-DSS, HIPAA, SOC2)
#
# Result: Complete compromise of external services!

# SECURE PATTERN (✅ USE THIS):
# ----
# Development:
#   1. Use .env file (add to .gitignore)
#   2. Load with: from dotenv import load_dotenv; load_dotenv()
#   3. Access with: os.environ['DB_PASSWORD']
#
# Production:
#   1. Use AWS Secrets Manager, Azure Key Vault, etc.
#   2. Rotate secrets automatically
#   3. Audit access logs
#   4. Use IAM roles for authentication

# KEY PRINCIPLES:
# 1. NEVER hardcode credentials in source code
# 2. Use environment variables for local development
# 3. Add .env to .gitignore
# 4. Use secrets manager for production
# 5. Implement credential rotation
# 6. Audit all secret access
# 7. Use IAM roles instead of credentials when possible
# 8. Store secrets in encrypted vaults

# SETUP INSTRUCTIONS:
# 
# 1. Create .env file (development only):
#    DB_HOST=localhost
#    DB_USER=admin
#    DB_PASSWORD=secure_password_here
#    API_KEY=sk-1234567890abcdef
#
# 2. Add to .gitignore:
#    .env
#    .env.local
#    *.key
#    *.pem
#
# 3. In production, set environment variables:
#    export DB_PASSWORD='production_password'
#    export API_KEY='production_api_key'
#
# 4. Or use secrets manager:
#    aws secretsmanager create-secret --name db-password --secret-string 'password'
