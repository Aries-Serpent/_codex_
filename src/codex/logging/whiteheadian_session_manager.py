"""
Whiteheadian Process-Based Session Manager

Refactors session management using Whitehead's process philosophy concepts:
- Sessions as actual occasions (events, not entities)
- Prehension (incorporating past sessions)
- Concrescence (integration of experiences)
- Satisfaction (achievement of completion)

Reference: .codex/docs/PHILOSOPHICAL_FRAMEWORK.md#whitehead-prehension
Philosophical Foundation: Whitehead - Process and Reality (1929)

Core Concepts:
- Actual Occasion: A session is a process of becoming, not a static thing
- Prehension: Loading and incorporating context from past sessions
- Concrescence: The process of integrating prehensions into unified experience
- Satisfaction: The definite outcome of a completed session
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional

LOGGER = logging.getLogger(__name__)


class SessionPhase(Enum):
    """Phases of a session's concrescence (coming-into-being)."""

    INITIAL = "initial"  # Session just created
    PREHENDING = "prehending"  # Loading past context
    CONCRESCING = "concrescing"  # Actively integrating experiences
    SATISFIED = "satisfied"  # Completed with definite outcome
    SUPERSEDED = "superseded"  # Replaced by new actual occasion


@dataclass
class Prehension:
    """
    A prehension - the way one session grasps/incorporates past sessions.

    Following Whitehead: "The theory of prehensions is founded upon the
    doctrine that there are no concrete facts which are merely
    instantaneous. Every such fact has its past and its future."

    Prehension is NOT passive observation - it's active feeling/grasping.
    """

    source_session_id: str  # The past session being prehended
    prehending_session_id: str  # The current session doing the prehending
    intensity: float  # 0.0 (weak) to 1.0 (strong)
    positive: bool  # True = positive prehension, False = negative prehension
    datum: dict[str, Any]  # The content being prehended
    prehended_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        if not 0.0 <= self.intensity <= 1.0:
            raise ValueError(f"Intensity must be 0.0-1.0, got {self.intensity}")


@dataclass
class ActualOccasion:
    """
    An actual occasion - a session modeled as a process of becoming.

    Following Whitehead: "'Actual entities' - also termed 'actual occasions' -
    are the final real things of which the world is made up."

    An actual occasion is:
    - A process, not a thing
    - Self-creating through concrescence
    - Definiteness achieved through satisfaction
    """

    session_id: str
    phase: SessionPhase = SessionPhase.INITIAL
    prehensions: list[Prehension] = field(default_factory=list)
    subjective_aim: str = ""  # The goal/purpose of this session
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    satisfied_at: Optional[datetime] = None
    definiteness: float = 0.0  # 0.0 (vague) to 1.0 (definite)
    novelty_contribution: float = 0.0  # How much new reality was created
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not 0.0 <= self.definiteness <= 1.0:
            raise ValueError(f"Definiteness must be 0.0-1.0, got {self.definiteness}")
        if not 0.0 <= self.novelty_contribution <= 1.0:
            raise ValueError(
                f"Novelty contribution must be 0.0-1.0, got {self.novelty_contribution}"
            )


