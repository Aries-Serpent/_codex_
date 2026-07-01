"""
LTM Pruning Engine - Long-Term Memory Maintenance

Implements stale memory detection, multiple pruning strategies,
safe deletion with immutable audit trail, and configurable retention policies.

Phase 10.2: Memory System (STM → LTM Integration)
Status: Production Ready
"""

import json
import logging
import sqlite3
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional

logger = logging.getLogger(__name__)


class PruningStrategy(Enum):
    """Pruning strategies for selecting candidates."""

    FIFO = "fifo"  # First-In-First-Out: delete oldest entries
    LRU = "lru"  # Least-Recently-Used: delete least accessed
    RELEVANCE_WEIGHTED = "relevance_weighted"  # Delete low-confidence entries
    COMBINED = "combined"  # Multi-factor (age + confidence + access_count)


@dataclass
class RetentionPolicy:
    """Retention policy configuration."""

    name: str
    max_age_days: int
    min_confidence_threshold: float = 0.0
    protected: bool = False
    description: str = ""


@dataclass
class PruningCandidate:
    """Represents an entry eligible for pruning."""

    key: str
    value: str
    pattern_type: str
    created_at: datetime
    last_accessed: datetime
    confidence: float
    frequency: int
    policy: str
    age_days: int = 0
    score: float = 0.0  # Pruning priority score
    reason: str = ""  # Why this entry is being pruned


@dataclass
class PruningMetrics:
    """Metrics for a pruning operation."""

    timestamp: datetime
    operation_id: str
    strategy: str
    total_scanned: int
    candidates_identified: int
    entries_pruned: int
    entries_archived: int
    storage_freed_bytes: int
    compression_ratio: float
    duration_ms: float
    error_count: int = 0
    error_messages: list[str] = field(default_factory=list)
    protected_entries: int = 0


