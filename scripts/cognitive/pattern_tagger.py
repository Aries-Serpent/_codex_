"""
Pattern Tagging System - Automatic Pattern Classification & Enrichment

Implements pattern classification (bug-fix, feature, security, optimization, refactor, etc.),
ImprovementArea tagging, relevance scoring with continuous updates,
automatic categorization using heuristics & ML, and pattern metadata enrichment.

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


class PatternCategory(Enum):
    """Pattern classification categories."""

    BUG_FIX = "bug_fix"  # Fixing identified bugs
    FEATURE = "feature"  # Adding new functionality
    SECURITY = "security"  # Security-related patterns
    OPTIMIZATION = "optimization"  # Performance improvements
    REFACTORING = "refactoring"  # Code refactoring
    TESTING = "testing"  # Test-related patterns
    DOCUMENTATION = "documentation"  # Documentation patterns
    CONFIGURATION = "configuration"  # Config management
    INFRASTRUCTURE = "infrastructure"  # Infra/DevOps patterns
    ERROR_HANDLING = "error_handling"  # Error handling strategies
    UNKNOWN = "unknown"  # Unclassified


class ImprovementArea(Enum):
    """Impact areas for pattern improvements."""

    CI_SELF_HEALING = "CI_SELF_HEALING"  # CI/CD healing patterns
    COVERAGE_IMPROVEMENT = "COVERAGE_IMPROVEMENT"  # Test coverage
    SECURITY_HARDENING = "SECURITY_HARDENING"  # Security enhancements
    PERFORMANCE_TUNING = "PERFORMANCE_TUNING"  # Performance patterns
    DOCUMENTATION_QUALITY = "DOCUMENTATION_QUALITY"  # Docs improvements
    ML_PATTERN_FEEDING = "ML_PATTERN_FEEDING"  # ML model training
    AGENT_CHAINING = "AGENT_CHAINING"  # Multi-agent orchestration
    DEPENDENCY_MANAGEMENT = "DEPENDENCY_MANAGEMENT"  # Dependency handling
    WORKFLOW_OPTIMIZATION = "WORKFLOW_OPTIMIZATION"  # Workflow improvements
    CODE_QUALITY = "CODE_QUALITY"  # General code quality


@dataclass
class TaggingRules:
    """Tagging rules for pattern classification."""

    keyword_patterns: dict[str, list[str]] = field(default_factory=dict)
    category_keywords: dict[PatternCategory, list[str]] = field(
        default_factory=dict
    )
    improvement_area_keywords: dict[ImprovementArea, list[str]] = field(
        default_factory=dict
    )
    confidence_thresholds: dict[str, float] = field(default_factory=dict)


@dataclass
class PatternTag:
    """Represents a single tag for a pattern."""

    name: str
    category: PatternCategory
    confidence: float  # 0.0-1.0
    improvement_areas: list[ImprovementArea] = field(default_factory=list)
    relevance_score: float = 0.5  # 1-10 scale
    source: str = "auto"  # "auto" or "manual"
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class TaggingMetrics:
    """Metrics for a tagging operation."""

    timestamp: datetime
    operation_id: str
    patterns_processed: int
    patterns_tagged: int
    avg_confidence: float
    avg_relevance_score: float
    duration_ms: float
    categories_assigned: dict[str, int] = field(default_factory=dict)
    improvement_areas_assigned: dict[str, int] = field(default_factory=dict)


class PatternTagger:
    """
    Automatic pattern classification and tagging system.
    
    Responsibilities:
    - Classify patterns into categories
    - Assign ImprovementArea tags
    - Calculate relevance scores
    - Update tags over time
    - Enrich metadata
    - Validate tagging consistency
    """

    def __init__(self, config: Optional[dict[str, Any]] = None):
        """Initialize pattern tagger."""
        self.config = config or self._default_config()
        self.rules = self._initialize_rules()
        self.metrics_log: list[TaggingMetrics] = []

    @staticmethod
    def _default_config() -> dict[str, Any]:
        """Return default configuration."""
        return {
            "confidence_threshold": 0.5,
            "relevance_min_score": 1,
            "relevance_max_score": 10,
            "enable_ml_classification": False,  # Future: ML-based classification
            "batch_size": 500,
        }

    def _initialize_rules(self) -> TaggingRules:
        """Initialize tagging rules from keywords and patterns."""
        rules = TaggingRules()

        # Category keywords
        rules.category_keywords = {
            PatternCategory.BUG_FIX: [
                "bug",
                "fix",
                "fixed",
                "error",
                "issue",
                "crash",
                "fail",
                "regression",
                "defect",
            ],
            PatternCategory.FEATURE: [
                "feature",
                "add",
                "implement",
                "new",
                "support",
                "enhancement",
                "capability",
            ],
            PatternCategory.SECURITY: [
                "security",
                "vulnerability",
                "exploit",
                "injection",
                "authentication",
                "authorization",
                "csrf",
                "xss",
                "secrets",
                "credentials",
            ],
            PatternCategory.OPTIMIZATION: [
                "optimize",
                "performance",
                "speed",
                "latency",
                "throughput",
                "memory",
                "cache",
                "efficient",
            ],
            PatternCategory.REFACTORING: [
                "refactor",
                "refactoring",
                "cleanup",
                "restructure",
                "reorganize",
                "simplify",
                "dedup",
            ],
            PatternCategory.TESTING: [
                "test",
                "testing",
                "unit",
                "integration",
                "coverage",
                "mock",
                "assert",
                "pytest",
            ],
            PatternCategory.DOCUMENTATION: [
                "doc",
                "documentation",
                "readme",
                "guide",
                "example",
                "comment",
                "docstring",
            ],
            PatternCategory.CONFIGURATION: [
                "config",
                "configuration",
                "setup",
                "environ",
                "variable",
                "setting",
                "yaml",
            ],
            PatternCategory.INFRASTRUCTURE: [
                "infra",
                "infrastructure",
                "devops",
                "deployment",
                "container",
                "docker",
                "kubernetes",
                "ci",
                "cd",
            ],
            PatternCategory.ERROR_HANDLING: [
                "exception",
                "error",
                "handling",
                "try",
                "except",
                "raise",
                "fallback",
            ],
        }

        # ImprovementArea keywords
        rules.improvement_area_keywords = {
            ImprovementArea.CI_SELF_HEALING: [
                "ci",
                "workflow",
                "github actions",
                "heal",
                "self-heal",
                "fail",
                "recovery",
            ],
            ImprovementArea.COVERAGE_IMPROVEMENT: [
                "coverage",
                "test",
                "pytest",
                "unit",
                "integration",
                "gap",
            ],
            ImprovementArea.SECURITY_HARDENING: [
                "security",
                "vulnerability",
                "codeql",
                "scan",
                "exploit",
                "crypto",
            ],
            ImprovementArea.PERFORMANCE_TUNING: [
                "performance",
                "latency",
                "throughput",
                "optimize",
                "speed",
                "memory",
            ],
            ImprovementArea.DOCUMENTATION_QUALITY: [
                "doc",
                "readme",
                "guide",
                "tutorial",
                "example",
                "clarity",
            ],
            ImprovementArea.ML_PATTERN_FEEDING: [
                "ml",
                "machine learning",
                "model",
                "training",
                "data",
                "pattern",
            ],
            ImprovementArea.AGENT_CHAINING: [
                "agent",
                "orchestr",
                "chain",
                "multi-agent",
                "workflow",
            ],
            ImprovementArea.DEPENDENCY_MANAGEMENT: [
                "dependency",
                "requirement",
                "pip",
                "package",
                "version",
                "upgrade",
            ],
            ImprovementArea.WORKFLOW_OPTIMIZATION: [
                "workflow",
                "process",
                "automation",
                "efficiency",
                "pipeline",
            ],
            ImprovementArea.CODE_QUALITY: [
                "quality",
                "lint",
                "format",
                "style",
                "refactor",
                "clean",
            ],
        }

        # Confidence thresholds
        rules.confidence_thresholds = {
            "keyword_match_exact": 0.95,
            "keyword_match_partial": 0.70,
            "keyword_match_weak": 0.50,
            "multi_keyword_match": 0.85,
        }

        return rules

    def classify_pattern(
        self, pattern_key: str, pattern_value: str
    ) -> tuple[PatternCategory, float]:
        """
        Classify a pattern into a category.
        
        Returns:
            (category, confidence_score)
        """
        # Combine key and value for analysis
        text = f"{pattern_key} {pattern_value}".lower()

        best_category = PatternCategory.UNKNOWN
        best_score = 0.0

        # Score each category
        for category, keywords in self.rules.category_keywords.items():
            # Count keyword matches
            matches = sum(1 for kw in keywords if kw in text)

            if matches == 0:
                continue

            # Calculate confidence based on number of matches
            if matches >= 3:
                confidence = self.rules.confidence_thresholds.get(
                    "multi_keyword_match", 0.85
                )
            elif matches >= 2:
                confidence = self.rules.confidence_thresholds.get(
                    "keyword_match_partial", 0.70
                )
            else:
                confidence = self.rules.confidence_thresholds.get(
                    "keyword_match_weak", 0.50
                )

            if confidence > best_score:
                best_score = confidence
                best_category = category

        return best_category, best_score

    def extract_improvement_areas(
        self, pattern_key: str, pattern_value: str, category: PatternCategory
    ) -> list[tuple[ImprovementArea, float]]:
        """
        Extract ImprovementArea tags for a pattern.
        
        Returns:
            List of (area, confidence) tuples
        """
        text = f"{pattern_key} {pattern_value}".lower()
        areas = []

        for area, keywords in self.rules.improvement_area_keywords.items():
            matches = sum(1 for kw in keywords if kw in text)

            if matches == 0:
                continue

            # Calculate confidence
            if matches >= 3:
                confidence = 0.90
            elif matches >= 2:
                confidence = 0.75
            else:
                confidence = 0.60

            areas.append((area, confidence))

        return areas

    def calculate_relevance_score(
        self,
        pattern_key: str,
        pattern_value: str,
        category: PatternCategory,
        frequency: int = 1,
        success_rate: float = 0.5,
        age_days: int = 0,
    ) -> float:
        """
        Calculate relevance score for a pattern (1-10 scale).
        
        Factors:
        - Category (some categories more important)
        - Frequency (repeated patterns more relevant)
        - Success rate (successful patterns more relevant)
        - Age (recent patterns more relevant)
        
        Returns:
            Score between 1 (least relevant) and 10 (most relevant)
        """
        # Base score by category
        category_scores = {
            PatternCategory.SECURITY: 9.5,
            PatternCategory.BUG_FIX: 8.5,
            PatternCategory.OPTIMIZATION: 7.5,
            PatternCategory.FEATURE: 7.0,
            PatternCategory.TESTING: 6.5,
            PatternCategory.REFACTORING: 5.5,
            PatternCategory.ERROR_HANDLING: 7.0,
            PatternCategory.INFRASTRUCTURE: 6.0,
            PatternCategory.CONFIGURATION: 5.0,
            PatternCategory.DOCUMENTATION: 4.5,
            PatternCategory.UNKNOWN: 3.0,
        }

        base_score = category_scores.get(category, 5.0)

        # Frequency factor (0.5 - 1.5x multiplier)
        frequency_factor = min(1.5, 0.5 + (frequency / 10.0))

        # Success rate factor (0.5 - 1.5x multiplier)
        success_factor = 0.5 + (success_rate * 1.0)

        # Age factor (0.5 - 1.5x multiplier, newer is better)
        age_factor = max(0.5, 1.5 - (age_days / 60.0))

        # Combine factors
        final_score = base_score * frequency_factor * success_factor * age_factor

        # Clamp to 1-10 range
        final_score = max(1.0, min(10.0, final_score))

        return round(final_score, 1)

    def tag_pattern(
        self,
        pattern_key: str,
        pattern_value: str,
        frequency: int = 1,
        success_rate: float = 0.5,
        age_days: int = 0,
    ) -> PatternTag:
        """
        Assign comprehensive tags to a pattern.
        
        Returns:
            PatternTag with category, improvement areas, and relevance score
        """
        # Classify pattern
        category, category_confidence = self.classify_pattern(pattern_key, pattern_value)

        # Extract improvement areas
        improvement_areas = self.extract_improvement_areas(
            pattern_key, pattern_value, category
        )

        # Calculate relevance score
        relevance_score = self.calculate_relevance_score(
            pattern_key,
            pattern_value,
            category,
            frequency=frequency,
            success_rate=success_rate,
            age_days=age_days,
        )

        # Create tag
        tag = PatternTag(
            name=f"{category.value}_{pattern_key[:20]}",
            category=category,
            confidence=category_confidence,
            improvement_areas=[area for area, _ in improvement_areas],
            relevance_score=relevance_score,
            source="auto",
        )

        return tag

    def tag_batch(
        self,
        patterns: list[dict[str, Any]],
        db_path: Optional[str] = None,
        persist: bool = True,
    ) -> TaggingMetrics:
        """
        Tag a batch of patterns.
        
        Args:
            patterns: List of pattern dicts with key, value, frequency, success_rate, age_days
            db_path: Database path for persistence
            persist: Whether to save tags to database
        
        Returns:
            TaggingMetrics with operation results
        """
        start_time = datetime.now(timezone.utc)
        operation_id = f"tag-{start_time.isoformat()}"

        tags_by_pattern = {}
        categories_count = {}
        areas_count = {}

        # Tag each pattern
        for i, pattern in enumerate(patterns):
            try:
                tag = self.tag_pattern(
                    pattern_key=pattern.get("key", f"pattern_{i}"),
                    pattern_value=pattern.get("value", ""),
                    frequency=pattern.get("frequency", 1),
                    success_rate=pattern.get("success_rate", 0.5),
                    age_days=pattern.get("age_days", 0),
                )

                tags_by_pattern[pattern.get("key", f"pattern_{i}")] = tag

                # Track category assignments
                category_name = tag.category.value
                categories_count[category_name] = categories_count.get(category_name, 0) + 1

                # Track improvement area assignments
                for area in tag.improvement_areas:
                    area_name = area.value
                    areas_count[area_name] = areas_count.get(area_name, 0) + 1

            except Exception as e:
                logger.error(f"Failed to tag pattern {pattern.get('key')}: {e}")

        # Persist to database if requested
        if persist and db_path:
            self._persist_tags(db_path, tags_by_pattern)

        # Calculate metrics
        avg_confidence = (
            sum(tag.confidence for tag in tags_by_pattern.values())
            / len(tags_by_pattern)
            if tags_by_pattern
            else 0.0
        )
        avg_relevance = (
            sum(tag.relevance_score for tag in tags_by_pattern.values())
            / len(tags_by_pattern)
            if tags_by_pattern
            else 0.0
        )

        duration_ms = (
            datetime.now(timezone.utc) - start_time
        ).total_seconds() * 1000

        metrics = TaggingMetrics(
            timestamp=start_time,
            operation_id=operation_id,
            patterns_processed=len(patterns),
            patterns_tagged=len(tags_by_pattern),
            avg_confidence=avg_confidence,
            avg_relevance_score=avg_relevance,
            duration_ms=duration_ms,
            categories_assigned=categories_count,
            improvement_areas_assigned=areas_count,
        )

        self.metrics_log.append(metrics)
        self._log_operation(metrics)

        return metrics

    def update_relevance_score(
        self,
        pattern_key: str,
        new_frequency: int,
        new_success_rate: float,
        db_path: Optional[str] = None,
    ) -> float:
        """
        Update relevance score for a pattern based on new data.
        """
        try:
            if not db_path:
                return 0.0

            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row

            # Retrieve pattern
            row = conn.execute(
                "SELECT * FROM ltm_entries WHERE key = ?", (pattern_key,)
            ).fetchone()

            if not row:
                logger.warning(f"Pattern not found: {pattern_key}")
                return 0.0

            # Recalculate relevance
            created_at = datetime.fromisoformat(row["created_at"])
            age_days = (datetime.now(timezone.utc) - created_at).days

            new_score = self.calculate_relevance_score(
                pattern_key,
                row["value"],
                PatternCategory(row["pattern_type"]),
                frequency=new_frequency,
                success_rate=new_success_rate,
                age_days=age_days,
            )

            # Update in database
            conn.execute(
                "UPDATE ltm_entries SET metadata = json_set(metadata, '$.relevance_score', ?) WHERE key = ?",
                (new_score, pattern_key),
            )
            conn.commit()
            conn.close()

            return new_score

        except Exception as e:
            logger.error(f"Failed to update relevance score: {e}")
            return 0.0

    def _persist_tags(
        self, db_path: str, tags_by_pattern: dict[str, PatternTag]
    ) -> None:
        """Persist tags to database."""
        try:
            conn = sqlite3.connect(db_path)

            for pattern_key, tag in tags_by_pattern.items():
                metadata = {
                    "tag_name": tag.name,
                    "category": tag.category.value,
                    "category_confidence": tag.confidence,
                    "improvement_areas": [area.value for area in tag.improvement_areas],
                    "relevance_score": tag.relevance_score,
                    "tagged_at": tag.created_at.isoformat(),
                }

                # Create tags array with tag name
                tags_list = [tag.category.value] + [area.value for area in tag.improvement_areas]

                conn.execute(
                    """
                    UPDATE ltm_entries 
                    SET metadata = json_set(metadata, '$', json(?)),
                        tags = json(?)
                    WHERE key = ?
                    """,
                    (json.dumps(metadata), json.dumps(tags_list), pattern_key),
                )

            conn.commit()
            conn.close()

            logger.info(f"Persisted tags for {len(tags_by_pattern)} patterns")

        except Exception as e:
            logger.error(f"Failed to persist tags: {e}", exc_info=True)

    def generate_tagging_report(self) -> dict[str, Any]:
        """Generate comprehensive tagging report."""
        if not self.metrics_log:
            return {
                "total_operations": 0,
                "total_patterns_tagged": 0,
                "avg_confidence": 0.0,
                "avg_relevance_score": 0.0,
            }

        total_tagged = sum(m.patterns_tagged for m in self.metrics_log)
        avg_confidence = (
            sum(m.avg_confidence * m.patterns_tagged for m in self.metrics_log)
            / total_tagged
            if total_tagged > 0
            else 0.0
        )
        avg_relevance = (
            sum(m.avg_relevance_score * m.patterns_tagged for m in self.metrics_log)
            / total_tagged
            if total_tagged > 0
            else 0.0
        )

        return {
            "total_operations": len(self.metrics_log),
            "total_patterns_tagged": total_tagged,
            "avg_confidence": avg_confidence,
            "avg_relevance_score": avg_relevance,
            "avg_duration_ms": sum(m.duration_ms for m in self.metrics_log)
            / len(self.metrics_log),
            "last_operation": asdict(self.metrics_log[-1]) if self.metrics_log else None,
        }

    def _log_operation(self, metrics: TaggingMetrics) -> None:
        """Log tagging operation."""
        log_entry = {
            "operation": "pattern_tagging",
            "operation_id": metrics.operation_id,
            "timestamp": metrics.timestamp.isoformat(),
            "patterns_processed": metrics.patterns_processed,
            "patterns_tagged": metrics.patterns_tagged,
            "avg_confidence": metrics.avg_confidence,
            "avg_relevance_score": metrics.avg_relevance_score,
            "duration_ms": metrics.duration_ms,
            "categories": metrics.categories_assigned,
            "improvement_areas": metrics.improvement_areas_assigned,
        }

        logger.info(f"Tagging operation: {json.dumps(log_entry)}")
