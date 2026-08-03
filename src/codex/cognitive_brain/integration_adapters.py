"""Integration Adapters for Planset 008 → Downstream Plansets (009, 010, 011).

Bridges Cognitive Reasoning Engine outputs to:
- Planset 009: Multi-Model Ensemble Prediction
- Planset 010: Enterprise Scaling & Multi-Tenant Isolation  
- Planset 011: Root Cause Analysis & Anomaly Correlation

All adapters produce JSON-compatible output for downstream processing.
"""

import json
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from .reasoning_engine import Decision


@dataclass
class Planset009Input:
    """Adapter output for Planset 009: Multi-Model Ensemble Prediction.
    
    Packages reasoning engine decision as feature vector for ensemble models.
    """
    
    reasoning_decision_id: str
    confidence_score: float
    confidence_level: str
    decision_option: str
    reasoning_text: str
    strategy_used: str
    candidate_count: int
    domain_validation_passed: bool
    latency_ms: float
    decision_timestamp: str
    category: str
    
    # Feature vector components for ensemble input
    feature_vector: Dict[str, float]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dict for Planset 009."""
        return {
            "reasoning_decision_id": self.reasoning_decision_id,
            "confidence_score": float(self.confidence_score),
            "confidence_level": self.confidence_level,
            "decision_option": self.decision_option,
            "reasoning_text": self.reasoning_text,
            "strategy_used": self.strategy_used,
            "candidate_count": int(self.candidate_count),
            "domain_validation_passed": bool(self.domain_validation_passed),
            "latency_ms": float(self.latency_ms),
            "decision_timestamp": self.decision_timestamp,
            "category": self.category,
            "feature_vector": {k: float(v) for k, v in self.feature_vector.items()},
        }
    
    def to_json(self) -> str:
        """Serialize to JSON string."""
        return json.dumps(self.to_dict())


@dataclass
class Planset010Input:
    """Adapter output for Planset 010: Enterprise Scaling & Multi-Tenant.
    
    Provides confidence scores and context for multi-tenant isolation decisions.
    """
    
    reasoning_decision_id: str
    confidence_score: float
    confidence_level: str
    domain_validation_passed: bool
    decision_latency_ms: float
    
    # Multi-tenant context
    tenant_id: Optional[str]
    isolation_required: bool
    resource_constraints: Dict[str, Any]
    
    # Isolation metrics for Planset 010
    confidence_threshold_met: bool  # confidence >= 0.75
    safe_for_production: bool  # domain_validation AND latency < 100ms
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dict for Planset 010."""
        return {
            "reasoning_decision_id": self.reasoning_decision_id,
            "confidence_score": float(self.confidence_score),
            "confidence_level": self.confidence_level,
            "domain_validation_passed": bool(self.domain_validation_passed),
            "decision_latency_ms": float(self.decision_latency_ms),
            "tenant_id": self.tenant_id,
            "isolation_required": bool(self.isolation_required),
            "resource_constraints": self.resource_constraints,
            "confidence_threshold_met": bool(self.confidence_threshold_met),
            "safe_for_production": bool(self.safe_for_production),
        }
    
    def to_json(self) -> str:
        """Serialize to JSON string."""
        return json.dumps(self.to_dict())


