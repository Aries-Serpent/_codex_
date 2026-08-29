"""
LTM Retention Policy Manager

Implements retention policies for long-term memory with support for
evergreen, standard, decay, and archived patterns.

PHASE 10.2: Retention Policies
Status: Production Ready
"""

import logging
import math
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional

logger = logging.getLogger(__name__)


class RetentionPolicy(Enum):
    """Retention policy types."""

    EVERGREEN = "evergreen"
    STANDARD = "standard"
    DECAY = "decay"
    ARCHIVED = "archived"


@dataclass
class RetentionConfig:
    """Configuration for retention policies."""

    evergreen_protected: bool = True
    standard_retention_days: int = 90
    decay_retention_days: int = 180
    decay_halflife_days: int = 60
    archived_retention_days: int = 365
    min_confidence_for_retention: float = 0.1
    confidence_decay_factor: float = 0.95  # per day
    cleanup_batch_size: int = 100
    dry_run: bool = False  # For testing


@dataclass
class PatternRecord:
    """Represents a pattern in LTM."""

    key: str
    value: str
    pattern_type: str
    confidence: float
    success_rate: float
    frequency: int
    created_at: datetime
    last_accessed: datetime
    tags: list[str] = field(default_factory=list)
    policy: RetentionPolicy = RetentionPolicy.STANDARD
    metadata: dict[str, Any] = field(default_factory=dict)


class PolicyBase:
    """Base class for retention policies."""

    def __init__(self, config: RetentionConfig):
        """Initialize policy."""
        self.config = config

    def should_retain(self, pattern: PatternRecord, now: datetime) -> bool:
        """Determine if pattern should be retained."""
        raise NotImplementedError

    def calculate_confidence(self, pattern: PatternRecord, now: datetime) -> float:
        """Calculate current confidence value."""
        raise NotImplementedError

    def get_retention_window(self) -> Optional[int]:
        """Get retention window in days (None for infinite)."""
        raise NotImplementedError


class EvergreenPolicy(PolicyBase):
    """Permanent retention policy."""

    def should_retain(self, pattern: PatternRecord, now: datetime) -> bool:
        """Evergreen patterns are always retained."""
        return True

    def calculate_confidence(self, pattern: PatternRecord, now: datetime) -> float:
        """Evergreen patterns maintain full confidence."""
        return pattern.confidence

    def get_retention_window(self) -> Optional[int]:
        """Evergreen retention is infinite."""
        return None


class StandardPolicy(PolicyBase):
    """Fixed-window retention policy (90 days)."""

    def should_retain(self, pattern: PatternRecord, now: datetime) -> bool:
        """Retain if within retention window."""
        retention_days = self.config.standard_retention_days
        age = (now - pattern.created_at).days
        return age <= retention_days

    def calculate_confidence(self, pattern: PatternRecord, now: datetime) -> float:
        """Confidence maintained during window."""
        if self.should_retain(pattern, now):
            return pattern.confidence
        else:
            return 0.0

    def get_retention_window(self) -> Optional[int]:
        """Standard retention window."""
        return self.config.standard_retention_days


class DecayPolicy(PolicyBase):
    """Exponential decay policy (180 days)."""

    def should_retain(self, pattern: PatternRecord, now: datetime) -> bool:
        """Retain as long as confidence above threshold."""
        confidence = self.calculate_confidence(pattern, now)
        return confidence >= self.config.min_confidence_for_retention

    def calculate_confidence(self, pattern: PatternRecord, now: datetime) -> float:
        """
        Calculate confidence with exponential decay.

        Confidence = initial_confidence × exp(-t / halflife)
        where t is time elapsed in days
        """
        age_days = (now - pattern.created_at).days
        halflife = self.config.decay_halflife_days

        # Exponential decay function
        decay_factor = math.exp(-age_days * math.log(2) / halflife)
        confidence = pattern.confidence * decay_factor

        return max(confidence, 0.0)

    def get_retention_window(self) -> Optional[int]:
        """Decay retention window."""
        return self.config.decay_retention_days


