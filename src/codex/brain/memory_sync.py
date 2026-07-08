"""
Memory Sync System — STM → LTM Consolidation

PHASE 10.2: Production memory consolidation engine with pattern discovery,
duplicate detection, fuzzy matching, and long-term archival.

Status: Production Ready (2026-07-13)
"""

from __future__ import annotations

import json
import logging
import math
import sqlite3
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta, timezone
from difflib import SequenceMatcher
from enum import Enum
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)


class PatternType(Enum):
    """Pattern type enumeration."""

    DECISION = "decision"
    ERROR = "error"
    PERFORMANCE = "performance"
    SUCCESS = "success"
    RISK = "risk"


class RetentionPolicy(Enum):
    """Retention policy enumeration."""

    EVERGREEN = "evergreen"
    STANDARD = "standard"
    DECAY = "decay"
    ARCHIVED = "archived"


class ImprovementArea(Enum):
    """Categories for improvement tracking."""

    ML_PATTERN_FEEDING = "ML_PATTERN_FEEDING"
    CI_SELF_HEALING = "CI_SELF_HEALING"
    AGENT_CHAINING = "AGENT_CHAINING"
    COVERAGE_IMPROVEMENT = "COVERAGE_IMPROVEMENT"
    PERFORMANCE_OPTIMIZATION = "PERFORMANCE_OPTIMIZATION"
    SECURITY_HARDENING = "SECURITY_HARDENING"
    ERROR_RESILIENCE = "ERROR_RESILIENCE"


@dataclass
class PatternEntry:
    """Represents a single pattern entry in memory."""

    key: str
    value: str
    pattern_type: PatternType
    frequency: int = 1
    success_rate: float = 0.5
    confidence: float = 0.0
    last_accessed: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict[str, Any] = field(default_factory=dict)
    tags: list[str] = field(default_factory=list)
    policy: Optional[RetentionPolicy] = None
    improvement_areas: list[str] = field(default_factory=list)


@dataclass
class ConsolidationMetrics:
    """Metrics for a consolidation cycle."""

    timestamp: datetime
    stm_count_before: int
    stm_count_after: int
    ltm_count_before: int
    ltm_count_after: int
    patterns_promoted: int
    patterns_pruned: int
    patterns_merged: int
    compression_rate: float
    duration_ms: float
    promotion_accuracy: float = 0.0


@dataclass
class DuplicateMatch:
    """Result of duplicate detection."""

    key1: str
    key2: str
    similarity: float
    merge_target: str  # Which key to keep