@dataclass
class Planset011Input:
    """Adapter output for Planset 011: Root Cause Analysis & Anomaly Correlation.
    
    Provides reasoning traces and decision history for anomaly investigation.
    """
    
    reasoning_decision_id: str
    decision_option: str
    confidence_score: float
    reasoning_text: str
    strategy_used: str
    
    # Decision artifacts for root cause tracing
    candidate_options: List[str]
    validation_rules_applied: List[str]
    
    # Backward-chaining support
    decision_category: str
    context_constraints: List[str]
    
    # Anomaly correlation data
    anomaly_indicators: Dict[str, float]  # metric_name -> score
    historical_decisions: List[str]  # Decision IDs for pattern matching
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dict for Planset 011."""
        return {
            "reasoning_decision_id": self.reasoning_decision_id,
            "decision_option": self.decision_option,
            "confidence_score": float(self.confidence_score),
            "reasoning_text": self.reasoning_text,
            "strategy_used": self.strategy_used,
            "candidate_options": self.candidate_options,
            "validation_rules_applied": self.validation_rules_applied,
            "decision_category": self.decision_category,
            "context_constraints": self.context_constraints,
            "anomaly_indicators": {k: float(v) for k, v in self.anomaly_indicators.items()},
            "historical_decisions": self.historical_decisions,
        }
    
    def to_json(self) -> str:
        """Serialize to JSON string."""
        return json.dumps(self.to_dict())


class PlansetIntegrationAdapter:
    """Main adapter class bridging Reasoning Engine to downstream Plansets."""
    
    def __init__(self, decision_history: Optional[List[Decision]] = None):
        """Initialize adapter.
        
        Args:
            decision_history: Optional history for anomaly correlation
        """
        self.decision_history = decision_history or []
    
    def adapt_for_planset_009(
        self,
        decision: Decision,
        category: str,
    ) -> Planset009Input:
        """Adapt reasoning decision for Planset 009 ensemble model.
        
        Args:
            decision: Decision from reasoning engine
            category: Decision category for routing
            
        Returns:
            Planset009Input ready for ensemble processing
        """
        # Build feature vector from decision components
        feature_vector = {
            "confidence": decision.confidence,
            "confidence_normalized": decision.confidence / 1.0,  # Already normalized
            "latency_factor": min(1.0, decision.latency_ms / 500.0),  # Inverse penalty
            "ensemble_bonus": 0.05 if decision.strategy.value == "ensemble" else 0.0,
            "domain_validation_factor": 0.1 if decision.domain_validation else 0.0,
        }
        
        return Planset009Input(
            reasoning_decision_id=decision.id,
            confidence_score=decision.confidence,
            confidence_level=decision.confidence_level.value,
            decision_option=decision.option,
            reasoning_text=decision.reasoning,
            strategy_used=decision.strategy.value,
            candidate_count=len(decision.candidates),
            domain_validation_passed=decision.domain_validation,
            latency_ms=decision.latency_ms,
            decision_timestamp=decision.timestamp,
            category=category,
            feature_vector=feature_vector,
        )
    
    def adapt_for_planset_010(
        self,
        decision: Decision,
        tenant_id: Optional[str] = None,
        resource_constraints: Optional[Dict[str, Any]] = None,
    ) -> Planset010Input:
        """Adapt reasoning decision for Planset 010 multi-tenant isolation.
        
        Args:
            decision: Decision from reasoning engine
            tenant_id: Optional tenant identifier
            resource_constraints: Optional resource limits for tenant
            
        Returns:
            Planset010Input with isolation metrics
        """
        # Determine if safe for production
        safe_for_production = (
            decision.domain_validation and
            decision.latency_ms < 100.0 and
            decision.confidence >= 0.80
        )
        
        confidence_threshold_met = decision.confidence >= 0.75
        
        return Planset010Input(
            reasoning_decision_id=decision.id,
            confidence_score=decision.confidence,
            confidence_level=decision.confidence_level.value,
            domain_validation_passed=decision.domain_validation,
            decision_latency_ms=decision.latency_ms,
            tenant_id=tenant_id,
            isolation_required=not safe_for_production,
            resource_constraints=resource_constraints or {},
            confidence_threshold_met=confidence_threshold_met,
            safe_for_production=safe_for_production,
        )
    
    def adapt_for_planset_011(
        self,
        decision: Decision,
        constraints: List[str],
        anomaly_indicators: Optional[Dict[str, float]] = None,
    ) -> Planset011Input:
        """Adapt reasoning decision for Planset 011 root cause analysis.
        
        Args:
            decision: Decision from reasoning engine
            constraints: Context constraints from decision
            anomaly_indicators: Optional anomaly scores for correlation
            
        Returns:
            Planset011Input with anomaly correlation data
        """
        # Get historical decisions excluding the current one
        historical_ids = self._get_historical_decision_ids(exclude_latest=True)
        
        return Planset011Input(
            reasoning_decision_id=decision.id,
            decision_option=decision.option,
            confidence_score=decision.confidence,
            reasoning_text=decision.reasoning,
            strategy_used=decision.strategy.value,
            candidate_options=[c.option for c in decision.candidates],
            validation_rules_applied=[r for c in decision.candidates for r in c.validation_rules],
            decision_category="unknown",  # Will be set by caller
            context_constraints=constraints,
            anomaly_indicators=anomaly_indicators or {},
            historical_decisions=historical_ids,
        )
    
    def add_decision_to_history(self, decision: Decision) -> None:
        """Track decision for anomaly correlation.
        
        Args:
            decision: Decision to track
        """
        self.decision_history.append(decision)
        # Keep last 100 decisions for pattern analysis
        if len(self.decision_history) > 100:
            self.decision_history = self.decision_history[-100:]
    
    def _get_historical_decision_ids(self, exclude_latest: bool = True) -> List[str]:
        """Get historical decision IDs for pattern matching.
        
        Args:
            exclude_latest: Whether to exclude the most recent decision
            
        Returns:
            List of decision IDs from history
        """
        if exclude_latest and len(self.decision_history) > 0:
            return [d.id for d in self.decision_history[:-1]]
        return [d.id for d in self.decision_history]
