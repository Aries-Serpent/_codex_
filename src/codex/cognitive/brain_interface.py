#!/usr/bin/env python3
"""
Agent Brain Interface Module

This module provides the standard interface for agent-brain communication,
enabling all 55 agents to integrate with the cognitive brain infrastructure.

The AgentBrainInterface provides:
1. Pattern store access - Query and submit learned patterns
2. Objective alignment check - Verify agent actions align with goals
3. Session state sharing - Read and update session state
4. Learning feedback submission - Report outcomes for continuous learning

Usage:
    from codex.cognitive.brain_interface import AgentBrainInterface

    # Initialize with agent ID
    brain = AgentBrainInterface(agent_id="ci-testing-agent")

    # Query patterns
    patterns = brain.query_patterns("pytest collection error")

    # Report learning
    brain.submit_learning(
        pattern_id="TFR-001",
        outcome="success",
        context={"issue": "import error", "resolution": "added mock"}
    )

See Also:
    .codex/docs/AGENT_BRAIN_PROTOCOL.md - Full protocol specification
    .github/agents/AGENT_CHAINING_GUIDE.md - Agent orchestration patterns
"""

from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Optional

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Minimum match score for PatternConfidence.LOW results.
# Override via COGNITIVE_BRAIN_PATTERN_MIN_CONFIDENCE env variable (float, 0–1).
_raw_min_conf = os.environ.get("COGNITIVE_BRAIN_PATTERN_MIN_CONFIDENCE", "0.0")
try:
    _MIN_CONFIDENCE: float = float(_raw_min_conf)
except ValueError:
    raise ValueError(
        f"COGNITIVE_BRAIN_PATTERN_MIN_CONFIDENCE must be a float between 0 and 1, "
        f"got: {_raw_min_conf!r}"
    ) from None


class AgentCategory(Enum):
    """Categories of agents in the ecosystem."""

    CI_CD = "ci_cd"
    TESTING = "testing"
    SECURITY = "security"
    DOCUMENTATION = "documentation"
    RAG_ML = "rag_ml"
    REPOSITORY = "repository"
    CONFIG = "config"
    SESSION = "session"
    UNKNOWN = "unknown"


class ObjectiveAlignment(Enum):
    """Alignment status between agent action and objectives."""

    ALIGNED = "aligned"
    PARTIALLY_ALIGNED = "partially_aligned"
    MISALIGNED = "misaligned"
    UNKNOWN = "unknown"


class PatternConfidence(Enum):
    """Confidence levels for pattern matches."""

    HIGH = "high"  # >= 85% match
    MEDIUM = "medium"  # 60-84% match
    LOW = "low"  # < 60% match


@dataclass
class AgentContext:
    """
    Context information provided by an agent when querying the brain.

    Attributes:
        agent_id: Unique identifier for the agent
        agent_category: Category of the agent (CI_CD, TESTING, etc.)
        session_id: Current session identifier
        pr_number: Associated PR number (if any)
        symptoms: List of symptoms or issues being diagnosed
        current_phase: Current phase of agent operation
        metadata: Additional context-specific metadata
    """

    agent_id: str
    agent_category: AgentCategory = AgentCategory.UNKNOWN
    session_id: Optional[str] = None
    pr_number: Optional[int] = None
    symptoms: list[str] = field(default_factory=list)
    current_phase: str = "initial"
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class PatternMatch:
    """
    A matched pattern from the pattern store.

    Attributes:
        pattern_id: Unique identifier for the pattern
        category: Pattern category (testing, ci_cd, security, etc.)
        confidence: Confidence level of the match
        match_score: Numeric match score (0.0 to 1.0)
        symptoms: Matched symptoms
        solutions: Recommended solutions
        success_rate: Historical success rate
        times_applied: Number of times this pattern has been applied
        related_prs: List of related PR numbers
    """

    pattern_id: str
    category: str
    confidence: PatternConfidence
    match_score: float
    symptoms: list[str]
    solutions: list[str]
    success_rate: float
    times_applied: int
    related_prs: list[str] = field(default_factory=list)
    diagnosis_steps: list[str] = field(default_factory=list)