class WhiteheadianSessionManager:
    """
    Session manager implementing Whiteheadian process philosophy.

    Models sessions as actual occasions that:
    1. Prehend (incorporate) past sessions
    2. Concresce (integrate) experiences
    3. Achieve satisfaction (definite outcomes)
    4. Contribute to creative advance (novelty)

    Example:
        >>> manager = WhiteheadianSessionManager()
        >>> session = manager.create_session("task-123", "Complete refactoring")
        >>> manager.prehend(session, ["session-456", "session-789"])
        >>> manager.concresce(session)
        >>> satisfaction = manager.achieve_satisfaction(session)
        >>> logger.info(f"Session satisfaction: {satisfaction:.2%}")
    """

    def __init__(self) -> None:
        self.occasions: dict[str, ActualOccasion] = {}
        self.prehension_network: dict[str, list[str]] = {}  # session_id -> prehended sessions
        LOGGER.info("WhiteheadianSessionManager initialized")

    def create_session(
        self,
        session_id: str,
        subjective_aim: str,
        metadata: Optional[dict[str, Any]] = None,
    ) -> ActualOccasion:
        """
        Create a new actual occasion (session).

        Args:
            session_id: Unique identifier for the session
            subjective_aim: The goal/purpose of this session
            metadata: Optional metadata

        Returns:
            The created actual occasion
        """
        occasion = ActualOccasion(
            session_id=session_id,
            subjective_aim=subjective_aim,
            metadata=metadata or {},
        )

        self.occasions[session_id] = occasion
        self.prehension_network[session_id] = []

        LOGGER.info(f"Created session {session_id}: {subjective_aim}")
        return occasion

    def prehend(
        self,
        occasion: ActualOccasion,
        past_session_ids: list[str],
        positive: bool = True,
    ) -> list[Prehension]:
        """
        Prehend (incorporate) past sessions into the current session.

        Following Whitehead: "The term 'feeling' will be used as the general
        term synonymous with the term 'positive prehension'."

        Args:
            occasion: The current session doing the prehending
            past_session_ids: IDs of past sessions to prehend
            positive: True for positive prehensions (incorporation),
                     False for negative prehensions (exclusion)

        Returns:
            List of created prehensions
        """
        occasion.phase = SessionPhase.PREHENDING
        created_prehensions: list[Prehension] = []

        for past_id in past_session_ids:
            # Check if past session exists
            past_occasion = self.occasions.get(past_id)
            if not past_occasion:
                LOGGER.warning(f"Cannot prehend non-existent session: {past_id}")
                continue

            # Calculate intensity based on recency and satisfaction
            intensity = self._calculate_prehension_intensity(occasion, past_occasion)

            # Create prehension
            prehension = Prehension(
                source_session_id=past_id,
                prehending_session_id=occasion.session_id,
                intensity=intensity,
                positive=positive,
                datum={
                    "subjective_aim": past_occasion.subjective_aim,
                    "definiteness": past_occasion.definiteness,
                    "novelty": past_occasion.novelty_contribution,
                },
            )

            occasion.prehensions.append(prehension)
            created_prehensions.append(prehension)

            # Track in prehension network
            if past_id not in self.prehension_network[occasion.session_id]:
                self.prehension_network[occasion.session_id].append(past_id)

        LOGGER.info(
            f"Session {occasion.session_id} prehended {len(created_prehensions)} past sessions"
        )
        return created_prehensions

    def concresce(self, occasion: ActualOccasion) -> None:
        """
        Perform concrescence - integrate prehensions into unified experience.

        Following Whitehead: "The term 'concrescence' refers to the growing
        together of the many things that are separately received as data into
        the unity of one actual entity."

        The process:
        1. Integrate all positive prehensions
        2. Exclude negative prehensions
        3. Synthesize into definite outcome
        4. Increase definiteness as integration progresses
        """
        occasion.phase = SessionPhase.CONCRESCING

        if not occasion.prehensions:
            LOGGER.debug(f"Session {occasion.session_id} has no prehensions to concresce")
            return

        # Calculate definiteness from integrated prehensions
        positive_prehensions = [p for p in occasion.prehensions if p.positive]

        if positive_prehensions:
            # Definiteness increases with integration
            total_intensity = sum(p.intensity for p in positive_prehensions)
            avg_intensity = total_intensity / len(positive_prehensions)

            # Increase definiteness based on prehension quality
            occasion.definiteness = min(1.0, 0.3 + (avg_intensity * 0.7))

        LOGGER.info(
            f"Session {occasion.session_id} concrescing: definiteness={occasion.definiteness:.2%}"
        )

    def achieve_satisfaction(self, occasion: ActualOccasion) -> float:
        """
        Achieve satisfaction - the definite outcome of the session.

        Following Whitehead: "The 'satisfaction' of an actual entity is its
        'individual essence' as a definiteness of feeling."

        Satisfaction is measured by:
        - Definiteness achieved
        - Novelty contributed
        - Subjective aim fulfilled

        Returns:
            Satisfaction score (0.0 to 1.0)
        """
        occasion.phase = SessionPhase.SATISFIED
        occasion.satisfied_at = datetime.now(timezone.utc)

        # Calculate satisfaction
        satisfaction = self.calculate_satisfaction(
            prehensions=len(occasion.prehensions),
            realizations=1,  # The session itself is one realization
            definiteness=occasion.definiteness,
        )

        # Store satisfaction in metadata
        occasion.metadata["satisfaction"] = satisfaction

        LOGGER.info(f"Session {occasion.session_id} achieved satisfaction: {satisfaction:.2%}")
        return satisfaction

    def contribute_novelty(self, occasion: ActualOccasion, novelty: float) -> None:
        """
        Record the novelty contribution of this session.

        Following Whitehead: "The many become one, and are increased by one."
        Each actual occasion adds new reality to the universe.

        Args:
            occasion: The session contributing novelty
            novelty: Novelty score (0.0 = no novelty, 1.0 = maximum novelty)
        """
        if not 0.0 <= novelty <= 1.0:
            raise ValueError(f"Novelty must be 0.0-1.0, got {novelty}")

        occasion.novelty_contribution = novelty

        LOGGER.info(f"Session {occasion.session_id} contributed novelty: {novelty:.2%}")

    def supersede(self, old_occasion: ActualOccasion, new_occasion: ActualOccasion) -> None:
        """
        Supersede an old session with a new one.

        The old session becomes part of the past that can be prehended.
        """
        old_occasion.phase = SessionPhase.SUPERSEDED

        # New occasion can prehend the old one
        if old_occasion.session_id not in self.prehension_network.get(new_occasion.session_id, []):
            self.prehend(new_occasion, [old_occasion.session_id])

        LOGGER.info(f"Session {old_occasion.session_id} superseded by {new_occasion.session_id}")

    def _calculate_prehension_intensity(
        self, current: ActualOccasion, past: ActualOccasion
    ) -> float:
        """
        Calculate intensity of prehension based on recency and quality.

        More recent and more definite sessions have stronger prehension.
        """
        # Base intensity
        intensity = 0.5

        # Increase for satisfied sessions
        if past.phase == SessionPhase.SATISFIED:
            intensity += 0.2

        # Increase for definite sessions
        intensity += past.definiteness * 0.3

        # Cap at 1.0
        return min(1.0, intensity)

    @staticmethod
    def calculate_satisfaction(prehensions: int, realizations: int, definiteness: float) -> float:
        """
        Calculate session satisfaction.

        Satisfaction = (Prehensions + Realizations) × Definiteness

        Where:
        - Prehensions = Past sessions incorporated
        - Realizations = Potentials actualized
        - Definiteness = Completion percentage (0.0-1.0)

        Reference: .codex/docs/PHILOSOPHICAL_FRAMEWORK.md#session-satisfaction
        """
        if not 0.0 <= definiteness <= 1.0:
            raise ValueError(f"Definiteness must be 0.0-1.0, got {definiteness}")

        return (prehensions + realizations) * definiteness

    def get_prehension_history(self, session_id: str) -> list[str]:
        """
        Get the prehension history of a session.

        Returns all past sessions that this session has prehended.
        """
        return self.prehension_network.get(session_id, [])

    def get_creative_advance_rate(self, time_window_hours: float = 24.0) -> float:
        """
        Calculate the rate of creative advance.

        Following Whitehead: The universe is constantly creating new
        actual occasions, advancing into novelty.

        Returns:
            Rate of session creation (sessions per hour)
        """
        if not self.occasions:
            return 0.0

        # Count satisfied sessions in time window
        now = datetime.now(timezone.utc)
        cutoff = now.timestamp() - (time_window_hours * 3600)

        satisfied_in_window = sum(
            1
            for occ in self.occasions.values()
            if occ.satisfied_at and occ.satisfied_at.timestamp() >= cutoff
        )

        rate = satisfied_in_window / time_window_hours
        LOGGER.debug(f"Creative advance rate: {rate:.2f} sessions/hour")
        return rate

    def get_stats(self) -> dict[str, Any]:
        """Get statistics about sessions and prehensions."""
        satisfied = sum(1 for occ in self.occasions.values() if occ.phase == SessionPhase.SATISFIED)
        total_prehensions = sum(len(occ.prehensions) for occ in self.occasions.values())

        avg_definiteness = (
            sum(occ.definiteness for occ in self.occasions.values()) / len(self.occasions)
            if self.occasions
            else 0.0
        )

        return {
            "total_sessions": len(self.occasions),
            "satisfied_sessions": satisfied,
            "total_prehensions": total_prehensions,
            "avg_definiteness": avg_definiteness,
            "creative_advance_rate": self.get_creative_advance_rate(),
        }
