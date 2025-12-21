"""
Deployment Configuration

This module provides configuration for deploying the reviewer agent
to various cloud platforms.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
import os


@dataclass
class DeploymentConfig:
    """Configuration for agent deployment."""
    
    # Platform
    platform: str = "aws-lambda"  # aws-lambda, gcp-functions, azure-functions
    
    # Runtime
    runtime: str = "python3.11"
    memory_mb: int = 512
    timeout_seconds: int = 300
    
    # Networking
    vpc_enabled: bool = False
    vpc_subnet_ids: List[str] = field(default_factory=list)
    security_group_ids: List[str] = field(default_factory=list)
    
    # Environment
    environment_variables: Dict[str, str] = field(default_factory=dict)
    
    # Scaling
    min_instances: int = 0
    max_instances: int = 10
    concurrency: int = 1
    
    # Monitoring
    enable_xray: bool = True
    enable_cloudwatch_logs: bool = True
    log_retention_days: int = 30
    
    # GitHub App
    github_app_id: Optional[str] = None
    github_app_private_key: Optional[str] = None
    github_webhook_secret: Optional[str] = None
    
    @classmethod
    def from_env(cls) -> "DeploymentConfig":
        """Create configuration from environment variables."""
        return cls(
            platform=os.environ.get("DEPLOYMENT_PLATFORM", "aws-lambda"),
            runtime=os.environ.get("RUNTIME", "python3.11"),
            memory_mb=int(os.environ.get("MEMORY_MB", "512")),
            timeout_seconds=int(os.environ.get("TIMEOUT_SECONDS", "300")),
            github_app_id=os.environ.get("CODEX_APP_ID"),
            github_app_private_key=os.environ.get("CODEX_PRIVATE_KEY"),
            github_webhook_secret=os.environ.get("CODEX_WEBHOOK_SECRET"),
        )
    
    def to_terraform_vars(self) -> Dict[str, any]:
        """Convert to Terraform variables format."""
        return {
            "function_name": "codex-quantum-reviewer",
            "runtime": self.runtime,
            "memory_size": self.memory_mb,
            "timeout": self.timeout_seconds,
            "environment_variables": self.environment_variables or {},
        }
    
    def to_cloudformation_params(self) -> List[Dict[str, str]]:
        """Convert to CloudFormation parameters format."""
        return [
            {"ParameterKey": "FunctionName", "ParameterValue": "codex-quantum-reviewer"},
            {"ParameterKey": "Runtime", "ParameterValue": self.runtime},
            {"ParameterKey": "MemorySize", "ParameterValue": str(self.memory_mb)},
            {"ParameterKey": "Timeout", "ParameterValue": str(self.timeout_seconds)},
        ]


# Default configurations for different environments
DEVELOPMENT = DeploymentConfig(
    platform="local",
    memory_mb=256,
    timeout_seconds=60,
    enable_xray=False,
    log_retention_days=7,
)

STAGING = DeploymentConfig(
    platform="aws-lambda",
    memory_mb=512,
    timeout_seconds=300,
    min_instances=1,
    max_instances=5,
    enable_xray=True,
    log_retention_days=14,
)

PRODUCTION = DeploymentConfig(
    platform="aws-lambda",
    memory_mb=512,
    timeout_seconds=300,
    min_instances=2,
    max_instances=20,
    concurrency=10,
    enable_xray=True,
    log_retention_days=90,
    vpc_enabled=True,
)