@dataclass
class LearningFeedback:
    """
    Feedback submitted by an agent after applying a pattern.

    Attributes:
        pattern_id: ID of the pattern that was applied
        outcome: Result of applying the pattern (success/failure/partial)
        agent_id: ID of the agent submitting feedback
        context: Context in which the pattern was applied
        resolution_details: Details about how the issue was resolved
        new_symptoms: Any new symptoms discovered
        suggested_improvements: Suggestions for improving the pattern
    """

    pattern_id: str
    outcome: str  # "success", "failure", "partial"
    agent_id: str
    context: dict[str, Any] = field(default_factory=dict)
    resolution_details: str = ""
    new_symptoms: list[str] = field(default_factory=list)
    suggested_improvements: list[str] = field(default_factory=list)


@dataclass
class BrainResponse:
    """
    Response from the cognitive brain to an agent query.

    Attributes:
        success: Whether the query was successful
        message: Human-readable response message
        patterns: List of matched patterns
        objectives: Current objectives relevant to the query
        session_state: Current session state snapshot
        recommendations: Brain's recommendations for next actions
        metadata: Additional response metadata
    """

    success: bool
    message: str
    patterns: list[PatternMatch] = field(default_factory=list)
    objectives: list[str] = field(default_factory=list)
    session_state: dict[str, Any] = field(default_factory=dict)
    recommendations: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


