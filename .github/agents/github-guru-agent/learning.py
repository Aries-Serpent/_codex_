"""
GitHub Guru Agent — Self-Evolution Learning

Captures patterns from each session and refines detection logic.
Implements the "Reflect → Capture → Refine → Improve" loop.

Lesson entries are stored in audit_artifacts/baselines/guru_lessons.jsonl.
"""
from __future__ import annotations

import json
import logging
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)


@dataclass
class LessonEntry:
    """A single lesson learned from a session."""

    lesson_id: str
    session_id: str
    capability: str
    observation: str  # what was observed
    hypothesis: str  # why it happened
    action_taken: str  # what was done
    outcome: str  # result of the action
    pattern_id: Optional[str] = None  # related pattern if applicable
    confidence: float = 0.5
    tags: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["created_at"] = self.created_at.isoformat()
        return d


class LearningEngine:
    """
    Captures and surfaces lessons from each session.

    Persists lessons to JSONL for longitudinal analysis and
    pattern refinement recommendations.
    """

    def __init__(
        self,
        session_id: str,
        lessons_file: Optional[Path] = None,
    ):
        self._session_id = session_id
        self._lessons_file = lessons_file or Path(
            "audit_artifacts/baselines/guru_lessons.jsonl"
        )
        self._lessons: list[LessonEntry] = []
        self._lesson_counter = 0

    def record_lesson(
        self,
        capability: str,
        observation: str,
        hypothesis: str,
        action_taken: str,
        outcome: str,
        pattern_id: Optional[str] = None,
        confidence: float = 0.5,
        tags: Optional[list[str]] = None,
    ) -> LessonEntry:
        """Record a lesson learned during a capability run."""
        self._lesson_counter += 1
        lesson = LessonEntry(
            lesson_id=f"{self._session_id}-L{self._lesson_counter:03d}",
            session_id=self._session_id,
            capability=capability,
            observation=observation,
            hypothesis=hypothesis,
            action_taken=action_taken,
            outcome=outcome,
            pattern_id=pattern_id,
            confidence=confidence,
            tags=tags or [],
        )
        self._lessons.append(lesson)
        logger.debug("Lesson recorded: %s", lesson.lesson_id)
        return lesson

    def get_lessons(self) -> list[LessonEntry]:
        """Return lessons from this session."""
        return list(self._lessons)

    def finalize(self) -> int:
        """Persist all lessons to the JSONL file. Returns count written."""
        if not self._lessons:
            return 0
        try:
            self._lessons_file.parent.mkdir(parents=True, exist_ok=True)
            with self._lessons_file.open("a", encoding="utf-8") as fh:
                for lesson in self._lessons:
                    fh.write(json.dumps(lesson.to_dict(), default=str) + "\n")
            logger.info("Persisted %d lessons to %s", len(self._lessons), self._lessons_file)
            return len(self._lessons)
        except OSError as exc:
            logger.warning("Could not persist lessons: %s", exc)
            return 0

    def load_all_lessons(self) -> list[dict[str, Any]]:
        """Load all historically persisted lessons for reflection."""
        if not self._lessons_file.exists():
            return []
        lessons: list[dict[str, Any]] = []
        try:
            with self._lessons_file.open(encoding="utf-8") as fh:
                for line in fh:
                    line = line.strip()
                    if line:
                        lessons.append(json.loads(line))
        except (OSError, json.JSONDecodeError) as exc:
            logger.warning("Could not load lessons: %s", exc)
        return lessons

    def get_pattern_refinements(self) -> list[dict[str, Any]]:
        """
        Analyze lessons to suggest pattern refinements.

        Returns list of dicts with pattern_id and suggested improvement.
        """
        all_lessons = self.load_all_lessons()
        refinements: dict[str, int] = {}

        for lesson in all_lessons:
            pid = lesson.get("pattern_id")
            outcome = lesson.get("outcome", "")
            if pid and "false positive" in outcome.lower():
                refinements[pid] = refinements.get(pid, 0) + 1

        return [
            {
                "pattern_id": pid,
                "false_positive_count": count,
                "suggestion": f"Review pattern {pid}: {count} false positives recorded",
            }
            for pid, count in sorted(refinements.items(), key=lambda x: -x[1])
        ]