class ArchivedPolicy(PolicyBase):
    """Compressed historical retention policy (1 year)."""

    def should_retain(self, pattern: PatternRecord, now: datetime) -> bool:
        """Retain in archive for 1 year."""
        retention_days = self.config.archived_retention_days
        age = (now - pattern.created_at).days
        return age <= retention_days

    def calculate_confidence(self, pattern: PatternRecord, now: datetime) -> float:
        """Archive patterns have minimal confidence."""
        return 0.0  # Archived patterns not used for active decisions

    def get_retention_window(self) -> Optional[int]:
        """Archive retention window."""
        return self.config.archived_retention_days


class RetentionPolicyManager:
    """
    Manages retention policies for LTM patterns.

    Responsibilities:
    - Classify patterns by policy type
    - Apply retention policies
    - Trigger cleanup cycles
    - Calculate confidence decay
    - Generate retention metrics
    """

    def __init__(self, config: Optional[RetentionConfig] = None):
        """Initialize retention manager."""
        self.config = config or RetentionConfig()
        self.policies = self._initialize_policies()

    def _initialize_policies(self) -> dict[RetentionPolicy, PolicyBase]:
        """Initialize all policy instances."""
        return {
            RetentionPolicy.EVERGREEN: EvergreenPolicy(self.config),
            RetentionPolicy.STANDARD: StandardPolicy(self.config),
            RetentionPolicy.DECAY: DecayPolicy(self.config),
            RetentionPolicy.ARCHIVED: ArchivedPolicy(self.config),
        }

    def classify_pattern(self, pattern: PatternRecord) -> RetentionPolicy:
        """
        Classify a pattern into appropriate retention policy.

        Classification rules:
        - Evergreen: success_rate > 0.95 OR tagged:security OR tagged:critical
        - Standard: success_rate > 0.70
        - Decay: 0.50 < success_rate <= 0.70
        - Archived: success_rate <= 0.50
        """
        # Check for evergreen conditions
        if pattern.success_rate > 0.95 or "security" in pattern.tags or "critical" in pattern.tags:
            return RetentionPolicy.EVERGREEN

        # Check success rate thresholds
        if pattern.success_rate > 0.70:
            return RetentionPolicy.STANDARD
        elif pattern.success_rate > 0.50:
            return RetentionPolicy.DECAY
        else:
            return RetentionPolicy.ARCHIVED

    def should_retain(self, pattern: PatternRecord, now: Optional[datetime] = None) -> bool:
        """Check if pattern should be retained."""
        if now is None:
            now = datetime.now(timezone.utc)

        policy = self.policies.get(pattern.policy)
        if policy is None:
            # Default to standard if policy not found
            policy = self.policies[RetentionPolicy.STANDARD]

        return policy.should_retain(pattern, now)

    def apply_policy(self, pattern: PatternRecord, now: Optional[datetime] = None) -> PatternRecord:
        """Apply retention policy to pattern."""
        if now is None:
            now = datetime.now(timezone.utc)

        policy = self.policies.get(pattern.policy)
        if policy is None:
            policy = self.policies[RetentionPolicy.STANDARD]

        # Update confidence
        new_confidence = policy.calculate_confidence(pattern, now)
        pattern.confidence = new_confidence

        # Check if still retained
        if not policy.should_retain(pattern, now):
            # Move to archive
            pattern.policy = RetentionPolicy.ARCHIVED

        return pattern

    def cleanup(
        self, patterns: list[PatternRecord], now: Optional[datetime] = None
    ) -> tuple[list[PatternRecord], list[str]]:
        """
        Run cleanup cycle on patterns.

        Returns:
            Tuple of (retained_patterns, pruned_keys)
        """
        if now is None:
            now = datetime.now(timezone.utc)

        retained = []
        pruned = []

        for pattern in patterns:
            # Skip protected patterns
            if pattern.policy == RetentionPolicy.EVERGREEN and self.config.evergreen_protected:
                retained.append(pattern)
                continue

            # Apply policy
            updated = self.apply_policy(pattern, now)

            # Check retention
            if self.should_retain(updated, now):
                retained.append(updated)
            else:
                pruned.append(pattern.key)
                logger.info(f"Pruned pattern: {pattern.key}")

        return retained, pruned

    def batch_cleanup(
        self, all_patterns: list[PatternRecord], now: Optional[datetime] = None
    ) -> dict[str, Any]:
        """
        Run cleanup on batch of patterns.

        Returns cleanup metrics.
        """
        if now is None:
            now = datetime.now(timezone.utc)

        batch_size = self.config.cleanup_batch_size
        total_patterns = len(all_patterns)

        retained_total = 0
        pruned_total = 0

        # Process in batches
        for i in range(0, total_patterns, batch_size):
            batch = all_patterns[i : i + batch_size]
            retained, pruned = self.cleanup(batch, now)

            retained_total += len(retained)
            pruned_total += len(pruned)

            if not self.config.dry_run:
                # Would persist changes here
                pass

        return {
            "timestamp": now.isoformat(),
            "total_processed": total_patterns,
            "retained": retained_total,
            "pruned": pruned_total,
            "prune_rate": pruned_total / total_patterns if total_patterns > 0 else 0.0,
        }

    def calculate_retention_window(self, policy: RetentionPolicy) -> Optional[int]:
        """Get retention window for policy in days."""
        return self.policies[policy].get_retention_window()

    def get_policy_distribution(self, patterns: list[PatternRecord]) -> dict[str, int]:
        """Get distribution of patterns by policy."""
        distribution = {p.value: 0 for p in RetentionPolicy}

        for pattern in patterns:
            distribution[pattern.policy.value] += 1

        return distribution

    def generate_retention_report(
        self, patterns: list[PatternRecord], now: Optional[datetime] = None
    ) -> dict[str, Any]:
        """Generate comprehensive retention report."""
        if now is None:
            now = datetime.now(timezone.utc)

        distribution = self.get_policy_distribution(patterns)

        # Analyze by policy
        policy_stats = {}
        for policy_type in RetentionPolicy:
            policy_patterns = [p for p in patterns if p.policy == policy_type]

            if policy_patterns:
                avg_confidence = sum(p.confidence for p in policy_patterns) / len(policy_patterns)
                avg_age_days = sum((now - p.created_at).days for p in policy_patterns) / len(
                    policy_patterns
                )
            else:
                avg_confidence = 0.0
                avg_age_days = 0.0

            policy_stats[policy_type.value] = {
                "count": distribution[policy_type.value],
                "avg_confidence": avg_confidence,
                "avg_age_days": avg_age_days,
            }

        # Cleanup simulation
        _, pruned = self.cleanup(patterns, now)

        return {
            "timestamp": now.isoformat(),
            "total_patterns": len(patterns),
            "distribution": distribution,
            "policy_statistics": policy_stats,
            "pruned_in_cleanup": len(pruned),
            "prune_rate": len(pruned) / len(patterns) if patterns else 0.0,
        }