class AgentBrainInterface:
    """
    Standard interface for agent-brain communication.

    This interface provides the core API for all agents to interact with
    the cognitive brain infrastructure, enabling:

    1. Pattern Store Access
       - Query patterns based on symptoms
       - Submit new patterns learned during operation
       - Update pattern success rates

    2. Objective Alignment
       - Check if proposed actions align with objectives
       - Get current objectives for context
       - Update objective progress

    3. Session State
       - Read current session state
       - Update session state with progress
       - Share state across agent switches

    4. Learning Feedback
       - Submit outcomes for pattern application
       - Report new discoveries
       - Contribute to continuous improvement

    Architecture:
        ┌─────────────────────────────────────────────────────────────┐
        │                    Cognitive Brain Hub                       │
        ├─────────────────────────────────────────────────────────────┤
        │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
        │  │ Pattern  │  │Objective │  │ Session  │  │ Learning │   │
        │  │  Store   │  │ Tracker  │  │ Manager  │  │ Pipeline │   │
        │  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘   │
        │       │              │              │              │        │
        │       └──────────────┼──────────────┼──────────────┘        │
        │                      │              │                        │
        │              ┌───────┴──────────────┴───────┐               │
        │              │    AgentBrainInterface       │               │
        │              └───────────────┬──────────────┘               │
        └──────────────────────────────┼──────────────────────────────┘
                                       │
                ┌──────────────────────┼──────────────────────┐
                │                      │                      │
           ┌────┴────┐           ┌─────┴─────┐          ┌────┴────┐
           │ CI/CD   │           │  Testing  │          │ Security│
           │ Agents  │           │  Agents   │          │ Agents  │
           └─────────┘           └───────────┘          └─────────┘

    Example:
        >>> from codex.cognitive.brain_interface import AgentBrainInterface
        >>>
        >>> # Initialize interface for an agent
        >>> brain = AgentBrainInterface(agent_id="ci-testing-agent")
        >>>
        >>> # Query patterns for a symptom
        >>> patterns = brain.query_patterns("pytest collection error")
        >>> for pattern in patterns:
        ...     logger.info(f"{pattern.pattern_id}: {pattern.solutions[0]}")
        >>>
        >>> # Check objective alignment
        >>> aligned = brain.check_alignment("run additional tests")
        >>>
        >>> # Submit learning feedback
        >>> brain.submit_learning(
        ...     pattern_id="TFR-001",
        ...     outcome="success",
        ...     context={"error": "import error", "fix": "added mock"}
        ... )
    """

    # Default paths (relative to repo root)
    DEFAULT_COGNITIVE_BRAIN_DIR = ".codex/cognitive_brain"
    DEFAULT_PATTERN_STORE = "pattern_learning_store.json"
    DEFAULT_SESSION_TRACKER = "session_tracker.md"
    DEFAULT_OBJECTIVES_TRACKER = "objectives_tracker.md"

    # Agent category mappings
    AGENT_CATEGORY_MAP: dict[str, AgentCategory] = {
        "ci-testing-agent": AgentCategory.CI_CD,
        "ci-log-retrieval-agent": AgentCategory.CI_CD,
        "workflow-ci-fixer": AgentCategory.CI_CD,
        "artifact-monitor-agent": AgentCategory.CI_CD,
        "ci-emergency-response-agent": AgentCategory.CI_CD,
        "coverage-roadmap-agent": AgentCategory.TESTING,
        "test-alignment-fixer": AgentCategory.TESTING,
        "test-coverage-monitor": AgentCategory.TESTING,
        "qa-walkthrough-agent": AgentCategory.TESTING,
        "security-alert-verification-agent": AgentCategory.SECURITY,
        "codeql-alert-resolution-agent": AgentCategory.SECURITY,
        "security-audit-agent": AgentCategory.SECURITY,
        "documentation-consolidator": AgentCategory.DOCUMENTATION,
        "link-validator-agent": AgentCategory.DOCUMENTATION,
        "doc-freshness-checker": AgentCategory.DOCUMENTATION,
        "rag-index-manager": AgentCategory.RAG_ML,
        "meta-tensor-validator": AgentCategory.RAG_ML,
        "repository-hygiene-agent": AgentCategory.REPOSITORY,
        "root-organizer-agent": AgentCategory.REPOSITORY,
        "reference-updater-agent": AgentCategory.REPOSITORY,
        "config-validator": AgentCategory.CONFIG,
        "session-analysis-agent": AgentCategory.SESSION,
        "session-log-retrieval-agent": AgentCategory.SESSION,
    }

    def __init__(
        self,
        agent_id: str,
        repo_root: Optional[str | Path] = None,
        auto_register: bool = True,
    ):
        """
        Initialize the Agent Brain Interface.

        Args:
            agent_id: Unique identifier for the agent using this interface
            repo_root: Root directory of the repository (defaults to cwd)
            auto_register: Automatically register the agent with the brain
        """
        self.agent_id = agent_id
        self.agent_category = self.AGENT_CATEGORY_MAP.get(agent_id, AgentCategory.UNKNOWN)
        self.repo_root = Path(repo_root) if repo_root else Path.cwd()

        # Set up paths
        self.cognitive_brain_dir = self.repo_root / self.DEFAULT_COGNITIVE_BRAIN_DIR
        self.pattern_store_path = self.cognitive_brain_dir / self.DEFAULT_PATTERN_STORE
        self.session_tracker_path = self.cognitive_brain_dir / self.DEFAULT_SESSION_TRACKER
        self.objectives_path = self.cognitive_brain_dir / self.DEFAULT_OBJECTIVES_TRACKER

        # Internal state
        self._patterns: dict[str, dict[str, Any]] = {}
        self._session_state: dict[str, Any] = {}
        self._objectives: list[str] = []
        self._registered = False

        # Load data
        self._load_patterns()
        self._load_session_state()
        self._load_objectives()

        if auto_register:
            self._register_agent()

        logger.info(f"AgentBrainInterface initialized for {agent_id}")

    def _load_patterns(self) -> None:
        """Load patterns from the pattern store."""
        if self.pattern_store_path.exists():
            try:
                with open(self.pattern_store_path, encoding="utf-8") as f:
                    data = json.load(f)
                    self._patterns = data.get("patterns", {})
                    logger.debug(f"Loaded {len(self._patterns)} patterns")
            except (OSError, json.JSONDecodeError) as e:
                type(e).__name__
                logger.warning("Failed to load patterns: <ERROR_TYPE>")
                self._patterns = {}
        else:
            logger.debug("Pattern store not found, starting with empty patterns")
            self._patterns = {}

    def _load_session_state(self) -> None:
        """Load current session state."""
        if self.session_tracker_path.exists():
            try:
                content = self.session_tracker_path.read_text(encoding="utf-8")
                # Parse basic state from markdown
                self._session_state = {
                    "loaded": True,
                    "path": str(self.session_tracker_path),
                    "content_length": len(content),
                }

                # Extract key values from markdown
                for line in content.split("\n"):
                    if line.startswith("**Session ID:**"):
                        self._session_state["session_id"] = line.split("**")[-1].strip()
                    elif line.startswith("**Status:**"):
                        self._session_state["status"] = line.split("**")[-1].strip()
                    elif line.startswith("**Phase:**"):
                        self._session_state["phase"] = line.split("**")[-1].strip()

            except OSError as e:
                type(e).__name__
                logger.warning("Failed to load session state: <ERROR_TYPE>")
                self._session_state = {}
        else:
            self._session_state = {}

    def _load_objectives(self) -> None:
        """Load current objectives."""
        if self.objectives_path.exists():
            try:
                content = self.objectives_path.read_text(encoding="utf-8")
                self._objectives = []

                # Parse objectives from markdown
                # Note: Substring checks below are for markdown heading detection,
                # not for URL/domain validation. This is safe markdown parsing.
                in_objectives = False
                for line in content.split("\n"):
                    if (
                        "## Current Objectives" in line or "### Primary" in line
                    ):  # nosec - markdown heading
                        in_objectives = True
                        continue
                    if in_objectives and line.startswith("- [ ]"):
                        objective = line.replace("- [ ]", "").strip()
                        self._objectives.append(objective)
                    elif in_objectives and line.startswith("- [x]"):
                        # Skip completed objectives
                        pass
                    elif in_objectives and line.startswith("#"):
                        in_objectives = False

            except OSError as e:
                type(e).__name__
                logger.warning("Failed to load objectives: <ERROR_TYPE>")
                self._objectives = []
        else:
            self._objectives = []

    def _register_agent(self) -> None:
        """Register the agent with the cognitive brain."""
        self._registered = True
        logger.debug(f"Agent {self.agent_id} registered with cognitive brain")

    def _calculate_match_score(self, symptoms: list[str], pattern_symptoms: list[str]) -> float:
        """
        Calculate match score between query symptoms and pattern symptoms.

        Uses a combination of exact matching and fuzzy keyword matching.

        Args:
            symptoms: List of symptoms from the query
            pattern_symptoms: List of symptoms in the pattern

        Returns:
            Match score from 0.0 to 1.0
        """
        if not symptoms or not pattern_symptoms:
            return 0.0

        # Convert to lowercase for comparison
        query_terms = set(" ".join(symptoms).lower().split())
        pattern_terms = set(" ".join(pattern_symptoms).lower().split())

        if not pattern_terms:
            return 0.0

        # Calculate Jaccard similarity
        intersection = len(query_terms & pattern_terms)
        union = len(query_terms | pattern_terms)

        if union == 0:
            return 0.0

        jaccard = intersection / union

        # Boost score if exact symptom matches exist
        exact_matches = sum(
            1 for s in symptoms if any(s.lower() in ps.lower() for ps in pattern_symptoms)
        )

        exact_boost = min(exact_matches * 0.1, 0.3)

        return min(jaccard + exact_boost, 1.0)

    def _get_confidence_level(self, score: float) -> PatternConfidence:
        """Convert numeric score to confidence level."""
        if score >= 0.85:
            return PatternConfidence.HIGH
        if score >= 0.60:
            return PatternConfidence.MEDIUM
        return PatternConfidence.LOW

    # =========================================================================
    # Pattern Store Access
    # =========================================================================

    def query_patterns(
        self,
        symptoms: str | list[str],
        category: Optional[str] = None,
        min_confidence: PatternConfidence = PatternConfidence.LOW,
        limit: int = 5,
    ) -> list[PatternMatch]:
        """
        Query the pattern store for matching patterns.

        Args:
            symptoms: Symptoms to search for (string or list of strings)
            category: Optional category filter (testing, ci_cd, security, etc.)
            min_confidence: Minimum confidence level for matches
            limit: Maximum number of patterns to return

        Returns:
            List of PatternMatch objects sorted by match score

        Example:
            >>> patterns = brain.query_patterns("pytest collection error")
            >>> for p in patterns:
            ...     logger.info(f"{p.pattern_id}: {p.confidence.value}")
        """
        if isinstance(symptoms, str):
            symptoms = [symptoms]

        matches: list[PatternMatch] = []
        min_score = {
            PatternConfidence.LOW: _MIN_CONFIDENCE,
            PatternConfidence.MEDIUM: 0.60,
            PatternConfidence.HIGH: 0.85,
        }.get(min_confidence, _MIN_CONFIDENCE)

        for pattern_name, pattern_data in self._patterns.items():
            # Apply category filter if specified
            if category and pattern_data.get("category") != category:
                continue

            pattern_symptoms = pattern_data.get("symptoms", [])
            score = self._calculate_match_score(symptoms, pattern_symptoms)

            if score < min_score:
                continue

            confidence = self._get_confidence_level(score)

            match = PatternMatch(
                pattern_id=pattern_data.get("id", pattern_name),
                category=pattern_data.get("category", "general"),
                confidence=confidence,
                match_score=score,
                symptoms=pattern_symptoms,
                solutions=pattern_data.get("solutions", []),
                success_rate=pattern_data.get("success_rate", 0.0),
                times_applied=pattern_data.get("times_applied", 0),
                related_prs=pattern_data.get("related_prs", []),
                diagnosis_steps=pattern_data.get("diagnosis_steps", []),
            )
            matches.append(match)

        # Sort by score descending
        matches.sort(key=lambda m: m.match_score, reverse=True)

        logger.info(f"Query for symptoms {symptoms}: found {len(matches)} matches")

        return matches[:limit]

    def get_pattern(self, pattern_id: str) -> Optional[PatternMatch]:
        """
        Get a specific pattern by ID.

        Args:
            pattern_id: The pattern ID to look up

        Returns:
            PatternMatch if found, None otherwise
        """
        for _, pattern_data in self._patterns.items():
            if pattern_data.get("id") == pattern_id:
                return PatternMatch(
                    pattern_id=pattern_id,
                    category=pattern_data.get("category", "general"),
                    confidence=PatternConfidence.HIGH,
                    match_score=1.0,
                    symptoms=pattern_data.get("symptoms", []),
                    solutions=pattern_data.get("solutions", []),
                    success_rate=pattern_data.get("success_rate", 0.0),
                    times_applied=pattern_data.get("times_applied", 0),
                    related_prs=pattern_data.get("related_prs", []),
                    diagnosis_steps=pattern_data.get("diagnosis_steps", []),
                )
        return None

    def submit_pattern(
        self,
        pattern_id: str,
        category: str,
        symptoms: list[str],
        solutions: list[str],
        diagnosis_steps: Optional[list[str]] = None,
    ) -> bool:
        """
        Submit a new pattern to the pattern store.

        Args:
            pattern_id: Unique identifier for the pattern
            category: Pattern category
            symptoms: List of symptoms this pattern addresses
            solutions: List of solutions for this pattern
            diagnosis_steps: Optional list of diagnosis steps

        Returns:
            True if pattern was added successfully
        """
        pattern_name = pattern_id.lower().replace("-", "_")

        self._patterns[pattern_name] = {
            "id": pattern_id,
            "category": category,
            "symptoms": symptoms,
            "diagnosis_steps": diagnosis_steps or [],
            "solutions": solutions,
            "success_rate": 0.0,
            "times_applied": 0,
            "last_used": "",
            "related_prs": [],
            "submitted_by": self.agent_id,
            "submitted_at": datetime.now(timezone.utc).isoformat(),
        }

        self._save_patterns()
        logger.info(f"New pattern submitted: {pattern_id}")
        return True

    def _save_patterns(self) -> None:
        """Save patterns to the pattern store."""
        try:
            # Ensure directory exists
            self.cognitive_brain_dir.mkdir(parents=True, exist_ok=True)

            # Load existing data to preserve metadata
            existing_data = {}
            if self.pattern_store_path.exists():
                with open(self.pattern_store_path, encoding="utf-8") as f:
                    existing_data = json.load(f)

            # Update patterns
            existing_data["patterns"] = self._patterns
            existing_data["metadata"] = existing_data.get("metadata", {})
            existing_data["metadata"]["last_updated"] = datetime.now(timezone.utc).isoformat()

            # Recalculate statistics
            existing_data["statistics"] = {
                "total_patterns": len(self._patterns),
                "total_applications": sum(
                    p.get("times_applied", 0) for p in self._patterns.values()
                ),
                "average_success_rate": sum(
                    p.get("success_rate", 0) for p in self._patterns.values()
                )
                / max(len(self._patterns), 1),
            }

            with open(self.pattern_store_path, "w", encoding="utf-8") as f:
                json.dump(existing_data, f, indent=2)

            logger.debug("Patterns saved successfully")
        except OSError as e:
            type(e).__name__
            logger.error("Failed to save patterns: <ERROR_TYPE>")

    # =========================================================================
    # Objective Alignment
    # =========================================================================

    def check_alignment(
        self, proposed_action: str, context: Optional[AgentContext] = None
    ) -> ObjectiveAlignment:
        """
        Check if a proposed action aligns with current objectives.

        Args:
            proposed_action: Description of the proposed action
            context: Optional context for more accurate alignment check

        Returns:
            ObjectiveAlignment indicating alignment status
        """
        if not self._objectives:
            return ObjectiveAlignment.UNKNOWN

        action_lower = proposed_action.lower()

        # Check for misalignment keywords FIRST (these are strong signals)
        # Both single words and phrases are matched using substring search
        # e.g., "skip all tests" matches "skip", "skip all", etc.
        misalignment_keywords = [
            "skip",
            "ignore",
            "defer",
            "remove test",
            "disable",
            "skip all",
            "delete test",
            "bypass",
        ]

        # Check for misalignment indicators first (substring matching)
        if any(keyword in action_lower for keyword in misalignment_keywords):
            logger.debug(f"Action '{proposed_action}' contains misalignment keyword")
            return ObjectiveAlignment.MISALIGNED

        # Check for alignment keywords (substring matching works for phrases too)
        alignment_keywords = [
            "fix",
            "coverage",
            "security",
            "documentation",
            "implement",
            "complete",
            "verify",
            "validate",
            "improve",
            "add test",
            "increase coverage",
            "remediate",
        ]

        # Check if action contains alignment keywords (substring matching)
        if any(keyword in action_lower for keyword in alignment_keywords):
            logger.debug(f"Action '{proposed_action}' contains alignment keyword")
            return ObjectiveAlignment.ALIGNED

        # Check objectives for relevance (use significant words only)
        for objective in self._objectives:
            obj_lower = objective.lower()
            # Only check significant words (4+ chars) to avoid common word matches
            significant_words = [w for w in obj_lower.split() if len(w) >= 4]

            # Check if action relates to objective
            if any(word in action_lower for word in significant_words):
                logger.debug(f"Action '{proposed_action}' aligned with objective: {objective}")
                return ObjectiveAlignment.ALIGNED

        # Default to partially aligned if we can't determine
        return ObjectiveAlignment.PARTIALLY_ALIGNED

    def get_objectives(self, include_completed: bool = False) -> list[str]:
        """
        Get current objectives.

        Args:
            include_completed: Whether to include completed objectives

        Returns:
            List of objective strings
        """
        if include_completed:
            # Would need to re-parse the file to get completed
            self._load_objectives()

        return self._objectives.copy()

    def update_objective_progress(
        self,
        objective: str,
        completed: bool = False,
        progress_note: Optional[str] = None,
    ) -> bool:
        """
        Update progress on an objective.

        Args:
            objective: The objective to update
            completed: Whether the objective is complete
            progress_note: Optional note about progress

        Returns:
            True if update was successful
        """
        # This would update the objectives tracker file
        # For now, just log the update
        logger.info(
            f"Objective progress update: {objective} - "
            f"{'completed' if completed else 'in progress'}"
        )

        if completed and objective in self._objectives:
            self._objectives.remove(objective)

        return True

    # =========================================================================
    # Session State
    # =========================================================================

    def get_session_state(self) -> dict[str, Any]:
        """
        Get the current session state.

        Returns:
            Dictionary containing session state information
        """
        return self._session_state.copy()

    def update_session_state(self, updates: dict[str, Any], merge: bool = True) -> bool:
        """
        Update the session state.

        Args:
            updates: Dictionary of updates to apply
            merge: Whether to merge with existing state (True) or replace (False)

        Returns:
            True if update was successful
        """
        if merge:
            self._session_state.update(updates)
        else:
            self._session_state = updates

        self._session_state["last_updated"] = datetime.now(timezone.utc).isoformat()
        self._session_state["updated_by"] = self.agent_id

        logger.debug(f"Session state updated by {self.agent_id}")
        return True

    # =========================================================================
    # Learning Feedback
    # =========================================================================

    def submit_learning(
        self,
        pattern_id: str,
        outcome: str,
        context: Optional[dict[str, Any]] = None,
        resolution_details: str = "",
        new_symptoms: Optional[list[str]] = None,
        suggested_improvements: Optional[list[str]] = None,
    ) -> bool:
        """
        Submit learning feedback after applying a pattern.

        Args:
            pattern_id: ID of the pattern that was applied
            outcome: Result ("success", "failure", "partial")
            context: Context in which the pattern was applied
            resolution_details: Details about how the issue was resolved
            new_symptoms: Any new symptoms discovered
            suggested_improvements: Suggestions for improving the pattern

        Returns:
            True if feedback was submitted successfully

        Example:
            >>> brain.submit_learning(
            ...     pattern_id="TFR-001",
            ...     outcome="success",
            ...     context={"error": "import error", "fix": "added mock"},
            ...     resolution_details="Added mock for optional dependency"
            ... )
        """
        feedback = LearningFeedback(
            pattern_id=pattern_id,
            outcome=outcome,
            agent_id=self.agent_id,
            context=context or {},
            resolution_details=resolution_details,
            new_symptoms=new_symptoms or [],
            suggested_improvements=suggested_improvements or [],
        )

        # Update pattern success rate
        self._update_pattern_stats(feedback)

        logger.info(f"Learning feedback submitted: {pattern_id} - {outcome}")

        return True

    def _update_pattern_stats(self, feedback: LearningFeedback) -> None:
        """Update pattern statistics based on feedback."""
        pattern_name = None
        for name, pattern_data in self._patterns.items():
            if pattern_data.get("id") == feedback.pattern_id:
                pattern_name = name
                break

        if not pattern_name:
            logger.warning(f"Pattern {feedback.pattern_id} not found for stats update")
            return

        pattern = self._patterns[pattern_name]

        # Update times applied
        pattern["times_applied"] = pattern.get("times_applied", 0) + 1
        pattern["last_used"] = datetime.now(timezone.utc).isoformat()

        # Update success rate using EMA (exponential moving average)
        old_rate = pattern.get("success_rate", 0.0)
        new_success = (
            1.0
            if feedback.outcome == "success"
            else (0.5 if feedback.outcome == "partial" else 0.0)
        )
        alpha = 0.3  # EMA smoothing factor
        pattern["success_rate"] = (alpha * new_success) + ((1 - alpha) * old_rate)

        # Save updated patterns
        self._save_patterns()

    # =========================================================================
    # Convenience Methods
    # =========================================================================

    def diagnose(
        self, symptoms: str | list[str], _auto_apply_patterns: bool = False
    ) -> BrainResponse:
        """
        Perform a full diagnosis based on symptoms.

        This convenience method combines pattern querying, objective checking,
        and generates recommendations.

        Args:
            symptoms: Symptoms to diagnose
            auto_apply_patterns: Whether to automatically apply matching patterns

        Returns:
            BrainResponse with patterns, objectives, and recommendations
        """
        # Query patterns
        patterns = self.query_patterns(symptoms)

        # Get relevant objectives
        objectives = self.get_objectives()

        # Generate recommendations
        recommendations = []
        for pattern in patterns[:3]:  # Top 3 patterns
            if pattern.diagnosis_steps:
                recommendations.append(
                    f"Diagnose with pattern {pattern.pattern_id}: {pattern.diagnosis_steps[0]}"
                )
            if pattern.solutions:
                recommendations.append(
                    f"Try solution from {pattern.pattern_id}: {pattern.solutions[0]}"
                )

        return BrainResponse(
            success=True,
            message=f"Diagnosis complete: {len(patterns)} patterns matched",
            patterns=patterns,
            objectives=objectives,
            session_state=self._session_state,
            recommendations=recommendations,
            metadata={
                "agent_id": self.agent_id,
                "query_symptoms": symptoms if isinstance(symptoms, list) else [symptoms],
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        )

    def __repr__(self) -> str:
        return (
            f"AgentBrainInterface("
            f"agent_id='{self.agent_id}', "
            f"category={self.agent_category.value}, "
            f"patterns_loaded={len(self._patterns)}, "
            f"objectives_loaded={len(self._objectives)})"
        )
