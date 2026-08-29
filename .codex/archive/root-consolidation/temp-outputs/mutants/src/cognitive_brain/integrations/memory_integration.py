"""
Memory-Augmented Compliance Assessment

Integrates QuantumMemoryManager with compliance assessment for memory-guided
decisions. Enables pattern reuse and computational efficiency through caching.

PDA Loop + AfterMath:
- PLAN: Define memory-first decision strategy
- DO: Check memory → cache hit or full assessment → store result
- ASSESS: Measure cache hit rate, time savings, accuracy
- AfterMath: Track k₁ improvement, memory efficiency

Decision Flow:
1. Extract features from audit
2. Check memory for similar cases
3. If high confidence match → return cached decision (cache hit)
4. If novel case → run full quantum assessment → store in memory
5. Track cache hit rate (target: ≥ 30%)
"""

import logging
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

from cognitive_brain.integrations.compliance_integration import (
    AuditResult,
    ComplianceAssessment,
    ComplianceDecision,
    QuantumComplianceAssessor,
)
from cognitive_brain.models.quantum_metrics import QuantumMetricRepository
from cognitive_brain.quantum.coherence_monitor import CoherenceMonitor
from cognitive_brain.quantum.config import QuantumConfig
from cognitive_brain.quantum.memory import MemoryPattern, QuantumMemoryManager

# Configure logging
logger = logging.getLogger(__name__)


# Constants
# Quantum baseline: average time for a full quantum compliance assessment from Phase 8.0 experiments.  # noqa: E501
# NOTE: This is distinct from the CLASSICAL_BASELINE_MS = 28.5 used in exp5_validation.py for k₁ calculations.  # noqa: E501
# The quantum baseline is used for memory-augmented/quantum performance comparisons, not classical rule-based baselines.  # noqa: E501
QUANTUM_FULL_ASSESSMENT_TIME_MS = 12.5


@dataclass
class MemoryAugmentedAssessment(ComplianceAssessment):
    """
    Extended assessment with memory metadata.

    Adds cache hit information to standard compliance assessment.
    """

    cache_hit: bool = False
    cache_confidence: Optional[float] = None
    similar_pattern_count: int = 0