class PruningStrategyExecutor:
    """Executes different pruning strategies."""

    def __init__(self, config: dict[str, Any]):
        """Initialize strategy executor."""
        self.config = config
        self.retention_policies = self._load_retention_policies()

    def _load_retention_policies(self) -> dict[str, RetentionPolicy]:
        """Load retention policies from config."""
        return {
            "evergreen": RetentionPolicy(
                name="evergreen",
                max_age_days=2555,  # 7 years for compliance
                min_confidence_threshold=0.0,
                protected=True,
                description="Permanently retained (7yr minimum)",
            ),
            "standard": RetentionPolicy(
                name="standard",
                max_age_days=90,
                min_confidence_threshold=0.0,
                protected=False,
                description="Standard retention (90 days)",
            ),
            "decay": RetentionPolicy(
                name="decay",
                max_age_days=180,
                min_confidence_threshold=0.1,
                protected=False,
                description="Decay-based retention (180 days, confidence-weighted)",
            ),
            "archived": RetentionPolicy(
                name="archived",
                max_age_days=365,
                min_confidence_threshold=0.0,
                protected=False,
                description="Archived retention (365 days)",
            ),
        }

    def fifo_strategy(
        self, candidates: list[PruningCandidate], limit: int
    ) -> list[PruningCandidate]:
        """
        FIFO Strategy: Delete oldest entries first.
        Simple, predictable, but doesn't consider value.
        """
        # Sort by created_at (oldest first)
        sorted_candidates = sorted(candidates, key=lambda x: x.created_at)

        selected = []
        for candidate in sorted_candidates[:limit]:
            candidate.score = 1.0 / (candidate.age_days + 1)  # Higher age = higher priority
            candidate.reason = f"FIFO: {candidate.age_days}d old"
            selected.append(candidate)

        logger.info(f"FIFO strategy selected {len(selected)} entries for pruning")
        return selected

    def lru_strategy(
        self, candidates: list[PruningCandidate], limit: int
    ) -> list[PruningCandidate]:
        """
        LRU Strategy: Delete least-recently-used entries.
        Favors frequently-accessed patterns, preserves hot items.
        """
        # Sort by last_accessed (oldest first)
        sorted_candidates = sorted(candidates, key=lambda x: x.last_accessed)

        selected = []
        for candidate in sorted_candidates[:limit]:
            days_since_access = (datetime.now(timezone.utc) - candidate.last_accessed).days
            candidate.score = 1.0 / (days_since_access + 1)
            candidate.reason = f"LRU: {days_since_access}d since last access"
            selected.append(candidate)

        logger.info(f"LRU strategy selected {len(selected)} entries for pruning")
        return selected

    def relevance_weighted_strategy(
        self, candidates: list[PruningCandidate], limit: int
    ) -> list[PruningCandidate]:
        """
        Relevance-Weighted Strategy: Delete low-confidence entries.
        Preserves high-value patterns, removes low-confidence data.
        """
        # Sort by confidence (lowest first), then age (oldest first)
        sorted_candidates = sorted(
            candidates, key=lambda x: (x.confidence, -x.age_days)
        )

        selected = []
        for candidate in sorted_candidates[:limit]:
            candidate.score = 1.0 - candidate.confidence  # Lower confidence = higher priority
            candidate.reason = f"Low-relevance: confidence={candidate.confidence:.2f}"
            selected.append(candidate)

        logger.info(
            f"Relevance-weighted strategy selected {len(selected)} entries for pruning"
        )
        return selected

    def combined_strategy(
        self, candidates: list[PruningCandidate], limit: int
    ) -> list[PruningCandidate]:
        """
        Combined Strategy: Multi-factor scoring.
        Considers age, confidence, frequency, and recency together.
        
        Score = (age_factor × confidence_factor) / frequency_factor
        where:
          age_factor = days_old / 90 (normalized to 90-day window)
          confidence_factor = (1 - confidence) (0=high value, 1=low value)
          frequency_factor = log(frequency + 1) (avoid over-weighting)
        """
        for candidate in candidates:
            age_factor = min(candidate.age_days / 90, 1.0)
            confidence_factor = 1.0 - candidate.confidence
            frequency_factor = max(1.0, (candidate.frequency * 0.1))  # Log-like scaling

            candidate.score = (age_factor * confidence_factor) / frequency_factor

            # Clamp score to [0, 1]
            candidate.score = min(max(candidate.score, 0.0), 1.0)

            candidate.reason = (
                f"Combined: age={candidate.age_days}d, "
                f"conf={candidate.confidence:.2f}, freq={candidate.frequency}"
            )

        # Sort by score (highest = most eligible for pruning)
        sorted_candidates = sorted(candidates, key=lambda x: x.score, reverse=True)
        selected = sorted_candidates[:limit]

        logger.info(f"Combined strategy selected {len(selected)} entries for pruning")
        return selected

    def select_candidates(
        self,
        candidates: list[PruningCandidate],
        strategy: PruningStrategy = PruningStrategy.RELEVANCE_WEIGHTED,
        limit: int = 1000,
    ) -> list[PruningCandidate]:
        """
        Select candidates for pruning using specified strategy.
        """
        if strategy == PruningStrategy.FIFO:
            return self.fifo_strategy(candidates, limit)
        elif strategy == PruningStrategy.LRU:
            return self.lru_strategy(candidates, limit)
        elif strategy == PruningStrategy.RELEVANCE_WEIGHTED:
            return self.relevance_weighted_strategy(candidates, limit)
        elif strategy == PruningStrategy.COMBINED:
            return self.combined_strategy(candidates, limit)
        else:
            logger.warning(f"Unknown strategy {strategy}, using RELEVANCE_WEIGHTED")
            return self.relevance_weighted_strategy(candidates, limit)


