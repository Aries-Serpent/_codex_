"""
Release Gatekeeper - DECIDE Phase

#AFTERMATH_PATTERN_IDENTIFIED: release_decision_making
#AFTERMATH_METRIC: decisions_made

Makes go/no-go release decisions based on validation results.
"""

from pathlib import Path
from typing import Dict, List, Any
from dataclasses import dataclass
from enum import Enum
import sys

_core_path = str(Path(__file__).parent.parent.parent / "core")
if _core_path not in sys.path:
    sys.path.insert(0, _core_path)
from cognitive_brain import CognitiveBrain


class ReleaseDecision(Enum):
    """Release decision types."""
    APPROVE = "approve"
    APPROVE_WITH_MONITORING = "approve_with_monitoring"
    BLOCK = "block"


@dataclass
class ReleaseAssessment:
    """Release risk assessment."""
    decision: ReleaseDecision
    risk_score: float  # 0.0 (low risk) - 1.0 (high risk)
    blockers: List[str]
    warnings: List[str]
    confidence: float  # 0.0 - 1.0
    reasoning: str
    metadata: Dict[str, Any]


class ReleaseGatekeeper:
    """
    Release Gatekeeper - DECIDE Phase
    
    #AFTERMATH_PATTERN_IDENTIFIED: risk_assessment
    
    Assesses release risk and makes go/no-go decisions.
    """
    
    def __init__(self):
        self.brain = CognitiveBrain(Path(".codex/brain.db"))
    
    def decide(self, validation_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        DECIDE: Make release decision based on validations.
        
        #AFTERMATH_METRIC: release_risk_calculated
        
        Args:
            validation_results: Results from PERCEIVE phase
            
        Returns:
            Release decision with risk assessment
        """
        # Calculate risk score
        risk_score = self._calculate_release_risk(validation_results)
        
        # Query cognitive brain for historical patterns
        historical_success_rate = self._query_historical_success(risk_score)
        
        # Identify blockers and warnings
        blockers = self._identify_blockers(validation_results)
        warnings = self._identify_warnings(validation_results)
        
        # Make decision based on risk and blockers
        decision = self._make_decision(risk_score, blockers, warnings)
        
        # Calculate confidence
        confidence = self._calculate_confidence(
            risk_score, historical_success_rate, len(blockers), len(warnings)
        )
        
        assessment = ReleaseAssessment(
            decision=decision,
            risk_score=risk_score,
            blockers=blockers,
            warnings=warnings,
            confidence=confidence,
            reasoning=self._generate_reasoning(decision, risk_score, blockers, warnings),
            metadata={
                "historical_success_rate": historical_success_rate,
                "validation_pass_rate": validation_results.get("pass_rate", 0.0)
            }
        )
        
        return {
            "decision": assessment.decision.value,
            "risk_score": assessment.risk_score,
            "blockers": assessment.blockers,
            "warnings": assessment.warnings,
            "confidence": assessment.confidence,
            "reasoning": assessment.reasoning,
            "metadata": assessment.metadata
        }
    
    def _calculate_release_risk(self, validation_results: Dict[str, Any]) -> float:
        """Calculate overall release risk score."""
        pass_rate = validation_results.get("pass_rate", 0.0)
        
        # Inverse pass rate for risk (higher pass rate = lower risk)
        base_risk = 1.0 - pass_rate
        
        # Adjust for critical failures
        validations = validation_results.get("validations", [])
        critical_failures = [
            v for v in validations 
            if not v["passed"] and v["check_name"] in ["CI/CD Status", "Security Scan"]
        ]
        
        # Increase risk for critical failures
        risk_adjustment = len(critical_failures) * 0.2
        
        return min(1.0, base_risk + risk_adjustment)
    
    def _query_historical_success(self, current_risk: float) -> float:
        """Query historical release success rate."""
        try:
            patterns = self.brain.query_patterns(
                pattern_type="release_outcome",
                confidence_threshold=0.6
            )
            
            # Filter by similar risk levels
            similar_releases = [
                p for p in patterns 
                if abs(p.get("risk_score", 0.5) - current_risk) < 0.2
            ]
            
            if similar_releases:
                success_count = sum(1 for p in similar_releases if p.get("success", False))
                return success_count / len(similar_releases)
            
            # Default to 70% if no historical data
            return 0.7
        except Exception:
            # Best-effort: if brain query fails, return default success rate
            return 0.7
    
    def _identify_blockers(self, validation_results: Dict[str, Any]) -> List[str]:
        """Identify release blockers."""
        blockers = []
        validations = validation_results.get("validations", [])
        
        for v in validations:
            if not v["passed"]:
                check_name = v["check_name"]
                # Critical checks are blockers
                if check_name in ["CI/CD Status", "Security Scan"]:
                    blockers.append(f"{check_name}: {v.get('error_message', 'Check failed')}")
                # High-severity issues are blockers
                elif v.get("score", 1.0) < 0.5:
                    blockers.append(f"{check_name}: Score {v['score']:.2f} below threshold")
        
        return blockers
    
    def _identify_warnings(self, validation_results: Dict[str, Any]) -> List[str]:
        """Identify release warnings."""
        warnings = []
        validations = validation_results.get("validations", [])
        
        for v in validations:
            if not v["passed"]:
                check_name = v["check_name"]
                # Non-critical failures are warnings
                if check_name not in ["CI/CD Status", "Security Scan"]:
                    if v.get("score", 0.0) >= 0.5:  # Partial pass
                        warnings.append(f"{check_name}: {v.get('error_message', 'Minor issues detected')}")
        
        return warnings
    
    def _make_decision(
        self, risk_score: float, blockers: List[str], warnings: List[str]
    ) -> ReleaseDecision:
        """Make final release decision."""
        # Block if any blockers exist
        if blockers:
            return ReleaseDecision.BLOCK
        
        # Approve with monitoring if risk is moderate or warnings exist
        if risk_score >= 0.3 or warnings:
            return ReleaseDecision.APPROVE_WITH_MONITORING
        
        # Approve if risk is low and no warnings
        return ReleaseDecision.APPROVE
    
    def _calculate_confidence(
        self, risk_score: float, historical_success: float, 
        blocker_count: int, warning_count: int
    ) -> float:
        """Calculate confidence in decision."""
        # Base confidence on historical data
        confidence = historical_success
        
        # Adjust for risk (higher risk = lower confidence)
        confidence *= (1.0 - (risk_score * 0.3))
        
        # Reduce confidence for blockers and warnings
        confidence *= (1.0 - (blocker_count * 0.1))
        confidence *= (1.0 - (warning_count * 0.05))
        
        return max(0.0, min(1.0, confidence))
    
    def _generate_reasoning(
        self, decision: ReleaseDecision, risk_score: float,
        blockers: List[str], warnings: List[str]
    ) -> str:
        """Generate human-readable reasoning."""
        if decision == ReleaseDecision.BLOCK:
            return f"Release BLOCKED due to {len(blockers)} blocker(s): {', '.join(blockers[:2])}"
        elif decision == ReleaseDecision.APPROVE_WITH_MONITORING:
            return f"Release APPROVED with monitoring (risk: {risk_score:.2f}, {len(warnings)} warning(s))"
        else:
            return f"Release APPROVED (low risk: {risk_score:.2f})"
