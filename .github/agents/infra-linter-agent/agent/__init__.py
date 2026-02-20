"""
infra-linter-agent.v1 - Infrastructure-as-Code Linting and Validation Agent

This agent validates IaC files (Terraform, Kubernetes, CloudFormation, Docker, Ansible)
to prevent misconfigurations, security vulnerabilities, and compliance violations.

PDA Loop Architecture:
- PERCEIVE (scanner.py): Discover and scan IaC files
- DECIDE (validator.py): Assess risk and make recommendations
- ACT (enforcer.py): Generate reports and enforce policies
- AFTERMATH (reporter.py): Track outcomes and learn patterns

Version: 1.0.0
Author: GitHub Copilot Agent
Created: 2026-01-01
"""

from .enforcer import EnforcementResult, IaCEnforcer
from .reporter import AftermathReport, IaCReporter
from .scanner import IaCScanner, ScanResult
from .validator import IaCValidator, ValidationResult

__all__ = [
    "IaCScanner",
    "ScanResult",
    "IaCValidator",
    "ValidationResult",
    "IaCEnforcer",
    "EnforcementResult",
    "IaCReporter",
    "AftermathReport",
]

__version__ = "1.0.0"
