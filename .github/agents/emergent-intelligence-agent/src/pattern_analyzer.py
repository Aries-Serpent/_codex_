"""
Emergent Intelligence Agent - V10 Custom Agent

Specialized emergent behavior analysis across repositories:
- Cross-repository pattern detection
- Code smell emergence tracking
- Behavior prediction
- Self-improving pattern recognition
- Real-time pattern notifications

Integration Points:
- phase8_9_emergent_behavior.py::EmergentPatternDetector
- phase8_9_emergent_behavior.py::SelfImprovementEngine
- phase8_10_production_deployment.py::MonitoringObservability
"""
import hashlib
import random
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional

# Try imports from cognitive brain core
try:
    import os
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'core'))
    from phase8_9_emergent_behavior import (
        EmergentPatternDetector,
        SelfImprovementEngine,
    )
    CORE_AVAILABLE = True
except ImportError:
    CORE_AVAILABLE = False
    EmergentPatternDetector = None
    SelfImprovementEngine = None
    PatternType = None


# =============================================================================
# CONSTANTS
# =============================================================================

RANDOM_SEED = 46  # V10 agent seed
PATTERN_ACCURACY_TARGET = 0.95
DETECTION_LATENCY_TARGET_MS = 500
MAX_PATTERNS_PER_REPO = 100
NOTIFICATION_COOLDOWN_SECONDS = 300  # 5 minutes


# =============================================================================
# DATA STRUCTURES
# =============================================================================

class EmergenceType(Enum):
    """Types of emergent behavior."""
    CODE_SMELL = "code_smell"
    TEST_FAILURE_PATTERN = "test_failure_pattern"
    PERFORMANCE_DEGRADATION = "performance_degradation"
    SECURITY_VULNERABILITY = "security_vulnerability"
    DESIGN_PATTERN = "design_pattern"


@dataclass
class EmergentPattern:
    """Detected emergent pattern.

    Attributes:
        pattern_id: Unique pattern identifier
        emergence_type: Type of emergent behavior
        repositories: Affected repositories
        confidence: Detection confidence (0-1)
        first_seen: First detection timestamp
        last_seen: Last detection timestamp
        occurrences: Number of occurrences
        metadata: Additional pattern metadata
    """
    pattern_id: str
    emergence_type: EmergenceType
    repositories: list[str]
    confidence: float
    first_seen: datetime
    last_seen: datetime
    occurrences: int = 1
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class BehaviorPrediction:
    """Predicted system behavior.

    Attributes:
        prediction_id: Unique prediction identifier
        predicted_behavior: Description of predicted behavior
        probability: Prediction probability (0-1)
        time_horizon: Prediction time horizon
        confidence: Prediction confidence (0-1)
        factors: Contributing factors
    """
    prediction_id: str
    predicted_behavior: str
    probability: float
    time_horizon: str
    confidence: float
    factors: list[str]


# =============================================================================
# EMERGENT INTELLIGENCE AGENT
# =============================================================================

