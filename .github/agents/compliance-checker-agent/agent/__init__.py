"""
Compliance Checker Agent - SOC2, PCI-DSS, GDPR, HIPAA Validation

This agent implements the PDA Loop pattern for compliance validation:
- PERCEIVE (auditor.py): Scan code for compliance-relevant patterns
- DECIDE (assessor.py): Assess compliance gaps and calculate risk
- ACT (enforcer.py): Generate audit reports and remediation plans
- AFTERMATH (reporter.py): Track compliance trends and learn patterns

All modules integrate with the Cognitive Brain for pattern learning.
"""

from .auditor import ComplianceAuditor, ComplianceFinding, AuditResult
from .assessor import ComplianceAssessor, AssessmentResult, ComplianceStatus
from .enforcer import ComplianceEnforcer, EnforcementResult
from .reporter import ComplianceReporter, AftermathReport

__all__ = [
    'ComplianceAuditor',
    'ComplianceFinding',
    'AuditResult',
    'ComplianceAssessor',
    'AssessmentResult',
    'ComplianceStatus',
    'ComplianceEnforcer',
    'EnforcementResult',
    'ComplianceReporter',
    'AftermathReport',
]

__version__ = '1.0.0'
