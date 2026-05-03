"""
Pattern Learning Engine

Implements advanced pattern learning capabilities:
- Semantic pattern clustering
- Pattern evolution tracking
- Anti-pattern detection
- Best practice recommendation engine

Phase 3: Pattern Learning

Author: mbaetiong
Generated: 2025-12-22
"""

from __future__ import annotations

import hashlib
import json
import logging
import math
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)


# ============================================================================
# Data Structures
# ============================================================================


@dataclass
class SemanticCluster:
    """A cluster of semantically related patterns."""

    cluster_id: str
    name: str
    centroid_features: dict[str, float]
    patterns: list[str]
    cohesion_score: float
    created_at: str
    updated_at: str


@dataclass
class PatternEvolution:
    """Tracks evolution of a pattern over time."""

    pattern_id: str
    versions: list[dict[str, Any]]
    current_version: int
    improvement_trend: float  # Positive = improving, Negative = degrading
    stability_score: float  # 0-1: How stable the pattern is


@dataclass
class AntiPattern:
    """Detected anti-pattern that should be avoided."""

    anti_pattern_id: str
    name: str
    description: str
    detection_signature: dict[str, Any]
    severity: str  # low, medium, high, critical
    remediation: str
    occurrences: int
    last_seen: str


@dataclass
class BestPractice:
    """Recommended best practice."""

    practice_id: str
    name: str
    description: str
    category: str
    confidence: float
    supporting_evidence: list[str]
    implementation_hints: list[str]
    adoption_rate: float  # 0-1


# ============================================================================
# Semantic Pattern Clustering
# ============================================================================