class EmergentIntelligenceAgent:
    """Emergent Intelligence Agent for cross-repository pattern analysis.

    Capabilities:
    1. Cross-repository pattern detection
    2. Code smell emergence tracking
    3. Behavior prediction
    4. Self-improving pattern recognition
    5. Real-time pattern notifications

    Example:
        agent = EmergentIntelligenceAgent(seed=46)
        agent.initialize()

        # Detect patterns across repos
        patterns = agent.detect_cross_repo_patterns(repos)

        # Predict behavior
        predictions = agent.predict_behavior(context)

        # Get metrics
        metrics = agent.get_metrics()
    """

    def __init__(self, seed: int = RANDOM_SEED):
        """Initialize emergent intelligence agent.

        Args:
            seed: Random seed for deterministic behavior
        """
        self.seed = seed
        self._rng = random.Random(seed)

        # Core components
        self.pattern_detector: Optional[Any] = None
        self.improvement_engine: Optional[Any] = None

        # State tracking
        self.detected_patterns: dict[str, EmergentPattern] = {}
        self.pattern_history: list[EmergentPattern] = []
        self.predictions: list[BehaviorPrediction] = []
        self.last_notification: dict[str, float] = {}

        # PDA Loop state
        self.pda_state = {
            "perception": None,
            "decision": None,
            "action": None,
            "aftermath": []
        }

        # Metrics
        self.metrics = {
            "patterns_detected": 0,
            "predictions_made": 0,
            "accuracy": 0.0,
            "avg_latency_ms": 0.0,
            "notifications_sent": 0
        }

        self.initialized = False

    def initialize(self) -> bool:
        """Initialize the agent with core components.

        Returns:
            True if initialization successful
        """
        if not CORE_AVAILABLE:
            self.initialized = False
            return False

        try:
            # Initialize pattern detector
            self.pattern_detector = EmergentPatternDetector()

            # Initialize improvement engine
            self.improvement_engine = SelfImprovementEngine()

            self.initialized = True
            return True
        except Exception:
            self.initialized = False
            return False

    def detect_cross_repo_patterns(
        self,
        repositories: list[str],
        context: Optional[dict[str, Any]] = None
    ) -> list[EmergentPattern]:
        """Detect patterns across multiple repositories.

        Args:
            repositories: List of repository identifiers
            context: Optional context information

        Returns:
            List of detected emergent patterns
        """
        start_time = time.time()

        # Perception phase
        self.pda_state["perception"] = {
            "repositories": repositories,
            "context": context,
            "timestamp": datetime.now()
        }

        patterns = []

        if not self.initialized or not self.pattern_detector:
            # Fallback: simple pattern detection
            patterns = self._fallback_pattern_detection(repositories, context)
        else:
            # Use core pattern detector
            patterns = self._detect_with_core(repositories, context)

        # Update state
        for pattern in patterns:
            self.detected_patterns[pattern.pattern_id] = pattern
            self.pattern_history.append(pattern)

        # Update metrics
        self.metrics["patterns_detected"] += len(patterns)
        latency_ms = (time.time() - start_time) * 1000
        self._update_latency(latency_ms)

        # Decision phase
        self.pda_state["decision"] = {
            "patterns_found": len(patterns),
            "high_confidence": [p for p in patterns if p.confidence > 0.9]
        }

        # Action phase
        self.pda_state["action"] = patterns

        return patterns

    def track_code_smells(
        self,
        repository: str,
        code_changes: list[dict[str, Any]]
    ) -> list[EmergentPattern]:
        """Track emerging code smells in repository.

        Args:
            repository: Repository identifier
            code_changes: List of code changes to analyze

        Returns:
            List of detected code smell patterns
        """
        patterns = []

        for change in code_changes:
            # Analyze change for code smells
            smells = self._analyze_code_smells(change)

            for smell in smells:
                pattern_id = self._generate_pattern_id(repository, smell)

                if pattern_id in self.detected_patterns:
                    # Update existing pattern
                    pattern = self.detected_patterns[pattern_id]
                    pattern.occurrences += 1
                    pattern.last_seen = datetime.now()
                else:
                    # Create new pattern
                    pattern = EmergentPattern(
                        pattern_id=pattern_id,
                        emergence_type=EmergenceType.CODE_SMELL,
                        repositories=[repository],
                        confidence=0.85,  # Base confidence
                        first_seen=datetime.now(),
                        last_seen=datetime.now(),
                        metadata={"smell_type": smell}
                    )
                    self.detected_patterns[pattern_id] = pattern

                patterns.append(pattern)

        return patterns

    def predict_behavior(
        self,
        context: dict[str, Any]
    ) -> list[BehaviorPrediction]:
        """Predict system behavior based on historical patterns.

        Args:
            context: Context information for prediction

        Returns:
            List of behavior predictions
        """
        predictions = []

        # Analyze historical patterns
        if len(self.pattern_history) >= 3:
            # Use historical data for prediction
            predictions = self._predict_from_history(context)
        else:
            # Insufficient data, make conservative predictions
            predictions = self._conservative_predictions(context)

        self.predictions.extend(predictions)
        self.metrics["predictions_made"] += len(predictions)

        return predictions

    def send_notification(
        self,
        pattern: EmergentPattern,
        recipients: list[str]
    ) -> bool:
        """Send real-time notification about detected pattern.

        Args:
            pattern: Pattern to notify about
            recipients: List of notification recipients

        Returns:
            True if notification sent successfully
        """
        _ = recipients
        # Check cooldown
        now = time.time()
        last_notif = self.last_notification.get(pattern.pattern_id, 0)

        if now - last_notif < NOTIFICATION_COOLDOWN_SECONDS:
            return False  # Still in cooldown

        # Send notification (placeholder - would integrate with actual system)
        self.last_notification[pattern.pattern_id] = now
        self.metrics["notifications_sent"] += 1

        return True

    def improve_accuracy(self, feedback: dict[str, Any]) -> None:
        """Improve pattern recognition accuracy based on feedback.

        Args:
            feedback: Feedback on pattern detection accuracy
        """
        # AfterMath phase - learn from feedback
        self.pda_state["aftermath"].append({
            "timestamp": datetime.now(),
            "feedback": feedback
        })

        if self.improvement_engine and self.initialized:
            # Use core improvement engine
            self.improvement_engine.apply_improvement(
                component="pattern_detection",
                improvement_data=feedback
            )

        # Update accuracy metric
        if "accuracy" in feedback:
            current_acc = self.metrics["accuracy"]
            new_acc = feedback["accuracy"]
            # Exponential moving average
            self.metrics["accuracy"] = 0.9 * current_acc + 0.1 * new_acc

    def get_metrics(self) -> dict[str, Any]:
        """Get agent metrics.

        Returns:
            Dictionary of agent metrics
        """
        return {
            **self.metrics,
            "total_patterns": len(self.detected_patterns),
            "unique_patterns": len(set(p.pattern_id for p in self.pattern_history)),
            "avg_confidence": self._calculate_avg_confidence(),
            "perceptions": 1 if self.pda_state.get("perception") else 0,
            "decisions": 1 if self.pda_state.get("decision") else 0,
            "actions": 1 if self.pda_state.get("action") else 0,
            "learnings": len(self.pda_state["aftermath"])
        }

    # =========================================================================
    # PRIVATE METHODS
    # =========================================================================

    def _fallback_pattern_detection(
        self,
        repositories: list[str],
        context: Optional[dict[str, Any]]
    ) -> list[EmergentPattern]:
        """Fallback pattern detection when core not available.

        Args:
            repositories: List of repositories
            context: Optional context

        Returns:
            List of detected patterns
        """
        patterns = []

        # Simple heuristic-based detection
        for repo in repositories:
            pattern_id = f"pattern_{hashlib.md5(repo.encode(), usedforsecurity=False).hexdigest()[:8]}"  # nosec B324 - Not for security, pattern ID generation only
            pattern = EmergentPattern(
                pattern_id=pattern_id,
                emergence_type=EmergenceType.DESIGN_PATTERN,
                repositories=[repo],
                confidence=0.75,
                first_seen=datetime.now(),
                last_seen=datetime.now()
            )
            patterns.append(pattern)

        return patterns

    def _detect_with_core(
        self,
        repositories: list[str],
        context: Optional[dict[str, Any]]
    ) -> list[EmergentPattern]:
        """Detect patterns using core components.

        Args:
            repositories: List of repositories
            context: Optional context

        Returns:
            List of detected patterns
        """
        # This would use the actual EmergentPatternDetector
        # For now, return empty list as placeholder
        return []

    def _analyze_code_smells(self, change: dict[str, Any]) -> list[str]:
        """Analyze code change for smells.

        Args:
            change: Code change information

        Returns:
            List of detected smell types
        """
        smells = []

        # Simple heuristics
        if "code" in change:
            code = change["code"]
            # Long method detection
            if len(code.split('\n')) > 50:
                smells.append("long_method")
            # Nested complexity
            if code.count("    ") > 20:  # 5+ indentation levels
                smells.append("deep_nesting")

        return smells

    def _generate_pattern_id(self, repository: str, smell: str) -> str:
        """Generate unique pattern ID.

        Args:
            repository: Repository identifier
            smell: Smell type

        Returns:
            Unique pattern ID
        """
        combined = f"{repository}:{smell}"
        return hashlib.sha256(combined.encode()).hexdigest()[:16]

    def _predict_from_history(
        self,
        context: dict[str, Any]
    ) -> list[BehaviorPrediction]:
        """Make predictions from historical patterns.

        Args:
            context: Context information

        Returns:
            List of predictions
        """
        predictions = []

        # Analyze pattern trends
        recent_patterns = self.pattern_history[-10:]

        if len(recent_patterns) >= 3:
            # Predict continuation of trend
            prediction = BehaviorPrediction(
                prediction_id=f"pred_{len(self.predictions)}",
                predicted_behavior="pattern_continuation",
                probability=0.75,
                time_horizon="1_week",
                confidence=0.80,
                factors=["historical_trend", "pattern_frequency"]
            )
            predictions.append(prediction)

        return predictions

    def _conservative_predictions(
        self,
        context: dict[str, Any]
    ) -> list[BehaviorPrediction]:
        """Make conservative predictions with insufficient data.

        Args:
            context: Context information

        Returns:
            List of conservative predictions
        """
        predictions = []

        # Make low-confidence prediction
        prediction = BehaviorPrediction(
            prediction_id=f"pred_{len(self.predictions)}",
            predicted_behavior="stable_state",
            probability=0.60,
            time_horizon="3_days",
            confidence=0.50,
            factors=["insufficient_data"]
        )
        predictions.append(prediction)

        return predictions

    def _update_latency(self, latency_ms: float) -> None:
        """Update average latency metric.

        Args:
            latency_ms: Latest latency measurement
        """
        current_avg = self.metrics["avg_latency_ms"]
        # Exponential moving average
        self.metrics["avg_latency_ms"] = 0.9 * current_avg + 0.1 * latency_ms

    def _calculate_avg_confidence(self) -> float:
        """Calculate average pattern confidence.

        Returns:
            Average confidence across all patterns
        """
        if not self.detected_patterns:
            return 0.0

        total_confidence = sum(p.confidence for p in self.detected_patterns.values())
        return total_confidence / len(self.detected_patterns)


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def create_agent(seed: int = RANDOM_SEED) -> EmergentIntelligenceAgent:
    """Create and initialize emergent intelligence agent.

    Args:
        seed: Random seed

    Returns:
        Initialized agent instance
    """
    agent = EmergentIntelligenceAgent(seed=seed)
    agent.initialize()
    return agent
