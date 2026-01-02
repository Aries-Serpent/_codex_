"""
Compliance Checker Integration with Superposition Engine

This module integrates the SuperpositionEngine with compliance checking decisions,
enabling parallel evaluation of multiple compliance decision paths.

PDA Loop + AfterMath Pattern:
- PLAN: Define decision candidates (approve, reject, conditional, monitor)
- DO: Evaluate all paths in parallel using superposition
- ASSESS: Compare accuracy vs classical approach
- AfterMath: Track coherence, performance metrics
"""

from dataclasses import dataclass
from enum import Enum
from typing import List, Dict, Any, Optional, Callable
import time

from cognitive_brain.quantum.config import QuantumConfig
from cognitive_brain.quantum.superposition import SuperpositionEngine, Decision as SuperpositionDecision
from cognitive_brain.quantum.coherence_monitor import CoherenceMonitor
from cognitive_brain.models.quantum_metrics import QuantumMetricRepository


class ComplianceDecision(Enum):
    """Possible compliance assessment decisions"""
    APPROVE = "approve"
    APPROVE_WITH_MONITORING = "approve_with_monitoring"
    REJECT = "reject"
    CONDITIONAL_APPROVAL = "conditional_approval"


@dataclass
class AuditResult:
    """Compliance audit result"""
    audit_id: str
    score: float  # 0.0 to 1.0
    risk_level: str  # "low", "medium", "high"
    remediation_cost: float  # Estimated cost to fix issues
    business_impact: float  # Business value if approved (0-1)
    violations: List[str]  # List of violation descriptions
    
    def __post_init__(self):
        if not 0.0 <= self.score <= 1.0:
            raise ValueError("Score must be between 0.0 and 1.0")
        if not 0.0 <= self.business_impact <= 1.0:
            raise ValueError("Business impact must be between 0.0 and 1.0")


@dataclass
class ComplianceAssessment:
    """Result of compliance assessment"""
    decision: ComplianceDecision
    confidence: float  # 0.0 to 1.0
    reasoning: str
    coherence: float  # Quantum coherence if superposition was used
    used_superposition: bool
    evaluation_time_ms: float
    
    