class MemorySyncEngine:
    """
    Production memory consolidation system.

    Workflow:
    1. OBSERVE: Query current memory state
    2. ORIENT: Analyze patterns, identify candidates
    3. DECIDE: Generate consolidation plan
    4. ACT: Execute promotions and pruning
    5. ANALYZE: Measure results and log
    """

    # Keyword → ImprovementArea mapping
    KEYWORD_MAPPING = {
        "stm": ImprovementArea.ML_PATTERN_FEEDING,
        "ltm": ImprovementArea.ML_PATTERN_FEEDING,
        "memory": ImprovementArea.ML_PATTERN_FEEDING,
        "consolidat": ImprovementArea.ML_PATTERN_FEEDING,
        "ci": ImprovementArea.CI_SELF_HEALING,
        "fail": ImprovementArea.CI_SELF_HEALING,
        "heal": ImprovementArea.CI_SELF_HEALING,
        "self-heal": ImprovementArea.CI_SELF_HEALING,
        "agent": ImprovementArea.AGENT_CHAINING,
        "chain": ImprovementArea.AGENT_CHAINING,
        "orchestrat": ImprovementArea.AGENT_CHAINING,
        "coverage": ImprovementArea.COVERAGE_IMPROVEMENT,
        "test": ImprovementArea.COVERAGE_IMPROVEMENT,
        "gap": ImprovementArea.COVERAGE_IMPROVEMENT,
        "performance": ImprovementArea.PERFORMANCE_OPTIMIZATION,
        "speed": ImprovementArea.PERFORMANCE_OPTIMIZATION,
        "latency": ImprovementArea.PERFORMANCE_OPTIMIZATION,
        "security": ImprovementArea.SECURITY_HARDENING,
        "vuln": ImprovementArea.SECURITY_HARDENING,
        "inject": ImprovementArea.SECURITY_HARDENING,
        "xss": ImprovementArea.SECURITY_HARDENING,
        "error": ImprovementArea.ERROR_RESILIENCE,
        "exception": ImprovementArea.ERROR_RESILIENCE,
        "resilience": ImprovementArea.ERROR_RESILIENCE,
    }

    def __init__(self, config: Optional[dict[str, Any]] = None):
        """Initialize sync engine with configuration."""
        self.config = config or self._default_config()
        self.db_path = self.config.get("db_path", ":memory:")
        self.ltm_path = Path(self.config.get("ltm_path", ".codex/ltm/"))
        self.metrics_log: list[ConsolidationMetrics] = []
        self._init_storage()

    @staticmethod
    def _default_config() -> dict[str, Any]:
        """Return default configuration."""
        return {
            "db_path": ":memory:",
            "ltm_path": ".codex/ltm/",
            "stm_capacity": 500,
            "ltm_capacity": 10000,
            "consolidation_threshold": 0.80,
            "frequency_threshold": 3,
            "promotion_score_threshold": 0.60,
            "max_promote_per_cycle": 100,
            "max_prune_per_cycle": 1000,
            "discovery_interval_seconds": 3600,
            "cleanup_interval_seconds": 86400,
            "duplicate_similarity_threshold": 0.85,
        }

    def _init_storage(self) -> None:
        """Initialize LTM storage directory."""
        self.ltm_path.mkdir(parents=True, exist_ok=True)

    def run(self, session_context: Optional[dict[str, Any]] = None) -> ConsolidationMetrics:
        """
        Execute full consolidation cycle.

        Returns:
            ConsolidationMetrics with consolidation results
        """
        start_time = time.time()

        try:
            # Phase 1: OBSERVE
            state_before = self._observe()

            # Early exit if STM not full
            fill_ratio = (
                state_before["stm_count"] / state_before["stm_capacity"]
                if state_before["stm_capacity"] > 0
                else 0
            )
            if fill_ratio < self.config["consolidation_threshold"]:
                logger.debug(f"STM fill ratio {fill_ratio:.1%} below threshold, skipping")
                return self._create_empty_metrics(state_before, state_before, 0, 0, 0)

            # Phase 2: ORIENT
            hot_entries = self._orient(state_before)
            cold_entries = self._find_cold_ltm_entries()

            # Check for duplicates
            duplicates = self._detect_duplicates(hot_entries)

            # Phase 3: DECIDE
            plan = self._decide(hot_entries, cold_entries, duplicates)

            # Phase 4: ACT
            promoted, pruned, merged = self._act(plan)

            # Phase 5: ANALYZE
            state_after = self._observe()
            metrics = self._analyze(
                state_before, state_after, promoted, pruned, merged, time.time() - start_time
            )

            self.metrics_log.append(metrics)
            self._log_operation(metrics)
            self._export_ltm_inventory()

            return metrics

        except Exception as e:
            logger.error(f"Consolidation cycle failed: {e}", exc_info=True)
            raise

    def _observe(self) -> dict[str, Any]:
        """Phase 1: Observe current memory state."""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row

            # Query STM stats
            stm_stats = conn.execute("SELECT COUNT(*) as count FROM stm_entries").fetchone()

            # Query LTM stats
            ltm_stats = conn.execute("SELECT COUNT(*) as count FROM ltm_entries").fetchone()

            conn.close()

            return {
                "timestamp": datetime.now(timezone.utc),
                "stm_count": stm_stats["count"] if stm_stats else 0,
                "ltm_count": ltm_stats["count"] if ltm_stats else 0,
                "stm_capacity": self.config["stm_capacity"],
                "ltm_capacity": self.config["ltm_capacity"],
            }
        except Exception as e:
            logger.error(f"Failed to observe memory state: {e}")
            return {
                "timestamp": datetime.now(timezone.utc),
                "stm_count": 0,
                "ltm_count": 0,
                "stm_capacity": self.config["stm_capacity"],
                "ltm_capacity": self.config["ltm_capacity"],
            }

    def _orient(self, state: dict[str, Any]) -> list[PatternEntry]:
        """Phase 2: Identify hot entries for promotion."""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row

            # Find hot entries (frequency >= threshold)
            frequency_threshold = self.config["frequency_threshold"]
            max_promote = self.config["max_promote_per_cycle"]

            hot_entries = conn.execute(f"""
                SELECT key, value, pattern_type, frequency, success_rate,
                       confidence, last_accessed, created_at, metadata, tags
                FROM stm_entries
                WHERE frequency >= {frequency_threshold}
                ORDER BY frequency DESC, last_accessed DESC
                LIMIT {max_promote}
                """).fetchall()

            conn.close()

            entries = []
            for row in hot_entries:
                entry = PatternEntry(
                    key=row["key"],
                    value=row["value"],
                    pattern_type=PatternType(row["pattern_type"]),
                    frequency=row["frequency"],
                    success_rate=row["success_rate"],
                    confidence=row["confidence"],
                    last_accessed=datetime.fromisoformat(row["last_accessed"]),
                    created_at=datetime.fromisoformat(row["created_at"]),
                    metadata=json.loads(row["metadata"]) if row["metadata"] else {},
                    tags=json.loads(row["tags"]) if row["tags"] else [],
                )
                entries.append(entry)

            logger.info(f"Identified {len(entries)} hot entries for promotion")
            return entries

        except Exception as e:
            logger.error(f"Failed to identify hot entries: {e}")
            return []

    def _find_cold_ltm_entries(self) -> list[tuple[str, float]]:
        """Find stale LTM entries eligible for pruning or archiving."""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row

            # Find entries past retention window
            cutoff_date = (datetime.now(timezone.utc) - timedelta(days=90)).isoformat()

            cold_entries = conn.execute(f"""
                SELECT key, confidence
                FROM ltm_entries
                WHERE created_at < '{cutoff_date}'
                AND confidence < 0.3
                AND policy != '{RetentionPolicy.EVERGREEN.value}'
                ORDER BY confidence ASC
                LIMIT {self.config['max_prune_per_cycle']}
                """).fetchall()

            conn.close()

            return [(row["key"], row["confidence"]) for row in cold_entries]

        except Exception as e:
            logger.error(f"Failed to find cold entries: {e}")
            return []

    def _detect_duplicates(self, entries: list[PatternEntry]) -> list[DuplicateMatch]:
        """Detect duplicate patterns using fuzzy matching."""
        duplicates: list[DuplicateMatch] = []
        threshold = self.config["duplicate_similarity_threshold"]

        for i, entry1 in enumerate(entries):
            for entry2 in entries[i + 1 :]:
                similarity = self._calculate_similarity(entry1.key, entry2.key)
                if similarity >= threshold:
                    # Keep higher-confidence entry
                    if entry1.confidence >= entry2.confidence:
                        merge_target = entry1.key
                    else:
                        merge_target = entry2.key

                    duplicates.append(
                        DuplicateMatch(
                            key1=entry1.key,
                            key2=entry2.key,
                            similarity=similarity,
                            merge_target=merge_target,
                        )
                    )

        logger.info(f"Detected {len(duplicates)} duplicate pairs")
        return duplicates

    @staticmethod
    def _calculate_similarity(s1: str, s2: str) -> float:
        """Calculate similarity between two strings (0.0-1.0)."""
        return SequenceMatcher(None, s1, s2).ratio()

    def _decide(
        self,
        hot_entries: list[PatternEntry],
        cold_entries: list[tuple[str, float]],
        duplicates: list[DuplicateMatch],
    ) -> dict[str, Any]:
        """Phase 3: Generate consolidation plan."""
        plan = {
            "promote": [],
            "prune": [],
            "merge": [],
            "timestamp": datetime.now(timezone.utc),
        }

        # Score and rank hot entries for promotion
        scored_entries = []
        for entry in hot_entries:
            score = self._calculate_pattern_score(entry)
            if score >= self.config["promotion_score_threshold"]:
                scored_entries.append((entry, score))

        # Sort by score descending
        scored_entries.sort(key=lambda x: x[1], reverse=True)

        # Add to promotion plan
        plan["promote"] = [entry for entry, _ in scored_entries]

        # Add cold entries to prune
        plan["prune"] = [key for key, _ in cold_entries]

        # Add duplicates to merge
        plan["merge"] = duplicates

        logger.info(
            f"Plan: promote {len(plan['promote'])}, merge {len(plan['merge'])}, "
            f"prune {len(plan['prune'])}"
        )
        return plan

    def _calculate_pattern_score(self, entry: PatternEntry) -> float:
        """
        Calculate pattern score for promotion.

        Score = (Frequency × Recency × Importance) / Age_Decay
        Range: 0.0 - 1.0
        """
        now = datetime.now(timezone.utc)

        # Frequency component (normalized to threshold)
        frequency_norm = min(entry.frequency / self.config["frequency_threshold"], 1.0)

        # Recency component (exponential decay, 30-day half-life)
        days_since_access = (now - entry.last_accessed).total_seconds() / 86400
        recency = math.exp(-(days_since_access / 30))

        # Importance component (success rate)
        importance = entry.success_rate

        # Age decay (older patterns less valuable)
        days_since_creation = (now - entry.created_at).total_seconds() / 86400
        age_decay = math.exp(days_since_creation / 90)

        score = (frequency_norm * recency * importance) / age_decay
        return min(score, 1.0)

    def _act(self, plan: dict[str, Any]) -> tuple[int, int, int]:
        """Phase 4: Execute consolidation plan."""
        promoted = 0
        pruned = 0
        merged = 0

        try:
            conn = sqlite3.connect(self.db_path)
            now = datetime.now(timezone.utc).isoformat()

            # Handle merges first (combine duplicates)
            for dup in plan["merge"]:
                merged += self._merge_duplicate_patterns(conn, dup, now)

            # Promote entries to LTM
            for entry in plan["promote"]:
                confidence = self._calculate_pattern_score(entry)
                policy = self._determine_retention_policy(entry, confidence)
                improvement_areas = self._extract_improvement_areas(entry)

                conn.execute(
                    """
                    INSERT OR REPLACE INTO ltm_entries
                    (key, value, pattern_type, frequency, success_rate,
                     confidence, created_at, last_accessed, metadata, tags, policy, improvement_areas)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        entry.key,
                        entry.value,
                        entry.pattern_type.value,
                        entry.frequency,
                        entry.success_rate,
                        confidence,
                        entry.created_at.isoformat(),
                        now,
                        json.dumps(entry.metadata),
                        json.dumps(entry.tags),
                        policy.value,
                        json.dumps(improvement_areas),
                    ),
                )

                # Remove from STM
                conn.execute("DELETE FROM stm_entries WHERE key = ?", (entry.key,))
                promoted += 1

            # Prune cold entries
            for key in plan["prune"]:
                # Move to archive first
                conn.execute(
                    "INSERT INTO ltm_archive SELECT * FROM ltm_entries WHERE key = ?", (key,)
                )
                # Delete from active LTM
                conn.execute("DELETE FROM ltm_entries WHERE key = ?", (key,))
                pruned += 1

            conn.commit()
            conn.close()

            logger.info(f"Promoted {promoted}, merged {merged}, pruned {pruned} patterns")

        except Exception as e:
            logger.error(f"Failed to execute consolidation plan: {e}")

        return promoted, pruned, merged

    def _merge_duplicate_patterns(
        self, conn: sqlite3.Connection, dup: DuplicateMatch, now: str
    ) -> int:
        """Merge duplicate patterns, keeping higher-confidence entry."""
        try:
            # Get both entries
            keeper_row = conn.execute(
                "SELECT * FROM stm_entries WHERE key = ?", (dup.merge_target,)
            ).fetchone()
            loser_row = conn.execute(
                "SELECT * FROM stm_entries WHERE key = ?",
                (dup.key2 if dup.merge_target == dup.key1 else dup.key1,),
            ).fetchone()

            if not keeper_row or not loser_row:
                return 0

            # Merge frequency and metadata
            merged_frequency = keeper_row["frequency"] + loser_row["frequency"]
            keeper_metadata = json.loads(keeper_row["metadata"]) if keeper_row["metadata"] else {}
            loser_metadata = json.loads(loser_row["metadata"]) if loser_row["metadata"] else {}

            # Union metadata keys
            merged_metadata = {**keeper_metadata, **loser_metadata}

            # Union tags
            keeper_tags = json.loads(keeper_row["tags"]) if keeper_row["tags"] else []
            loser_tags = json.loads(loser_row["tags"]) if loser_row["tags"] else []
            merged_tags = list(set(keeper_tags + loser_tags))

            # Update keeper
            conn.execute(
                """
                UPDATE stm_entries
                SET frequency = ?, metadata = ?, tags = ?, last_accessed = ?
                WHERE key = ?
                """,
                (
                    merged_frequency,
                    json.dumps(merged_metadata),
                    json.dumps(merged_tags),
                    now,
                    dup.merge_target,
                ),
            )

            # Delete loser
            loser_key = dup.key2 if dup.merge_target == dup.key1 else dup.key1
            conn.execute("DELETE FROM stm_entries WHERE key = ?", (loser_key,))

            return 1

        except Exception as e:
            logger.error(f"Failed to merge duplicates: {e}")
            return 0

    @staticmethod
    def _determine_retention_policy(entry: PatternEntry, confidence: float) -> RetentionPolicy:
        """Determine appropriate retention policy for an entry."""
        if entry.success_rate > 0.95 or "security" in entry.tags or "critical" in entry.tags:
            return RetentionPolicy.EVERGREEN
        elif entry.success_rate > 0.70:
            return RetentionPolicy.STANDARD
        elif entry.success_rate > 0.50:
            return RetentionPolicy.DECAY
        else:
            return RetentionPolicy.ARCHIVED

    def _extract_improvement_areas(self, entry: PatternEntry) -> list[str]:
        """Extract improvement areas from entry tags and content."""
        areas: set[str] = set()

        # Check tags
        for tag in entry.tags:
            for keyword, area in self.KEYWORD_MAPPING.items():
                if keyword.lower() in tag.lower():
                    areas.add(area.value)

        # Check key
        key_lower = entry.key.lower()
        for keyword, area in self.KEYWORD_MAPPING.items():
            if keyword.lower() in key_lower:
                areas.add(area.value)

        # Check metadata
        metadata_str = json.dumps(entry.metadata).lower()
        for keyword, area in self.KEYWORD_MAPPING.items():
            if keyword.lower() in metadata_str:
                areas.add(area.value)

        return list(areas)

    def _analyze(
        self,
        state_before: dict[str, Any],
        state_after: dict[str, Any],
        promoted: int,
        pruned: int,
        merged: int,
        duration: float,
    ) -> ConsolidationMetrics:
        """Phase 5: Analyze results and generate metrics."""

        compression_rate = 0.0
        if (state_after["stm_count"] + state_after["ltm_count"]) > 0:
            compression_rate = state_after["ltm_count"] / (
                state_after["stm_count"] + state_after["ltm_count"]
            )

        metrics = ConsolidationMetrics(
            timestamp=state_after["timestamp"],
            stm_count_before=state_before["stm_count"],
            stm_count_after=state_after["stm_count"],
            ltm_count_before=state_before["ltm_count"],
            ltm_count_after=state_after["ltm_count"],
            patterns_promoted=promoted,
            patterns_pruned=pruned,
            patterns_merged=merged,
            compression_rate=compression_rate,
            duration_ms=duration * 1000,
        )

        return metrics

    @staticmethod
    def _create_empty_metrics(
        state_before: dict[str, Any],
        state_after: dict[str, Any],
        promoted: int,
        pruned: int,
        merged: int,
    ) -> ConsolidationMetrics:
        """Create empty metrics for early exit."""
        return ConsolidationMetrics(
            timestamp=state_after["timestamp"],
            stm_count_before=state_before["stm_count"],
            stm_count_after=state_after["stm_count"],
            ltm_count_before=state_before["ltm_count"],
            ltm_count_after=state_after["ltm_count"],
            patterns_promoted=promoted,
            patterns_pruned=pruned,
            patterns_merged=merged,
            compression_rate=0.0,
            duration_ms=0.0,
        )

    def _log_operation(self, metrics: ConsolidationMetrics) -> None:
        """Log consolidation operation to action log."""
        log_entry = {
            "operation": "memory_consolidation",
            "timestamp": metrics.timestamp.isoformat(),
            "stm_count": {"before": metrics.stm_count_before, "after": metrics.stm_count_after},
            "ltm_count": {"before": metrics.ltm_count_before, "after": metrics.ltm_count_after},
            "patterns_promoted": metrics.patterns_promoted,
            "patterns_merged": metrics.patterns_merged,
            "patterns_pruned": metrics.patterns_pruned,
            "compression_rate": metrics.compression_rate,
            "duration_ms": metrics.duration_ms,
        }

        logger.info(f"Consolidation cycle: {json.dumps(log_entry)}")

    def _export_ltm_inventory(self) -> None:
        """Export LTM inventory to .codex/ltm/ltm_inventory.json."""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row

            # Fetch all LTM entries
            ltm_entries = conn.execute(
                "SELECT * FROM ltm_entries ORDER BY confidence DESC"
            ).fetchall()

            conn.close()

            patterns = []
            for row in ltm_entries:
                patterns.append(
                    {
                        "key": row["key"],
                        "name": row["key"].replace("_", " ").title(),
                        "pattern_type": row["pattern_type"],
                        "confidence": row["confidence"],
                        "frequency": row["frequency"],
                        "success_rate": row["success_rate"],
                        "tags": json.loads(row["tags"]) if row["tags"] else [],
                        "improvement_areas": (
                            json.loads(row["improvement_areas"]) if row["improvement_areas"] else []
                        ),
                        "policy": row["policy"],
                    }
                )

            inventory = {
                "metadata": {
                    "generated_at": datetime.now(timezone.utc).isoformat(),
                    "total_patterns": len(patterns),
                    "consolidation_cycles": len(self.metrics_log),
                },
                "patterns": patterns,
            }

            # Write inventory
            inventory_path = self.ltm_path / "ltm_inventory.json"
            with open(inventory_path, "w") as f:
                json.dump(inventory, f, indent=2)

            logger.info(f"Exported {len(patterns)} patterns to {inventory_path}")

        except Exception as e:
            logger.error(f"Failed to export LTM inventory: {e}")

    def get_metrics_summary(self) -> dict[str, Any]:
        """Get summary of all consolidation metrics."""
        if not self.metrics_log:
            return {}

        total_promoted = sum(m.patterns_promoted for m in self.metrics_log)
        total_pruned = sum(m.patterns_pruned for m in self.metrics_log)
        total_merged = sum(m.patterns_merged for m in self.metrics_log)
        avg_duration = sum(m.duration_ms for m in self.metrics_log) / len(self.metrics_log)

        return {
            "cycles": len(self.metrics_log),
            "total_promoted": total_promoted,
            "total_pruned": total_pruned,
            "total_merged": total_merged,
            "avg_duration_ms": avg_duration,
            "last_cycle": asdict(self.metrics_log[-1]) if self.metrics_log else None,
        }
