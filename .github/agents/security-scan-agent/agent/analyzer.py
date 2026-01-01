"""
Security Analyzer Module - DECIDE Phase

#AFTERMATH_PATTERN_IDENTIFIED: security_vulnerability_analysis
Implements CVSS-based severity classification and risk assessment.
"""

from pathlib import Path
from typing import Dict, List, Any
from dataclasses import dataclass
from enum import Enum
import sys

# Add core to path for CognitiveBrain access (acceptable for agent isolation)
# Alternative: Use proper packaging with __init__.py exports
_core_path = str(Path(__file__).parent.parent.parent / "core")
if _core_path not in sys.path:
    sys.path.insert(0, _core_path)
from cognitive_brain import CognitiveBrain


class VulnerabilitySeverity(Enum):
    """Vulnerability severity levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class RemediationPriority(Enum):
    """Remediation priority levels."""
    P0 = "p0"  # Immediate
    P1 = "p1"  # Within 24 hours
    P2 = "p2"  # Within 1 week
    P3 = "p3"  # Within 1 month
    P4 = "p4"  # Best effort


@dataclass
class SecurityAnalysis:
    """Security vulnerability analysis result."""
    finding_id: str
    severity: VulnerabilitySeverity
    priority: RemediationPriority
    cvss_score: float
    exploitability: float
    impact_score: float
    risk_score: float
    remediation_strategy: str
    auto_fixable: bool
    estimated_effort: str
    compliance_impact: List[str]
    metadata: Dict[str, Any]


class SecurityAnalyzer:
    """
    Security Analyzer - DECIDE Phase
    
    #AFTERMATH_PATTERN_IDENTIFIED: cvss_based_risk_assessment
    
    Analyzes security findings and determines:
    - Severity classification (CVSS v3.1)
    - Exploitability assessment
    - Impact analysis (CIA triad)
    - Risk prioritization
    - Remediation strategy selection
    """
    
    def __init__(self, repo_path: Path):
        self.repo_path = repo_path
        self.brain = CognitiveBrain(Path(".codex/brain.db"))
        self.analyses: List[SecurityAnalysis] = []
        
    def decide(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        DECIDE: Analyze findings and determine remediation priorities.
        
        #AFTERMATH_PATTERN_IDENTIFIED: risk_based_prioritization
        
        Args:
            context: Scan results from PERCEIVE phase
            
        Returns:
            Decision with analyses and priorities
        """
        all_findings = context.get("all_findings", [])
        
        # Analyze each finding
        for finding in all_findings:
            analysis = self._analyze_finding(finding)
            self.analyses.append(analysis)
        
        # Query brain for historical patterns
        historical_patterns = self._query_historical_data()
        
        # Prioritize by risk
        prioritized = self._prioritize_by_risk(self.analyses)
        
        decision = {
            "analyses": self.analyses,
            "prioritized_findings": prioritized,
            "critical_count": sum(1 for a in self.analyses if a.severity == VulnerabilitySeverity.CRITICAL),
            "high_count": sum(1 for a in self.analyses if a.severity == VulnerabilitySeverity.HIGH),
            "auto_fixable_count": sum(1 for a in self.analyses if a.auto_fixable),
            "historical_patterns": historical_patterns,
            "recommendations": self._generate_recommendations(prioritized)
        }
        
        #AFTERMATH_METRIC: critical_vulnerabilities = decision["critical_count"]
        #AFTERMATH_METRIC: auto_fixable = decision["auto_fixable_count"]
        
        return decision
    
    def _analyze_finding(self, finding: Any) -> SecurityAnalysis:
        """
        Analyze individual security finding.
        
        #AFTERMATH_PATTERN_IDENTIFIED: individual_vulnerability_assessment
        """
        # Calculate CVSS score
        cvss_score = self._calculate_cvss(finding)
        
        # Assess exploitability
        exploitability = self._assess_exploitability(finding)
        
        # Calculate impact
        impact_score = self._calculate_impact(finding)
        
        # Calculate overall risk
        risk_score = (cvss_score * 0.5) + (exploitability * 0.3) + (impact_score * 0.2)
        
        # Determine severity
        severity = self._map_cvss_to_severity(cvss_score)
        
        # Determine priority
        priority = self._calculate_priority(severity, exploitability, impact_score)
        
        # Select remediation strategy
        strategy = self._select_remediation_strategy(finding)
        
        # Check if auto-fixable
        auto_fixable = self._is_auto_fixable(finding)
        
        # Estimate effort
        effort = self._estimate_effort(finding, auto_fixable)
        
        # Assess compliance impact
        compliance = self._assess_compliance_impact(finding)
        
        return SecurityAnalysis(
            finding_id=f"{finding.tool}_{finding.category}_{hash(finding.title)}",
            severity=severity,
            priority=priority,
            cvss_score=cvss_score,
            exploitability=exploitability,
            impact_score=impact_score,
            risk_score=risk_score,
            remediation_strategy=strategy,
            auto_fixable=auto_fixable,
            estimated_effort=effort,
            compliance_impact=compliance,
            metadata={
                "original_finding": finding,
                "cwe_id": finding.cwe_id,
                "cve_id": finding.cve_id
            }
        )
    
    def _calculate_cvss(self, finding: Any) -> float:
        """
        Calculate CVSS v3.1 score.
        
        #AFTERMATH_PATTERN_IDENTIFIED: cvss_scoring
        """
        # Simplified CVSS calculation based on severity
        if finding.severity == "critical":
            base_score = 9.5
        elif finding.severity == "high":
            base_score = 7.5
        elif finding.severity == "medium":
            base_score = 5.0
        elif finding.severity == "low":
            base_score = 3.0
        else:
            base_score = 1.0
        
        # Adjust based on confidence
        base_score *= finding.confidence
        
        return min(10.0, base_score)
    
    def _assess_exploitability(self, finding: Any) -> float:
        """
        Assess exploitability (0.0-1.0).
        
        #AFTERMATH_PATTERN_IDENTIFIED: exploitability_assessment
        """
        exploitability = 0.5
        
        # SQL injection, XSS = highly exploitable
        if finding.cwe_id in ["CWE-89", "CWE-79"]:
            exploitability = 0.9
        
        # Command injection, path traversal
        elif finding.cwe_id in ["CWE-78", "CWE-22"]:
            exploitability = 0.8
        
        # Insecure crypto
        elif finding.cwe_id in ["CWE-327", "CWE-798"]:
            exploitability = 0.7
        
        # Dependency vulnerabilities with known exploits
        elif finding.cve_id and finding.tool in ["Safety", "pip-audit"]:
            exploitability = 0.8
        
        return exploitability
    
    def _calculate_impact(self, finding: Any) -> float:
        """
        Calculate impact score (0.0-1.0) based on CIA triad.
        
        #AFTERMATH_PATTERN_IDENTIFIED: impact_analysis
        """
        impact = 0.5
        
        # High impact: data exfiltration, remote code execution
        if finding.cwe_id in ["CWE-89", "CWE-78", "CWE-798"]:
            impact = 0.9
        
        # Medium-high: XSS, CSRF
        elif finding.cwe_id in ["CWE-79", "CWE-352"]:
            impact = 0.7
        
        # Medium: crypto, path traversal
        elif finding.cwe_id in ["CWE-327", "CWE-22"]:
            impact = 0.6
        
        return impact
    
    def _map_cvss_to_severity(self, cvss_score: float) -> VulnerabilitySeverity:
        """Map CVSS score to severity enum."""
        if cvss_score >= 9.0:
            return VulnerabilitySeverity.CRITICAL
        elif cvss_score >= 7.0:
            return VulnerabilitySeverity.HIGH
        elif cvss_score >= 4.0:
            return VulnerabilitySeverity.MEDIUM
        elif cvss_score >= 0.1:
            return VulnerabilitySeverity.LOW
        else:
            return VulnerabilitySeverity.INFO
    
    def _calculate_priority(self, severity: VulnerabilitySeverity, 
                          exploitability: float, impact: float) -> RemediationPriority:
        """Calculate remediation priority."""
        if severity == VulnerabilitySeverity.CRITICAL:
            return RemediationPriority.P0
        elif severity == VulnerabilitySeverity.HIGH:
            if exploitability > 0.7:
                return RemediationPriority.P0
            return RemediationPriority.P1
        elif severity == VulnerabilitySeverity.MEDIUM:
            if exploitability > 0.8:
                return RemediationPriority.P1
            return RemediationPriority.P2
        elif severity == VulnerabilitySeverity.LOW:
            return RemediationPriority.P3
        else:
            return RemediationPriority.P4
    
    def _select_remediation_strategy(self, finding: Any) -> str:
        """Select appropriate remediation strategy."""
        if finding.tool in ["Safety", "pip-audit"]:
            return "dependency_upgrade"
        elif finding.cwe_id in ["CWE-89", "CWE-79"]:
            return "input_sanitization"
        elif finding.cwe_id == "CWE-798":
            return "credential_removal"
        elif finding.cwe_id == "CWE-327":
            return "crypto_upgrade"
        else:
            return "code_review"
    
    def _is_auto_fixable(self, finding: Any) -> bool:
        """Determine if vulnerability can be auto-fixed."""
        # Dependency updates are auto-fixable
        if finding.tool in ["Safety", "pip-audit"]:
            return True
        
        # Some pattern-based issues are auto-fixable
        if finding.cwe_id in ["CWE-798"]:  # Hardcoded secrets
            return True
        
        return False
    
    def _estimate_effort(self, finding: Any, auto_fixable: bool) -> str:
        """Estimate remediation effort."""
        if auto_fixable:
            return "low (automated)"
        elif finding.cwe_id in ["CWE-89", "CWE-79"]:
            return "medium (requires code changes)"
        else:
            return "high (requires investigation)"
    
    def _assess_compliance_impact(self, finding: Any) -> List[str]:
        """Assess compliance framework impacts."""
        impacts = []
        
        # OWASP Top 10
        if finding.cwe_id in ["CWE-89", "CWE-79", "CWE-22"]:
            impacts.append("OWASP_TOP_10")
        
        # PCI-DSS
        if finding.cwe_id in ["CWE-798", "CWE-327"]:
            impacts.append("PCI_DSS")
        
        # SOC 2
        if finding.severity in ["critical", "high"]:
            impacts.append("SOC2")
        
        return impacts
    
    def _query_historical_data(self) -> List[Dict[str, Any]]:
        """Query cognitive brain for historical vulnerability patterns."""
        try:
            patterns = self.brain.query_patterns(
                pattern_type="security_vulnerability",
                confidence_threshold=0.7
            )
            return [p.__dict__ for p in patterns[:10]]
        except Exception:
            return []
    
    def _prioritize_by_risk(self, analyses: List[SecurityAnalysis]) -> List[SecurityAnalysis]:
        """Sort analyses by risk score (highest first)."""
        return sorted(analyses, key=lambda a: a.risk_score, reverse=True)
    
    def _generate_recommendations(self, prioritized: List[SecurityAnalysis]) -> List[str]:
        """Generate high-level recommendations."""
        recommendations = []
        
        critical_count = sum(1 for a in prioritized if a.severity == VulnerabilitySeverity.CRITICAL)
        if critical_count > 0:
            recommendations.append(f"Address {critical_count} critical vulnerabilities immediately")
        
        auto_fixable = [a for a in prioritized if a.auto_fixable]
        if auto_fixable:
            recommendations.append(f"Apply {len(auto_fixable)} automated fixes")
        
        deps = [a for a in prioritized if a.remediation_strategy == "dependency_upgrade"]
        if deps:
            recommendations.append(f"Update {len(deps)} vulnerable dependencies")
        
        return recommendations