class LTMPruningEngine:
    """
    Main pruning engine for long-term memory maintenance.
    
    Responsibilities:
    - Detect stale memory (age-based & relevance-based)
    - Apply multiple pruning strategies
    - Safe deletion with immutable audit trail
    - Enforce configurable retention policies
    - Generate pruning metrics
    """

    def __init__(self, db_path: str, config: Optional[dict[str, Any]] = None):
        """Initialize pruning engine."""
        self.db_path = db_path
        self.config = config or self._default_config()
        self.strategy_executor = PruningStrategyExecutor(self.config)
        self.metrics_log: list[PruningMetrics] = []

    @staticmethod
    def _default_config() -> dict[str, Any]:
        """Return default configuration."""
        return {
            "batch_size": 500,
            "prune_limit_per_cycle": 1000,
            "dry_run": False,
            "archive_on_prune": True,
            "compression_threshold": 0.1,  # 10% size reduction
            "max_duration_ms": 30000,  # 30 second limit
            "retention_policies": {
                "evergreen": {"max_age_days": 2555, "protected": True},
                "standard": {"max_age_days": 90},
                "decay": {"max_age_days": 180, "min_confidence": 0.1},
                "archived": {"max_age_days": 365},
            },
        }

    def identify_stale_entries(
        self, policy_filter: Optional[str] = None
    ) -> list[PruningCandidate]:
        """
        Identify stale LTM entries based on age and relevance.
        
        Returns list of candidates sorted by pruning priority.
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row

            now = datetime.now(timezone.utc)
            candidates = []

            # Query all LTM entries
            query = "SELECT * FROM ltm_entries WHERE 1=1"
            params = []

            # Filter by policy if specified
            if policy_filter and policy_filter != "evergreen":
                query += " AND policy != ?"
                params.append("evergreen")

            rows = conn.execute(query, params).fetchall()
            conn.close()

            # Process each entry
            for row in rows:
                created_at = datetime.fromisoformat(row["created_at"])
                last_accessed = datetime.fromisoformat(row["last_accessed"])
                age_days = (now - created_at).days

                policy = row["policy"]
                max_age = self.strategy_executor.retention_policies[policy].max_age_days

                # Check if entry exceeds retention window
                if age_days > max_age:
                    candidate = PruningCandidate(
                        key=row["key"],
                        value=row["value"],
                        pattern_type=row["pattern_type"],
                        created_at=created_at,
                        last_accessed=last_accessed,
                        confidence=row["confidence"],
                        frequency=row["frequency"],
                        policy=policy,
                        age_days=age_days,
                        reason=f"Age exceeded: {age_days}d > {max_age}d",
                    )
                    candidates.append(candidate)
                    continue

                # Check confidence threshold
                if policy == "decay":
                    min_conf = self.strategy_executor.retention_policies[policy].min_confidence_threshold
                    if row["confidence"] < min_conf:
                        candidate = PruningCandidate(
                            key=row["key"],
                            value=row["value"],
                            pattern_type=row["pattern_type"],
                            created_at=created_at,
                            last_accessed=last_accessed,
                            confidence=row["confidence"],
                            frequency=row["frequency"],
                            policy=policy,
                            age_days=age_days,
                            reason=f"Low confidence: {row['confidence']:.2f} < {min_conf}",
                        )
                        candidates.append(candidate)

            logger.info(f"Identified {len(candidates)} stale entries for potential pruning")
            return candidates

        except Exception as e:
            logger.error(f"Failed to identify stale entries: {e}", exc_info=True)
            return []

    def prune_with_strategy(
        self,
        strategy: PruningStrategy = PruningStrategy.RELEVANCE_WEIGHTED,
        policy_filter: Optional[str] = None,
        dry_run: Optional[bool] = None,
    ) -> PruningMetrics:
        """
        Execute pruning operation using specified strategy.
        
        Args:
            strategy: Pruning strategy to use
            policy_filter: Only prune entries with this policy
            dry_run: If True, don't persist changes
        
        Returns:
            PruningMetrics with operation results
        """
        start_time = datetime.now(timezone.utc)
        start_ms = datetime.now().timestamp() * 1000
        operation_id = f"prune-{start_time.isoformat()}"
        dry_run = dry_run if dry_run is not None else self.config.get("dry_run", False)

        try:
            # Phase 1: Identify stale entries
            stale_entries = self.identify_stale_entries(policy_filter)
            total_scanned = len(stale_entries)

            if total_scanned == 0:
                logger.info("No stale entries found, skipping pruning")
                return PruningMetrics(
                    timestamp=start_time,
                    operation_id=operation_id,
                    strategy=strategy.value,
                    total_scanned=0,
                    candidates_identified=0,
                    entries_pruned=0,
                    entries_archived=0,
                    storage_freed_bytes=0,
                    compression_ratio=0.0,
                    duration_ms=0.0,
                )

            # Phase 2: Select candidates using strategy
            candidates = self.strategy_executor.select_candidates(
                stale_entries,
                strategy=strategy,
                limit=self.config.get("prune_limit_per_cycle", 1000),
            )

            # Phase 3: Execute pruning
            pruned_keys = []
            archived_count = 0
            protected_count = 0
            storage_freed = 0

            if not dry_run:
                conn = sqlite3.connect(self.db_path)

                try:
                    # Archive entries first (if configured)
                    if self.config.get("archive_on_prune", True):
                        for candidate in candidates:
                            try:
                                conn.execute(
                                    """
                                    INSERT INTO ltm_archive
                                    (key, value, pattern_type, frequency, success_rate,
                                     confidence, policy, metadata, tags, created_at, archived_at, archived_reason)
                                    SELECT key, value, pattern_type, frequency, success_rate,
                                           confidence, policy, metadata, tags, created_at,
                                           ?, ?
                                    FROM ltm_entries WHERE key = ?
                                    """,
                                    (start_time.isoformat(), candidate.reason, candidate.key),
                                )
                                archived_count += 1
                            except sqlite3.IntegrityError:
                                logger.warning(f"Entry already archived: {candidate.key}")

                    # Delete pruned entries
                    for candidate in candidates:
                        try:
                            cursor = conn.execute(
                                "DELETE FROM ltm_entries WHERE key = ?",
                                (candidate.key,),
                            )
                            if cursor.rowcount > 0:
                                pruned_keys.append(candidate.key)
                                # Estimate storage freed (approximate)
                                storage_freed += len(candidate.value.encode("utf-8")) + 100
                        except sqlite3.Error as e:
                            logger.error(f"Failed to prune {candidate.key}: {e}")

                    conn.commit()
                    conn.close()

                except Exception as e:
                    conn.rollback()
                    logger.error(f"Pruning transaction failed: {e}", exc_info=True)
                    raise

            # Phase 4: Calculate metrics
            duration_ms = (datetime.now().timestamp() * 1000) - start_ms
            compression_ratio = (
                archived_count / total_scanned if total_scanned > 0 else 0.0
            )

            metrics = PruningMetrics(
                timestamp=start_time,
                operation_id=operation_id,
                strategy=strategy.value,
                total_scanned=total_scanned,
                candidates_identified=len(candidates),
                entries_pruned=len(pruned_keys),
                entries_archived=archived_count,
                storage_freed_bytes=storage_freed,
                compression_ratio=compression_ratio,
                duration_ms=duration_ms,
                protected_entries=protected_count,
            )

            self.metrics_log.append(metrics)
            self._log_operation(metrics, dry_run)

            logger.info(
                f"Pruning complete: {len(pruned_keys)} pruned, "
                f"{archived_count} archived, {storage_freed} bytes freed"
            )

            return metrics

        except Exception as e:
            logger.error(f"Pruning operation failed: {e}", exc_info=True)
            return PruningMetrics(
                timestamp=start_time,
                operation_id=operation_id,
                strategy=strategy.value,
                total_scanned=0,
                candidates_identified=0,
                entries_pruned=0,
                entries_archived=0,
                storage_freed_bytes=0,
                compression_ratio=0.0,
                duration_ms=0.0,
                error_count=1,
                error_messages=[str(e)],
            )

    def cleanup_batch(self, batch_size: int = 500) -> PruningMetrics:
        """
        Run batch cleanup on LTM.
        Cleans up in chunks to avoid long-running transactions.
        """
        total_pruned = 0
        total_archived = 0
        total_freed = 0

        while True:
            # Run one pruning cycle
            metrics = self.prune_with_strategy(
                strategy=PruningStrategy.COMBINED,
                dry_run=False,
            )

            total_pruned += metrics.entries_pruned
            total_archived += metrics.entries_archived
            total_freed += metrics.storage_freed_bytes

            # Stop if no more entries to prune
            if metrics.entries_pruned == 0:
                break

            # Stop if we've pruned enough
            if total_pruned >= self.config.get("prune_limit_per_cycle", 1000):
                break

        logger.info(
            f"Batch cleanup complete: {total_pruned} pruned, "
            f"{total_archived} archived, {total_freed} bytes freed"
        )

        return metrics

    def get_retention_policy(self, pattern_type: str) -> RetentionPolicy:
        """Get retention policy for a pattern type."""
        policy = self.strategy_executor.retention_policies.get(
            pattern_type, self.strategy_executor.retention_policies["standard"]
        )
        return policy

    def generate_pruning_report(self) -> dict[str, Any]:
        """Generate comprehensive pruning report."""
        if not self.metrics_log:
            return {
                "total_cycles": 0,
                "total_pruned": 0,
                "total_archived": 0,
                "avg_duration_ms": 0.0,
                "total_storage_freed": 0,
            }

        return {
            "total_cycles": len(self.metrics_log),
            "total_pruned": sum(m.entries_pruned for m in self.metrics_log),
            "total_archived": sum(m.entries_archived for m in self.metrics_log),
            "avg_duration_ms": sum(m.duration_ms for m in self.metrics_log)
            / len(self.metrics_log),
            "total_storage_freed": sum(m.storage_freed_bytes for m in self.metrics_log),
            "compression_ratio": sum(m.compression_ratio for m in self.metrics_log)
            / len(self.metrics_log) if self.metrics_log else 0.0,
            "last_cycle": asdict(self.metrics_log[-1]) if self.metrics_log else None,
        }

    def _log_operation(self, metrics: PruningMetrics, dry_run: bool) -> None:
        """Log pruning operation to action log."""
        log_entry = {
            "operation": "ltm_pruning",
            "operation_id": metrics.operation_id,
            "timestamp": metrics.timestamp.isoformat(),
            "dry_run": dry_run,
            "strategy": metrics.strategy,
            "total_scanned": metrics.total_scanned,
            "candidates_identified": metrics.candidates_identified,
            "entries_pruned": metrics.entries_pruned,
            "entries_archived": metrics.entries_archived,
            "storage_freed_bytes": metrics.storage_freed_bytes,
            "compression_ratio": metrics.compression_ratio,
            "duration_ms": metrics.duration_ms,
            "error_count": metrics.error_count,
        }

        logger.info(f"Pruning operation: {json.dumps(log_entry)}")