class MemoryAugmentedComplianceAssessor:
    """
    Compliance assessor augmented with quantum memory management.

    Decision Strategy:
    - Memory-first: Check cache for similar patterns
    - Cache hit: Return cached decision if high confidence
    - Cache miss: Run full quantum assessment + store result

    Performance Target:
    - Cache hit rate ≥ 30%
    - Time reduction ≥ 15% (compared to always running full assessment)
    - Accuracy ≥ 95% (memory vs full assessment)
    - k₁ improvement: 0.35 → 0.345 (1.4% reduction)
    """

    def __init__(
        self,
        config: Optional[QuantumConfig] = None,
        monitor: Optional[CoherenceMonitor] = None,
        repository: Optional[QuantumMetricRepository] = None,
        memory_manager: Optional[QuantumMemoryManager] = None,
        confidence_threshold: float = 0.85,
        enable_memory: bool = True,
    ):
        """
        Initialize memory-augmented assessor.

        Args:
            config: Quantum configuration (defaults to ``QuantumConfig()``)
            monitor: Coherence monitor (defaults to ``CoherenceMonitor()``)
            repository: Metric repository (defaults to ``QuantumMetricRepository()``)
            memory_manager: Memory manager (created if None)
            confidence_threshold: Minimum confidence for cache hit (default: 0.85)
            enable_memory: Whether to use memory (feature flag)
        """
        self.config = config or QuantumConfig()
        self.monitor = monitor or CoherenceMonitor()
        self.repository = repository or QuantumMetricRepository()
        self.confidence_threshold = confidence_threshold
        self.enable_memory = enable_memory

        # Create base assessor (full quantum assessment)
        self.base_assessor = QuantumComplianceAssessor(
            config=config, monitor=monitor, repository=repository
        )

        # Create or use provided memory manager
        if memory_manager is None:
            self.memory = QuantumMemoryManager(self.config)
        else:
            self.memory = memory_manager

        # Statistics
        self.total_assessments = 0
        self.cache_hit_count = 0
        self.cache_miss_count = 0
        self.time_saved_ms = 0.0

    def assess_with_memory(self, audit: AuditResult) -> MemoryAugmentedAssessment:
        """
        Assess compliance with memory-guided decision.

        Flow:
        1. Extract features from audit
        2. Check memory for similar cases
        3. If high confidence → return cached decision
        4. If novel → run full assessment → store result

        Args:
            audit: Audit result to assess

        Returns:
            Memory-augmented assessment with cache metadata
        """
        self.total_assessments += 1
        start_time = time.time()

        # Extract features for memory lookup
        features = self._extract_features(audit)

        # Try memory-guided decision
        if self.enable_memory:
            cached_decision = self.memory.memory_guided_decision(
                features, confidence_threshold=self.confidence_threshold
            )

            if cached_decision is not None:
                # Cache hit!
                elapsed_ms = (time.time() - start_time) * 1000
                self.cache_hit_count += 1

                # Estimate time saved (compared to full assessment)
                # Use quantum baseline constant from Phase 8.0 measurements
                time_saved = QUANTUM_FULL_ASSESSMENT_TIME_MS - elapsed_ms
                self.time_saved_ms += max(0, time_saved)

                # Retrieve similar patterns for metadata
                similar_patterns = self.memory.retrieve_similar(features, k=5)
                avg_confidence = (
                    sum(p.confidence for p in similar_patterns) / len(similar_patterns)
                    if similar_patterns
                    else 0.0
                )

                # Convert cached decision string to enum
                try:
                    decision_enum = ComplianceDecision(cached_decision)
                except (ValueError, KeyError):
                    # If conversion fails, run full assessment
                    self.cache_miss_count += 1
                    assessment = self.base_assessor.assess_compliance(audit)
                    elapsed_ms = (time.time() - start_time) * 1000

                    return MemoryAugmentedAssessment(
                        decision=assessment.decision,
                        confidence=assessment.confidence,
                        reasoning="Cache hit with invalid decision format, ran full assessment",
                        coherence=assessment.coherence,
                        used_superposition=assessment.used_superposition,
                        evaluation_time_ms=elapsed_ms,
                        cache_hit=False,
                        cache_confidence=None,
                        similar_pattern_count=0,
                    )

                return MemoryAugmentedAssessment(
                    decision=decision_enum,
                    confidence=avg_confidence,
                    reasoning=f"Cached decision from {len(similar_patterns)} similar patterns",
                    coherence=0.0,  # No superposition used
                    used_superposition=False,
                    evaluation_time_ms=elapsed_ms,
                    cache_hit=True,
                    cache_confidence=avg_confidence,
                    similar_pattern_count=len(similar_patterns),
                )

        # Cache miss - run full assessment
        self.cache_miss_count += 1
        assessment = self.base_assessor.assess_compliance(audit)
        elapsed_ms = (time.time() - start_time) * 1000

        # Store in memory for future use
        if self.enable_memory:
            pattern = MemoryPattern(
                pattern_id=audit.audit_id,
                features=features,
                decision=assessment.decision.value,
                confidence=assessment.confidence,
                timestamp=datetime.now(timezone.utc),
            )
            self.memory.store_pattern(pattern)

            # Periodically consolidate (every 100 patterns)
            if self.total_assessments % 100 == 0:
                self.memory.consolidate()

        # Convert to memory-augmented assessment
        return MemoryAugmentedAssessment(
            decision=assessment.decision,
            confidence=assessment.confidence,
            reasoning=assessment.reasoning,
            coherence=assessment.coherence,
            used_superposition=assessment.used_superposition,
            evaluation_time_ms=elapsed_ms,
            cache_hit=False,
            cache_confidence=None,
            similar_pattern_count=0,
        )

    def get_cache_hit_rate(self) -> float:
        """
        Calculate cache hit rate.

        Returns:
            Cache hit rate (0.0-1.0)
        """
        if self.total_assessments == 0:
            return 0.0
        return self.cache_hit_count / self.total_assessments

    def get_time_savings_percentage(self) -> float:
        """
        Calculate time savings percentage from memory hits.

        Returns:
            Time savings percentage (e.g., 0.15 = 15% savings)
        """
        if self.total_assessments == 0:
            return 0.0

        # Calculate average time saved per assessment
        avg_time_saved = self.time_saved_ms / self.total_assessments

        # Use quantum baseline constant from Phase 8.0
        return avg_time_saved / QUANTUM_FULL_ASSESSMENT_TIME_MS

    def get_statistics(self) -> dict:
        """
        Get comprehensive statistics.

        Returns:
            Dictionary with assessment and memory metrics
        """
        memory_stats = self.memory.get_statistics()

        return {
            "total_assessments": self.total_assessments,
            "cache_hits": self.cache_hit_count,
            "cache_misses": self.cache_miss_count,
            "cache_hit_rate": self.get_cache_hit_rate(),
            "time_saved_ms": self.time_saved_ms,
            "time_savings_pct": self.get_time_savings_percentage(),
            "memory_enabled": self.enable_memory,
            **memory_stats,  # Include memory manager statistics
        }

    @staticmethod
    def _extract_features(audit: AuditResult) -> dict[str, float]:
        """
        Extract normalized feature vector from audit result.

        Args:
            audit: Audit result

        Returns:
            Normalized feature dict
        """
        # Risk level encoding
        risk_encoding = {"low": 0.0, "medium": 0.5, "high": 1.0}

        # Get risk value with validation
        risk_level_normalized = audit.risk_level.lower()
        if risk_level_normalized not in risk_encoding:
            # Use proper logging instead of print
            logger.warning(
                f"Unknown risk level '{audit.risk_level}' for audit {audit.audit_id}, "
                "defaulting to 'medium' (0.5)"
            )
            risk_value = 0.5
        else:
            risk_value = risk_encoding[risk_level_normalized]

        # Normalize features to 0-1 range
        return {
            "score": audit.score,  # Already 0-1
            "risk": risk_value,
            "cost_normalized": min(audit.remediation_cost / 20000, 1.0),  # Cap at $20k
            "impact": audit.business_impact,  # Already 0-1
            "violation_count": min(len(audit.violations) / 10.0, 1.0),  # Cap at 10
        }


# Alias for backward compatibility
ComplianceAssessor = MemoryAugmentedComplianceAssessor