class SemanticPatternClusterer:
    """
    Clusters patterns based on semantic similarity.

    Uses feature extraction and K-means-like clustering
    to group related patterns together.
    """

    def __init__(self, storage_path: Optional[Path] = None):
        """Initialize semantic pattern clusterer."""
        self.storage_path = storage_path or Path(
            "data/clusters"
        )
        self.storage_path.mkdir(parents=True, exist_ok=True)

        self.clusters: dict[str, SemanticCluster] = {}
        self.pattern_features: dict[str, dict[str, float]] = {}

        self._load_clusters()

        logger.info(
            f"✅ SemanticPatternClusterer initialized | "
            f"Clusters: {len(self.clusters)}"
        )

    def _load_clusters(self) -> None:
        """Load clusters from disk."""
        clusters_file = self.storage_path / "clusters.json"
        try:
            if clusters_file.exists():
                with open(clusters_file) as f:
                    data = json.load(f)
                    for cid, cdata in data.get("clusters", {}).items():
                        self.clusters[cid] = SemanticCluster(**cdata)
                    self.pattern_features = data.get("pattern_features", {})
        except Exception as e:
            logger.warning(f"Failed to load clusters: {e}")

    def _save_clusters(self) -> None:
        """Save clusters to disk."""
        clusters_file = self.storage_path / "clusters.json"
        try:
            data = {
                "clusters": {
                    cid: {
                        "cluster_id": c.cluster_id,
                        "name": c.name,
                        "centroid_features": c.centroid_features,
                        "patterns": c.patterns,
                        "cohesion_score": c.cohesion_score,
                        "created_at": c.created_at,
                        "updated_at": c.updated_at,
                    }
                    for cid, c in self.clusters.items()
                },
                "pattern_features": self.pattern_features,
            }
            with open(clusters_file, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.warning(f"Failed to save clusters: {e}")

    def extract_features(self, pattern: dict[str, Any]) -> dict[str, float]:
        """
        Extract semantic features from a pattern.

        Args:
            pattern: Pattern dictionary

        Returns:
            Feature vector as dictionary
        """
        features: dict[str, float] = {}

        pattern_str = json.dumps(pattern, sort_keys=True).lower()

        # Domain features
        domain_keywords = {
            "security": ["security", "auth", "token", "encrypt", "validate"],
            "quantum": ["quantum", "superposition", "entangle", "coherence"],
            "testing": ["test", "assert", "mock", "fixture", "pytest"],
            "infrastructure": ["docker", "workflow", "ci", "build", "deploy"],
            "ml": ["model", "train", "predict", "neural", "embedding"],
        }

        for domain, keywords in domain_keywords.items():
            score = sum(1 for kw in keywords if kw in pattern_str)
            features[f"domain_{domain}"] = min(1.0, score / len(keywords))

        # Complexity features
        features["complexity_lines"] = min(
            1.0, pattern.get("lines", 0) / 100
        )
        features["complexity_methods"] = min(
            1.0, len(pattern.get("methods", [])) / 10
        )
        features["has_async"] = 1.0 if "async" in pattern_str else 0.0
        features["has_dataclass"] = 1.0 if "dataclass" in pattern_str else 0.0

        # Quality features
        features["has_docstring"] = (
            1.0 if '"""' in pattern_str or "'''" in pattern_str else 0.0
        )
        features["has_type_hints"] = 1.0 if "->" in pattern_str else 0.0

        return features

    def calculate_similarity(
        self, features1: dict[str, float], features2: dict[str, float]
    ) -> float:
        """
        Calculate cosine similarity between feature vectors.

        Args:
            features1: First feature vector
            features2: Second feature vector

        Returns:
            Similarity score (0-1)
        """
        all_keys = set(features1.keys()) | set(features2.keys())

        dot_product = 0.0
        norm1 = 0.0
        norm2 = 0.0

        for key in all_keys:
            v1 = features1.get(key, 0.0)
            v2 = features2.get(key, 0.0)
            dot_product += v1 * v2
            norm1 += v1 * v1
            norm2 += v2 * v2

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return dot_product / (math.sqrt(norm1) * math.sqrt(norm2))

    def cluster_patterns(
        self, patterns: list[dict[str, Any]], num_clusters: int = 5
    ) -> list[SemanticCluster]:
        """
        Cluster patterns into semantic groups.

        Args:
            patterns: List of patterns to cluster
            num_clusters: Number of clusters to create

        Returns:
            List of SemanticCluster objects
        """
        if not patterns:
            return []

        # Extract features for all patterns
        pattern_ids = []
        for i, pattern in enumerate(patterns):
            pid = hashlib.md5(
                json.dumps(pattern, sort_keys=True).encode(), usedforsecurity=False
            ).hexdigest()[:12]  # nosec B324 - Not for security, ID generation only
            pattern_ids.append(pid)
            self.pattern_features[pid] = self.extract_features(pattern)

        # Simple K-means-like clustering
        clusters: list[SemanticCluster] = []

        # Initialize cluster centroids
        step = max(1, len(pattern_ids) // num_clusters)
        centroids = [
            self.pattern_features[pattern_ids[i * step]]
            for i in range(min(num_clusters, len(pattern_ids)))
        ]

        # Assign patterns to clusters
        for _ in range(10):  # Max iterations
            cluster_assignments: dict[int, list[str]] = defaultdict(list)

            for pid in pattern_ids:
                features = self.pattern_features[pid]
                best_cluster = 0
                best_sim = -1

                for i, centroid in enumerate(centroids):
                    sim = self.calculate_similarity(features, centroid)
                    if sim > best_sim:
                        best_sim = sim
                        best_cluster = i

                cluster_assignments[best_cluster].append(pid)

            # Update centroids
            for i, pids in cluster_assignments.items():
                if not pids:
                    continue
                new_centroid: dict[str, float] = {}
                all_keys: set[str] = set()
                for pid in pids:
                    all_keys.update(self.pattern_features[pid].keys())

                for key in all_keys:
                    values = [
                        self.pattern_features[pid].get(key, 0.0) for pid in pids
                    ]
                    new_centroid[key] = sum(values) / len(values)

                if i < len(centroids):
                    centroids[i] = new_centroid

        # Create cluster objects
        now = datetime.utcnow().isoformat()
        cluster_names = [
            "security_patterns",
            "quantum_patterns",
            "testing_patterns",
            "infrastructure_patterns",
            "ml_patterns",
        ]

        for i, pids in cluster_assignments.items():
            if not pids:
                continue

            cluster_id = f"cluster_{i}"
            name = (
                cluster_names[i] if i < len(cluster_names) else f"cluster_{i}"
            )

            # Calculate cohesion
            cohesion = self._calculate_cohesion(pids)

            cluster = SemanticCluster(
                cluster_id=cluster_id,
                name=name,
                centroid_features=centroids[i] if i < len(centroids) else {},
                patterns=pids,
                cohesion_score=cohesion,
                created_at=now,
                updated_at=now,
            )

            clusters.append(cluster)
            self.clusters[cluster_id] = cluster

        self._save_clusters()

        logger.info(f"🎯 Created {len(clusters)} semantic clusters")

        return clusters

    def _calculate_cohesion(self, pattern_ids: list[str]) -> float:
        """Calculate cohesion score for a cluster."""
        if len(pattern_ids) < 2:
            return 1.0

        total_sim = 0.0
        count = 0

        for i, pid1 in enumerate(pattern_ids):
            for pid2 in pattern_ids[i + 1 :]:
                f1 = self.pattern_features.get(pid1, {})
                f2 = self.pattern_features.get(pid2, {})
                total_sim += self.calculate_similarity(f1, f2)
                count += 1

        return total_sim / count if count > 0 else 0.0

    def find_similar_patterns(
        self, pattern: dict[str, Any], top_k: int = 5
    ) -> list[tuple[str, float]]:
        """
        Find patterns similar to the given pattern.

        Args:
            pattern: Pattern to find similar patterns for
            top_k: Number of similar patterns to return

        Returns:
            List of (pattern_id, similarity) tuples
        """
        features = self.extract_features(pattern)

        similarities = []
        for pid, pf in self.pattern_features.items():
            sim = self.calculate_similarity(features, pf)
            similarities.append((pid, sim))

        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:top_k]


# ============================================================================
# Pattern Evolution Tracker
# ============================================================================


class PatternEvolutionTracker:
    """
    Tracks how patterns evolve over time.

    Monitors changes to patterns and identifies improvement
    or degradation trends.
    """

    def __init__(self, storage_path: Optional[Path] = None):
        """Initialize pattern evolution tracker."""
        self.storage_path = storage_path or Path(
            "data/evolution"
        )
        self.storage_path.mkdir(parents=True, exist_ok=True)

        self.evolutions: dict[str, PatternEvolution] = {}
        self._load_evolutions()

        logger.info(
            f"✅ PatternEvolutionTracker initialized | "
            f"Tracked patterns: {len(self.evolutions)}"
        )

    def _load_evolutions(self) -> None:
        """Load evolution data from disk."""
        evolutions_file = self.storage_path / "evolutions.json"
        try:
            if evolutions_file.exists():
                with open(evolutions_file) as f:
                    data = json.load(f)
                    for pid, pdata in data.items():
                        self.evolutions[pid] = PatternEvolution(**pdata)
        except Exception as e:
            logger.warning(f"Failed to load evolutions: {e}")

    def _save_evolutions(self) -> None:
        """Save evolution data to disk."""
        evolutions_file = self.storage_path / "evolutions.json"
        try:
            data = {
                pid: {
                    "pattern_id": e.pattern_id,
                    "versions": e.versions,
                    "current_version": e.current_version,
                    "improvement_trend": e.improvement_trend,
                    "stability_score": e.stability_score,
                }
                for pid, e in self.evolutions.items()
            }
            with open(evolutions_file, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.warning(f"Failed to save evolutions: {e}")

    def record_pattern_version(
        self,
        pattern_id: str,
        pattern_data: dict[str, Any],
        metrics: dict[str, float],
    ) -> PatternEvolution:
        """
        Record a new version of a pattern.

        Args:
            pattern_id: Pattern identifier
            pattern_data: Current pattern data
            metrics: Performance metrics for this version

        Returns:
            Updated PatternEvolution
        """
        now = datetime.utcnow().isoformat()

        version_entry = {
            "version": 1,
            "data": pattern_data,
            "metrics": metrics,
            "timestamp": now,
        }

        if pattern_id in self.evolutions:
            evolution = self.evolutions[pattern_id]
            version_entry["version"] = evolution.current_version + 1
            evolution.versions.append(version_entry)
            evolution.current_version = version_entry["version"]

            # Calculate improvement trend
            evolution.improvement_trend = self._calculate_trend(evolution.versions)
            evolution.stability_score = self._calculate_stability(evolution.versions)
        else:
            evolution = PatternEvolution(
                pattern_id=pattern_id,
                versions=[version_entry],
                current_version=1,
                improvement_trend=0.0,
                stability_score=1.0,
            )
            self.evolutions[pattern_id] = evolution

        self._save_evolutions()

        logger.info(
            f"📊 Recorded version {evolution.current_version} for {pattern_id} | "
            f"Trend: {evolution.improvement_trend:+.2f}"
        )

        return evolution

    def _calculate_trend(self, versions: list[dict[str, Any]]) -> float:
        """Calculate improvement trend from version history."""
        if len(versions) < 2:
            return 0.0

        # Compare last 5 versions' metrics
        recent = versions[-5:]
        if len(recent) < 2:
            return 0.0

        # Calculate trend from success_rate metric
        rates = [
            v.get("metrics", {}).get("success_rate", 0.5) for v in recent
        ]

        # Simple linear regression slope
        n = len(rates)
        x_mean = (n - 1) / 2
        y_mean = sum(rates) / n

        numerator = sum(
            (i - x_mean) * (rates[i] - y_mean) for i in range(n)
        )
        denominator = sum((i - x_mean) ** 2 for i in range(n))

        if denominator == 0:
            return 0.0

        return numerator / denominator

    def _calculate_stability(self, versions: list[dict[str, Any]]) -> float:
        """Calculate stability score from version variance."""
        if len(versions) < 2:
            return 1.0

        rates = [
            v.get("metrics", {}).get("success_rate", 0.5) for v in versions[-10:]
        ]

        mean = sum(rates) / len(rates)
        variance = sum((r - mean) ** 2 for r in rates) / len(rates)

        # Convert variance to stability (lower variance = higher stability)
        return max(0.0, 1.0 - math.sqrt(variance) * 2)

    def get_improving_patterns(self) -> list[PatternEvolution]:
        """Get patterns that are improving over time."""
        return [
            e
            for e in self.evolutions.values()
            if e.improvement_trend > 0.1 and e.stability_score > 0.5
        ]

    def get_degrading_patterns(self) -> list[PatternEvolution]:
        """Get patterns that are degrading over time."""
        return [
            e
            for e in self.evolutions.values()
            if e.improvement_trend < -0.1
        ]


# ============================================================================
# Anti-Pattern Detector
# ============================================================================


class AntiPatternDetector:
    """
    Detects anti-patterns that should be avoided.

    Identifies common mistakes and problematic patterns
    in code and configurations.
    """

    def __init__(self, storage_path: Optional[Path] = None):
        """Initialize anti-pattern detector."""
        self.storage_path = storage_path or Path(
            "data/antipatterns"
        )
        self.storage_path.mkdir(parents=True, exist_ok=True)

        self.anti_patterns: dict[str, AntiPattern] = {}
        self._initialize_known_antipatterns()
        self._load_antipatterns()

        logger.info(
            f"✅ AntiPatternDetector initialized | "
            f"Known anti-patterns: {len(self.anti_patterns)}"
        )

    def _initialize_known_antipatterns(self) -> None:
        """Initialize with known anti-patterns."""
        known = [
            AntiPattern(
                anti_pattern_id="ap_hardcoded_secrets",
                name="Hardcoded Secrets",
                description="Secrets or API keys hardcoded in source files",
                detection_signature={
                    "patterns": ["api_key", "secret", "password", "token"],
                    "exclude": ["test", "example", "placeholder"],
                },
                severity="critical",
                remediation="Use environment variables or secret management",
                occurrences=0,
                last_seen="",
            ),
            AntiPattern(
                anti_pattern_id="ap_mutable_default",
                name="Mutable Default Argument",
                description="Using mutable objects as default function arguments",
                detection_signature={
                    "patterns": ["def.*=\\[\\]", "def.*=\\{\\}"],
                    "context": "function_definition",
                },
                severity="medium",
                remediation="Use None as default and create mutable inside function",
                occurrences=0,
                last_seen="",
            ),
            AntiPattern(
                anti_pattern_id="ap_bare_except",
                name="Bare Except Clause",
                description="Using bare except: without specifying exception type",
                detection_signature={
                    "patterns": ["except:"],
                    "exclude": ["except Exception:", "except BaseException:"],
                },
                severity="medium",
                remediation="Catch specific exceptions instead of bare except",
                occurrences=0,
                last_seen="",
            ),
            AntiPattern(
                anti_pattern_id="ap_god_class",
                name="God Class",
                description="Class with too many methods or responsibilities",
                detection_signature={
                    "method_count_threshold": 20,
                    "lines_threshold": 500,
                },
                severity="high",
                remediation="Split into smaller, focused classes",
                occurrences=0,
                last_seen="",
            ),
            AntiPattern(
                anti_pattern_id="ap_circular_import",
                name="Circular Import",
                description="Modules importing each other circularly",
                detection_signature={
                    "patterns": ["ImportError: circular"],
                    "context": "import_error",
                },
                severity="high",
                remediation="Restructure imports or use dependency injection",
                occurrences=0,
                last_seen="",
            ),
        ]

        for ap in known:
            self.anti_patterns[ap.anti_pattern_id] = ap

    def _load_antipatterns(self) -> None:
        """Load anti-patterns from disk."""
        ap_file = self.storage_path / "antipatterns.json"
        try:
            if ap_file.exists():
                with open(ap_file) as f:
                    data = json.load(f)
                    for apid, apdata in data.items():
                        self.anti_patterns[apid] = AntiPattern(**apdata)
        except Exception as e:
            logger.warning(f"Failed to load anti-patterns: {e}")

    def _save_antipatterns(self) -> None:
        """Save anti-patterns to disk."""
        ap_file = self.storage_path / "antipatterns.json"
        try:
            data = {
                apid: {
                    "anti_pattern_id": ap.anti_pattern_id,
                    "name": ap.name,
                    "description": ap.description,
                    "detection_signature": ap.detection_signature,
                    "severity": ap.severity,
                    "remediation": ap.remediation,
                    "occurrences": ap.occurrences,
                    "last_seen": ap.last_seen,
                }
                for apid, ap in self.anti_patterns.items()
            }
            with open(ap_file, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.warning(f"Failed to save anti-patterns: {e}")

    def detect(
        self, content: str, context: Optional[dict[str, Any]] = None
    ) -> list[AntiPattern]:
        """
        Detect anti-patterns in content.

        Args:
            content: Content to analyze
            context: Optional context information

        Returns:
            List of detected AntiPattern objects
        """
        detected = []
        content_lower = content.lower()
        context = context or {}
        if context:
            logger.debug("AntiPattern detection context: %s", context)

        for ap in self.anti_patterns.values():
            signature = ap.detection_signature

            # Pattern matching
            patterns = signature.get("patterns", [])
            excludes = signature.get("exclude", [])

            matched = False
            for pattern in patterns:
                if pattern.lower() in content_lower:
                    # Check exclusions
                    if not any(ex.lower() in content_lower for ex in excludes):
                        matched = True
                        break

            # Threshold checks
            if "method_count_threshold" in signature:
                method_count = content.count("def ")
                if method_count > signature["method_count_threshold"]:
                    matched = True

            if "lines_threshold" in signature:
                lines = content.count("\n")
                if lines > signature["lines_threshold"]:
                    matched = True

            if matched:
                ap.occurrences += 1
                ap.last_seen = datetime.utcnow().isoformat()
                detected.append(ap)

        if detected:
            self._save_antipatterns()
            logger.warning(
                f"⚠️ Detected {len(detected)} anti-patterns: "
                f"{[ap.name for ap in detected]}"
            )

        return detected

    def get_statistics(self) -> dict[str, Any]:
        """Get anti-pattern detection statistics."""
        return {
            "total_antipatterns": len(self.anti_patterns),
            "by_severity": {
                severity: len(
                    [ap for ap in self.anti_patterns.values() if ap.severity == severity]
                )
                for severity in ["low", "medium", "high", "critical"]
            },
            "most_common": sorted(
                [
                    (ap.name, ap.occurrences)
                    for ap in self.anti_patterns.values()
                    if ap.occurrences > 0
                ],
                key=lambda x: x[1],
                reverse=True,
            )[:5],
        }


# ============================================================================
# Best Practice Recommendation Engine
# ============================================================================


class BestPracticeRecommender:
    """
    Recommends best practices based on observed patterns.

    Analyzes successful patterns and generates actionable
    recommendations for improvement.
    """

    def __init__(self, storage_path: Optional[Path] = None):
        """Initialize best practice recommender."""
        self.storage_path = storage_path or Path(
            "data/best_practices"
        )
        self.storage_path.mkdir(parents=True, exist_ok=True)

        self.best_practices: dict[str, BestPractice] = {}
        self._initialize_practices()
        self._load_practices()

        logger.info(
            f"✅ BestPracticeRecommender initialized | "
            f"Practices: {len(self.best_practices)}"
        )

    def _initialize_practices(self) -> None:
        """Initialize with known best practices."""
        practices = [
            BestPractice(
                practice_id="bp_type_hints",
                name="Use Type Hints",
                description="Add type hints to function signatures and variables",
                category="code_quality",
                confidence=0.95,
                supporting_evidence=["Improves IDE support", "Catches bugs early"],
                implementation_hints=[
                    "Add return type: def func() -> ReturnType:",
                    "Add param types: def func(param: ParamType):",
                    "Use typing module for complex types",
                ],
                adoption_rate=0.0,
            ),
            BestPractice(
                practice_id="bp_docstrings",
                name="Comprehensive Docstrings",
                description="Add docstrings to all public functions and classes",
                category="documentation",
                confidence=0.92,
                supporting_evidence=["Improves maintainability", "Enables auto-docs"],
                implementation_hints=[
                    'Use triple quotes: """Description"""',
                    "Include Args, Returns, Raises sections",
                    "Add examples when helpful",
                ],
                adoption_rate=0.0,
            ),
            BestPractice(
                practice_id="bp_dataclasses",
                name="Use Dataclasses for Data",
                description="Use @dataclass for simple data containers",
                category="code_structure",
                confidence=0.88,
                supporting_evidence=["Reduces boilerplate", "Auto-generates methods"],
                implementation_hints=[
                    "from dataclasses import dataclass",
                    "@dataclass decorator above class",
                    "Use field() for default mutable values",
                ],
                adoption_rate=0.0,
            ),
            BestPractice(
                practice_id="bp_async_await",
                name="Async/Await for I/O",
                description="Use async/await for I/O-bound operations",
                category="performance",
                confidence=0.85,
                supporting_evidence=["Improves concurrency", "Better resource usage"],
                implementation_hints=[
                    "async def for async functions",
                    "await for async calls",
                    "Use asyncio for orchestration",
                ],
                adoption_rate=0.0,
            ),
            BestPractice(
                practice_id="bp_error_handling",
                name="Specific Exception Handling",
                description="Catch specific exceptions, not bare except",
                category="error_handling",
                confidence=0.95,
                supporting_evidence=["Prevents hiding bugs", "Better error messages"],
                implementation_hints=[
                    "except SpecificError as e:",
                    "Log the error details",
                    "Re-raise if can't handle",
                ],
                adoption_rate=0.0,
            ),
        ]

        for bp in practices:
            self.best_practices[bp.practice_id] = bp

    def _load_practices(self) -> None:
        """Load practices from disk."""
        bp_file = self.storage_path / "practices.json"
        try:
            if bp_file.exists():
                with open(bp_file) as f:
                    data = json.load(f)
                    for bpid, bpdata in data.items():
                        self.best_practices[bpid] = BestPractice(**bpdata)
        except Exception as e:
            logger.warning(f"Failed to load practices: {e}")

    def _save_practices(self) -> None:
        """Save practices to disk."""
        bp_file = self.storage_path / "practices.json"
        try:
            data = {
                bpid: {
                    "practice_id": bp.practice_id,
                    "name": bp.name,
                    "description": bp.description,
                    "category": bp.category,
                    "confidence": bp.confidence,
                    "supporting_evidence": bp.supporting_evidence,
                    "implementation_hints": bp.implementation_hints,
                    "adoption_rate": bp.adoption_rate,
                }
                for bpid, bp in self.best_practices.items()
            }
            with open(bp_file, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.warning(f"Failed to save practices: {e}")

    def recommend(
        self,
        content: str,
        context: Optional[dict[str, Any]] = None,
        top_k: int = 3,
    ) -> list[BestPractice]:
        """
        Recommend best practices for the given content.

        Args:
            content: Content to analyze
            context: Optional context information
            top_k: Number of recommendations to return

        Returns:
            List of recommended BestPractice objects
        """
        recommendations = []
        content_lower = content.lower()

        for bp in self.best_practices.values():
            # Check if practice is already adopted
            adopted = self._check_adoption(bp, content_lower)

            if not adopted:
                # Calculate relevance score
                relevance = self._calculate_relevance(bp, content_lower, context)
                if relevance > 0.3:
                    recommendations.append((bp, relevance))

        # Sort by relevance and confidence
        recommendations.sort(
            key=lambda x: x[1] * x[0].confidence, reverse=True
        )

        return [bp for bp, _ in recommendations[:top_k]]

    def _check_adoption(self, practice: BestPractice, content: str) -> bool:
        """Check if a practice is already adopted."""
        checks = {
            "bp_type_hints": "->" in content,
            "bp_docstrings": '"""' in content or "'''" in content,
            "bp_dataclasses": "@dataclass" in content,
            "bp_async_await": "async def" in content,
            "bp_error_handling": "except " in content and "except:" not in content,
        }

        return checks.get(practice.practice_id, False)

    def _calculate_relevance(
        self,
        practice: BestPractice,
        content: str,
        context: Optional[dict[str, Any]],
    ) -> float:
        """Calculate relevance of a practice for the content."""
        relevance = 0.5  # Base relevance

        # Category-based relevance
        category_keywords = {
            "code_quality": ["def ", "class ", "import "],
            "documentation": ["def ", "class "],
            "code_structure": ["class ", "dataclass"],
            "performance": ["async", "await", "io", "network"],
            "error_handling": ["try:", "except", "raise"],
        }

        keywords = category_keywords.get(practice.category, [])
        for kw in keywords:
            if kw.lower() in content:
                relevance += 0.1

        return min(1.0, relevance)

    def record_adoption(self, practice_id: str) -> None:
        """Record that a practice was adopted."""
        if practice_id in self.best_practices:
            bp = self.best_practices[practice_id]
            # Update adoption rate with exponential moving average
            bp.adoption_rate = 0.1 + 0.9 * bp.adoption_rate
            self._save_practices()

            logger.info(f"📈 Recorded adoption of {bp.name}: {bp.adoption_rate:.1%}")

    def get_statistics(self) -> dict[str, Any]:
        """Get best practice statistics."""
        return {
            "total_practices": len(self.best_practices),
            "by_category": {
                cat: len(
                    [bp for bp in self.best_practices.values() if bp.category == cat]
                )
                for cat in set(bp.category for bp in self.best_practices.values())
            },
            "avg_confidence": sum(
                bp.confidence for bp in self.best_practices.values()
            )
            / len(self.best_practices)
            if self.best_practices
            else 0.0,
            "avg_adoption": sum(
                bp.adoption_rate for bp in self.best_practices.values()
            )
            / len(self.best_practices)
            if self.best_practices
            else 0.0,
        }