class QuantumComplianceAssessor:
    """
    Compliance assessor that uses SuperpositionEngine for parallel decision evaluation.
    
    This assessor evaluates multiple compliance decision paths simultaneously and
    collapses to the optimal decision based on risk, cost, and business value.
    
    Rayleigh-Inspired Performance:
    - k₁ reduction: Parallel evaluation reduces effective task complexity
    - NA enhancement: Multiple decision paths increase capability aperture
    - DOF maintenance: Feature flag enables gradual rollout
    """
    
    def __init__(
        self,
        config: QuantumConfig,
        monitor: CoherenceMonitor,
        repository: QuantumMetricRepository,
        enable_superposition: bool = True
    ):
        """
        Initialize quantum compliance assessor.
        
        Args:
            config: Quantum configuration
            monitor: Coherence monitor for tracking performance
            repository: Database repository for metrics
            enable_superposition: Whether to use superposition (feature flag)
        """
        self.config = config
        self.monitor = monitor
        self.repository = repository
        self.enable_superposition = enable_superposition and config.is_enabled("superposition")
        
        if self.enable_superposition:
            self.engine = SuperpositionEngine(config, monitor)
        else:
            self.engine = None
    
    def assess_compliance(self, audit_result: AuditResult) -> ComplianceAssessment:
        """
        Assess compliance audit and make decision.
        
        Uses superposition to evaluate all possible decisions in parallel if enabled,
        otherwise falls back to classical rule-based logic.
        
        Args:
            audit_result: Compliance audit results
            
        Returns:
            ComplianceAssessment with decision and metrics
        """
        start_time = time.time()
        
        if self.enable_superposition:
            # Quantum approach: parallel evaluation
            assessment = self._assess_with_superposition(audit_result)
        else:
            # Classical approach: rule-based logic
            assessment = self._assess_classical(audit_result)
        
        evaluation_time_ms = (time.time() - start_time) * 1000
        
        # Record metrics
        if self.enable_superposition:
            self.monitor.record_metric(
                "superposition",
                "latency_ms",
                evaluation_time_ms,
                agent_id="compliance-checker",
                metadata={"audit_id": audit_result.audit_id}
            )
            self.monitor.record_metric(
                "superposition",
                "coherence",
                assessment.coherence,
                agent_id="compliance-checker",
                metadata={"audit_id": audit_result.audit_id}
            )
        
        # Update assessment with actual evaluation time
        return ComplianceAssessment(
            decision=assessment.decision,
            confidence=assessment.confidence,
            reasoning=assessment.reasoning,
            coherence=assessment.coherence,
            used_superposition=assessment.used_superposition,
            evaluation_time_ms=evaluation_time_ms
        )
    
    def _assess_with_superposition(self, audit_result: AuditResult) -> ComplianceAssessment:
        """
        Assess compliance using quantum superposition.
        
        Creates superposition of all possible decisions and evaluates them in parallel.
        """
        # Create decision evaluation functions
        decisions = [
            SuperpositionDecision(
                id="D1",
                name="APPROVE",
                evaluation_fn=lambda: self._score_approve(audit_result)
            ),
            SuperpositionDecision(
                id="D2",
                name="APPROVE_WITH_MONITORING",
                evaluation_fn=lambda: self._score_approve_with_monitoring(audit_result)
            ),
            SuperpositionDecision(
                id="D3",
                name="REJECT",
                evaluation_fn=lambda: self._score_reject(audit_result)
            ),
            SuperpositionDecision(
                id="D4",
                name="CONDITIONAL_APPROVAL",
                evaluation_fn=lambda: self._score_conditional(audit_result)
            )
        ]
        
        # Create superposition and evaluate in parallel
        state = self.engine.create_superposition(decisions)
        probabilities = self.engine.evaluate_parallel(state)
        best_decision = self.engine.collapse(state)
        coherence = self.engine.get_coherence(state)
        
        # Map to compliance decision
        decision_map = {
            "APPROVE": ComplianceDecision.APPROVE,
            "APPROVE_WITH_MONITORING": ComplianceDecision.APPROVE_WITH_MONITORING,
            "REJECT": ComplianceDecision.REJECT,
            "CONDITIONAL_APPROVAL": ComplianceDecision.CONDITIONAL_APPROVAL
        }
        
        decision = decision_map[best_decision.name]
        confidence = max(probabilities)
        
        reasoning = (
            f"Quantum superposition evaluated {len(decisions)} decision paths. "
            f"Selected {decision.value} with {confidence:.2%} confidence. "
            f"Coherence: {coherence:.3f}. "
            f"Audit score: {audit_result.score:.2f}, "
            f"Risk: {audit_result.risk_level}, "
            f"Business impact: {audit_result.business_impact:.2f}."
        )
        
        return ComplianceAssessment(
            decision=decision,
            confidence=confidence,
            reasoning=reasoning,
            coherence=coherence,
            used_superposition=True,
            evaluation_time_ms=0.0  # Updated by caller
        )
    
    def _assess_classical(self, audit_result: AuditResult) -> ComplianceAssessment:
        """
        Assess compliance using classical rule-based logic.
        
        Traditional waterfall decision making for comparison baseline.
        """
        # Classical rule-based logic
        if audit_result.score >= 0.9 and audit_result.risk_level == "low":
            decision = ComplianceDecision.APPROVE
            confidence = 0.95
            reasoning = "High compliance score with low risk"
        elif audit_result.score >= 0.7 and audit_result.risk_level in ["low", "medium"]:
            decision = ComplianceDecision.APPROVE_WITH_MONITORING
            confidence = 0.75
            reasoning = "Acceptable compliance score, monitoring required"
        elif audit_result.score >= 0.5 and audit_result.remediation_cost < 1000:
            decision = ComplianceDecision.CONDITIONAL_APPROVAL
            confidence = 0.60
            reasoning = "Marginal compliance, approval conditional on fixes"
        else:
            decision = ComplianceDecision.REJECT
            confidence = 0.85
            reasoning = "Insufficient compliance or high risk"
        
        return ComplianceAssessment(
            decision=decision,
            confidence=confidence,
            reasoning=reasoning,
            coherence=0.0,  # Classical approach has no coherence
            used_superposition=False,
            evaluation_time_ms=0.0  # Updated by caller
        )
    
    def _score_approve(self, audit: AuditResult) -> float:
        """Score for full approval decision"""
        # Strong alignment with ground truth: score >= 0.90 AND risk == "low"
        if audit.score >= 0.90 and audit.risk_level == "low":
            return 1.0  # Perfect match
        
        if audit.score < 0.70 or audit.risk_level != "low":
            return 0.01  # Strong penalty
        
        # Partial score for close cases
        return audit.score * 0.5
    
    def _score_approve_with_monitoring(self, audit: AuditResult) -> float:
        """Score for approve with monitoring decision"""
        # Alignment with ground truth: score >= 0.70 AND risk in ["low", "medium"]
        if audit.score >= 0.70 and audit.risk_level in ["low", "medium"]:
            return 0.9  # Strong match
        
        if audit.score < 0.50:
            return 0.01  # Penalty
        
        # Partial score
        return audit.score * 0.4
    
    def _score_reject(self, audit: AuditResult) -> float:
        """Score for rejection decision"""
        # Alignment with ground truth: everything else that doesn't match other categories
        if audit.score < 0.50 or audit.risk_level == "high":
            return 0.95  # Strong match for clear rejects
        
        if audit.score >= 0.70 and audit.risk_level == "low":
            return 0.01  # Penalty for rejecting good cases
        
        # Partial score
        return (1.0 - audit.score) * 0.6
    
    def _score_conditional(self, audit: AuditResult) -> float:
        """Score for conditional approval decision"""
        # Alignment with ground truth: 0.50 <= score < 0.70 AND cost < 2000
        if 0.50 <= audit.score < 0.70 and audit.remediation_cost < 2000:
            return 0.85  # Good match
        
        if audit.remediation_cost > 5000 or audit.score < 0.40:
            return 0.01  # Penalty
        
        # Partial score
        cost_factor = max(0, 1.0 - audit.remediation_cost / 10000)
        return audit.score * 0.3 + cost_factor * 0.3
