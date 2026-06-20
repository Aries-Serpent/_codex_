#!/usr/bin/env python3
"""
Validate registry configuration against discovered patterns.

This script validates registry configurations by checking them against
discovered best practices and generating confidence scores.
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import logging
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class RegistryValidator:
    """Validate registry configuration against patterns."""

    def __init__(self, patterns_file: Optional[Path] = None):
        """Initialize validator."""
        self.patterns = self._load_patterns(patterns_file)
        self.validation_timestamp = datetime.utcnow().isoformat() + "Z"
        self.confidence_threshold = 0.80

    def _load_patterns(self, patterns_file: Optional[Path]) -> Dict[str, Any]:
        """Load patterns from file or return default patterns."""
        if patterns_file and patterns_file.exists():
            try:
                with open(patterns_file, "r") as f:
                    data = json.load(f)
                    return data.get("patterns", {})
            except Exception as e:
                logger.warning(f"Failed to load patterns file: {e}")
        
        # Return default patterns if file not found
        return self._get_default_patterns()

    @staticmethod
    def _get_default_patterns() -> Dict[str, Any]:
        """Get default patterns."""
        return {
            "dockerhub": {
                "registry_type": "dockerhub",
                "endpoint": "docker.io",
                "best_practices": [
                    "Use official Docker images when available",
                    "Pin image tags to specific versions",
                    "Implement rate limiting awareness",
                    "Use pull-through cache registry",
                    "Authenticate even for public images",
                    "Use image scanning",
                ],
                "required_fields": ["username", "password"],
                "authentication_method": "username_password",
            },
            "ghcr": {
                "registry_type": "ghcr",
                "endpoint": "ghcr.io",
                "best_practices": [
                    "Use GitHub token with packages:write scope",
                    "Organize images by organization/repository",
                    "Leverage GitHub Actions integration",
                    "Use container signing with Sigstore",
                    "Implement vulnerability scanning via GHAS",
                    "Configure SBOM generation",
                ],
                "required_fields": ["github_token", "github_user"],
                "authentication_method": "github_token",
            },
            "private": {
                "registry_type": "private",
                "endpoint": "registry.company.internal",
                "best_practices": [
                    "Use TLS/HTTPS for communication",
                    "Implement authentication via HTTP Basic or OAuth2",
                    "Configure storage backend",
                    "Enable garbage collection",
                    "Implement backup and disaster recovery",
                    "Use reverse proxy for load balancing",
                    "Monitor registry metrics",
                ],
                "required_fields": ["endpoint", "username", "password"],
                "authentication_method": "http_basic_or_oauth2",
            },
            "ecr": {
                "registry_type": "ecr",
                "endpoint": "*.dkr.ecr.*.amazonaws.com",
                "best_practices": [
                    "Use IAM roles for authentication",
                    "Implement ECR image scanning",
                    "Use lifecycle policies",
                    "Enable cross-account access",
                    "Integrate with CloudTrail",
                    "Use image replication",
                ],
                "required_fields": ["aws_account_id", "aws_region"],
                "authentication_method": "iam_role_or_access_key",
            },
            "gcr": {
                "registry_type": "gcr",
                "endpoint": "gcr.io",
                "best_practices": [
                    "Use service accounts",
                    "Implement Artifact Analysis",
                    "Use Binary Authorization",
                    "Enable image signing with KMS",
                    "Organize with multi-regional settings",
                    "Implement VPC Service Controls",
                ],
                "required_fields": ["service_account_key", "project_id"],
                "authentication_method": "service_account_key",
            },
        }

    def validate_registry_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate a registry configuration."""
        registry_type = config.get("registry_type", "").lower()
        
        if registry_type not in self.patterns:
            return {
                "valid": False,
                "confidence": 0.0,
                "error": f"Unknown registry type: {registry_type}",
                "checks": [],
            }
        
        pattern = self.patterns[registry_type]
        checks = self._run_checks(config, pattern, registry_type)
        confidence = self._calculate_confidence(checks)
        
        return {
            "valid": confidence >= self.confidence_threshold,
            "confidence": round(confidence, 3),
            "registry_type": registry_type,
            "checks": checks,
            "issues": self._extract_issues(checks),
            "recommendations": self._generate_recommendations(checks),
            "timestamp": self.validation_timestamp,
        }

    def _run_checks(
        self, config: Dict[str, Any], pattern: Dict[str, Any], registry_type: str
    ) -> List[Dict[str, Any]]:
        """Run validation checks."""
        checks = []
        
        # Check 1: Required fields
        checks.append(self._check_required_fields(config, pattern))
        
        # Check 2: Endpoint validation
        checks.append(self._check_endpoint(config, pattern))
        
        # Check 3: Authentication method
        checks.append(self._check_authentication(config, pattern))
        
        # Check 4: Credentials present
        checks.append(self._check_credentials(config, pattern))
        
        # Check 5: Namespace structure
        checks.append(self._check_namespace(config, pattern))
        
        # Check 6: Security settings
        checks.append(self._check_security_settings(config, registry_type))
        
        return checks

    @staticmethod
    def _check_required_fields(
        config: Dict[str, Any], pattern: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Check if required fields are present."""
        required = pattern.get("required_fields", [])
        present = [f for f in required if f in config]
        missing = [f for f in required if f not in config]
        
        return {
            "name": "Required Fields Check",
            "passed": len(missing) == 0,
            "details": {
                "required": required,
                "present": present,
                "missing": missing,
            },
            "weight": 0.25,
        }

    @staticmethod
    def _check_endpoint(
        config: Dict[str, Any], pattern: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Check endpoint configuration."""
        endpoint = config.get("endpoint", "")
        pattern_endpoint = pattern.get("endpoint", "")
        
        if not endpoint:
            return {
                "name": "Endpoint Check",
                "passed": False,
                "details": {"error": "Endpoint not provided"},
                "weight": 0.20,
            }
        
        # Simple pattern matching for wildcards
        if "*" in pattern_endpoint:
            # Match pattern like *.dkr.ecr.*.amazonaws.com
            pattern_re = pattern_endpoint.replace("*", ".*")
            matches = re.match(f"^{pattern_re}$", endpoint)
            return {
                "name": "Endpoint Check",
                "passed": bool(matches),
                "details": {
                    "endpoint": endpoint,
                    "pattern": pattern_endpoint,
                    "matches": bool(matches),
                },
                "weight": 0.20,
            }
        else:
            return {
                "name": "Endpoint Check",
                "passed": True,  # Always pass if endpoint is provided
                "details": {
                    "endpoint": endpoint,
                    "validated": True,
                },
                "weight": 0.20,
            }

    @staticmethod
    def _check_authentication(
        config: Dict[str, Any], pattern: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Check authentication method."""
        auth_method = config.get("authentication_method", "")
        expected_method = pattern.get("authentication_method", "")
        
        return {
            "name": "Authentication Method Check",
            "passed": auth_method == expected_method,
            "details": {
                "provided": auth_method,
                "expected": expected_method,
                "match": auth_method == expected_method,
            },
            "weight": 0.15,
        }

    @staticmethod
    def _check_credentials(
        config: Dict[str, Any], pattern: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Check if credentials are securely stored."""
        has_credentials = bool(config.get("credentials_provided", False))
        
        return {
            "name": "Credentials Storage Check",
            "passed": has_credentials,
            "details": {
                "credentials_provided": has_credentials,
                "note": "Credentials should be stored in GitHub Secrets, not config",
            },
            "weight": 0.20,
        }

    @staticmethod
    def _check_namespace(
        config: Dict[str, Any], pattern: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Check namespace structure."""
        namespace = config.get("namespace", "")
        structure = pattern.get("namespace_structure", "")
        
        return {
            "name": "Namespace Structure Check",
            "passed": bool(namespace),
            "details": {
                "provided": namespace,
                "expected_format": structure,
                "has_namespace": bool(namespace),
            },
            "weight": 0.10,
        }

    @staticmethod
    def _check_security_settings(config: Dict[str, Any], registry_type: str) -> Dict[str, Any]:
        """Check security-related settings."""
        security_checks = {
            "dockerhub": [
                "image_scanning_enabled",
                "content_trust_enabled",
            ],
            "ghcr": [
                "ghas_scanning_enabled",
                "container_signing_enabled",
            ],
            "private": [
                "tls_enabled",
                "authentication_enabled",
            ],
            "ecr": [
                "image_scanning_enabled",
                "kms_encryption_enabled",
            ],
            "gcr": [
                "binary_authorization_enabled",
                "artifact_analysis_enabled",
            ],
        }
        
        required_checks = security_checks.get(registry_type, [])
        enabled_checks = [c for c in required_checks if config.get(c, False)]
        
        return {
            "name": "Security Settings Check",
            "passed": len(enabled_checks) > 0,
            "details": {
                "required": required_checks,
                "enabled": enabled_checks,
                "coverage": len(enabled_checks) / max(len(required_checks), 1),
            },
            "weight": 0.10,
        }

    @staticmethod
    def _calculate_confidence(checks: List[Dict[str, Any]]) -> float:
        """Calculate overall confidence score."""
        if not checks:
            return 0.0
        
        total_weight = sum(c.get("weight", 0) for c in checks)
        weighted_score = sum(
            (1.0 if c.get("passed", False) else 0.0) * c.get("weight", 0)
            for c in checks
        )
        
        return weighted_score / total_weight if total_weight > 0 else 0.0

    @staticmethod
    def _extract_issues(checks: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """Extract issues from failed checks."""
        issues = []
        for check in checks:
            if not check.get("passed", False):
                issues.append({
                    "check": check.get("name", "Unknown"),
                    "details": check.get("details", {}),
                })
        return issues

    @staticmethod
    def _generate_recommendations(checks: List[Dict[str, Any]]) -> List[str]:
        """Generate recommendations based on failed checks."""
        recommendations = []
        
        for check in checks:
            if not check.get("passed", False):
                name = check.get("name", "")
                if "Required Fields" in name:
                    recommendations.append(
                        "Provide all required configuration fields"
                    )
                elif "Endpoint" in name:
                    recommendations.append(
                        "Verify registry endpoint is correct and accessible"
                    )
                elif "Authentication" in name:
                    recommendations.append(
                        "Verify authentication method matches pattern"
                    )
                elif "Credentials" in name:
                    recommendations.append(
                        "Store credentials in GitHub Secrets or environment variables"
                    )
                elif "Namespace" in name:
                    recommendations.append(
                        "Define appropriate namespace/organization structure"
                    )
                elif "Security" in name:
                    recommendations.append(
                        "Enable recommended security features for this registry type"
                    )
        
        return recommendations


def validate_config_sample() -> Dict[str, Any]:
    """Create and validate a sample configuration."""
    validator = RegistryValidator()
    
    # Sample GHCR configuration
    sample_config = {
        "registry_type": "ghcr",
        "endpoint": "ghcr.io",
        "username": "github_user",
        "github_token": "***",
        "namespace": "org/imagename",
        "authentication_method": "github_token",
        "credentials_provided": True,
        "ghas_scanning_enabled": True,
        "container_signing_enabled": True,
    }
    
    return validator.validate_registry_config(sample_config)


def main():
    """Main entry point."""
    try:
        # Initialize validator
        validator = RegistryValidator()
        
        # Generate sample validation
        validation_result = validate_config_sample()
        
        # Create output
        output = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "validator_version": "1.0.0",
            "validation_results": validation_result,
            "sample_configuration": {
                "note": "This is a sample validation result",
                "threshold": validator.confidence_threshold,
            },
        }
        
        # Log results
        logger.info(f"Validation confidence: {validation_result['confidence']}")
        logger.info(f"Valid: {validation_result['valid']}")
        
        # Print output
        print(json.dumps(output, indent=2))
        
        return 0
    except Exception as e:
        logger.error(f"Error validating registry config: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