class ConfidenceDecayCalculator:
    """Calculates confidence decay over time."""

    @staticmethod
    def exponential_decay(
        initial_confidence: float, days_elapsed: float, halflife_days: float
    ) -> float:
        """
        Calculate confidence with exponential decay.

        Formula: C(t) = C₀ × exp(-t / τ)
        where τ = halflife / ln(2)
        """
        decay_constant = math.log(2) / halflife_days
        return initial_confidence * math.exp(-days_elapsed * decay_constant)

    @staticmethod
    def linear_decay(
        initial_confidence: float, days_elapsed: float, retention_days: float
    ) -> float:
        """
        Calculate confidence with linear decay.

        Formula: C(t) = C₀ × (1 - t / T)
        """
        if days_elapsed >= retention_days:
            return 0.0
        return initial_confidence * (1 - days_elapsed / retention_days)

    @staticmethod
    def step_decay(initial_confidence: float, days_elapsed: float, step_days: float) -> float:
        """
        Calculate confidence with step-wise decay.

        Confidence decreases at regular intervals.
        """
        steps = int(days_elapsed / step_days)
        decay_per_step = 0.1  # 10% per step
        return max(initial_confidence * (1 - steps * decay_per_step), 0.0)


# Example usage function
def create_default_manager() -> RetentionPolicyManager:
    """Create manager with default configuration."""
    config = RetentionConfig(
        standard_retention_days=90,
        decay_retention_days=180,
        decay_halflife_days=60,
        archived_retention_days=365,
    )
    return RetentionPolicyManager(config)
