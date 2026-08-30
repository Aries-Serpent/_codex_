"""
Knowledge Distiller - Phase 4.1 of Long-term Plan 4.

This module provides knowledge distillation capabilities for extracting,
generalizing, and storing key learnings from each session for cross-session
context retention.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any


class KnowledgeType(Enum):
    """Types of knowledge that can be distilled."""

    FACTUAL = "factual"  # Codebase conventions, API patterns
    PROCEDURAL = "procedural"  # How to fix specific issues
    CONTEXTUAL = "contextual"  # Current project state, pending work
    DECISION = "decision"  # Key decisions made
    PATTERN = "pattern"  # Recurring patterns discovered


class KnowledgePriority(Enum):
    """Priority levels for knowledge retention."""

    CRITICAL = "critical"  # Must always retain (security, breaking changes)
    HIGH = "high"  # Important for most sessions
    MEDIUM = "medium"  # Useful context
    LOW = "low"  # Nice to have, can decay


@dataclass
class KnowledgeItem:
    """A single piece of distilled knowledge."""

    id: str
    knowledge_type: KnowledgeType
    priority: KnowledgePriority
    content: str
    source: str  # Where this knowledge came from
    session_id: str
    created_at: datetime
    last_accessed: datetime
    access_count: int = 0
    tags: list[str] = field(default_factory=list)
    related_files: list[str] = field(default_factory=list)
    confidence: float = 1.0  # How confident we are in this knowledge

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "knowledge_type": self.knowledge_type.value,
            "priority": self.priority.value,
            "content": self.content,
            "source": self.source,
            "session_id": self.session_id,
            "created_at": self.created_at.isoformat(),
            "last_accessed": self.last_accessed.isoformat(),
            "access_count": self.access_count,
            "tags": self.tags,
            "related_files": self.related_files,
            "confidence": self.confidence,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> KnowledgeItem:
        """Create from dictionary."""
        return cls(
            id=data["id"],
            knowledge_type=KnowledgeType(data["knowledge_type"]),
            priority=KnowledgePriority(data["priority"]),
            content=data["content"],
            source=data["source"],
            session_id=data["session_id"],
            created_at=datetime.fromisoformat(data["created_at"]),
            last_accessed=datetime.fromisoformat(data["last_accessed"]),
            access_count=data.get("access_count", 0),
            tags=data.get("tags", []),
            related_files=data.get("related_files", []),
            confidence=data.get("confidence", 1.0),
        )


@dataclass
class SessionSummary:
    """Summary of a session for knowledge extraction."""

    session_id: str
    start_time: datetime
    end_time: datetime | None
    files_modified: list[str]
    patterns_used: list[str]
    decisions_made: list[str]
    issues_resolved: list[str]
    learnings: list[str]
    pending_work: list[str]

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "session_id": self.session_id,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "files_modified": self.files_modified,
            "patterns_used": self.patterns_used,
            "decisions_made": self.decisions_made,
            "issues_resolved": self.issues_resolved,
            "learnings": self.learnings,
            "pending_work": self.pending_work,
        }


class KnowledgeStore:
    """Persistent storage for distilled knowledge."""

    def __init__(self, store_path: Path | None = None):
        """Initialize knowledge store."""
        self.store_path = store_path or Path(".codex/knowledge/knowledge_store.json")
        self._knowledge: dict[str, KnowledgeItem] = {}
        self._load()

    def _load(self) -> None:
        """Load knowledge from disk."""
        if self.store_path.exists():
            try:
                with open(self.store_path) as f:
                    data = json.load(f)
                    for item_data in data.get("items", []):
                        item = KnowledgeItem.from_dict(item_data)
                        self._knowledge[item.id] = item
            except (json.JSONDecodeError, KeyError):
                self._knowledge = {}

    def save(self) -> None:
        """Save knowledge to disk."""
        self.store_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.store_path, "w") as f:
            json.dump(
                {
                    "version": "1.0",
                    "updated_at": datetime.now(timezone.utc).isoformat(),
                    "items": [item.to_dict() for item in self._knowledge.values()],
                },
                f,
                indent=2,
            )

    def add(self, item: KnowledgeItem) -> None:
        """Add a knowledge item."""
        self._knowledge[item.id] = item
        self.save()

    def get(self, item_id: str) -> KnowledgeItem | None:
        """Get a knowledge item by ID."""
        item = self._knowledge.get(item_id)
        if item:
            item.access_count += 1
            item.last_accessed = datetime.now(timezone.utc)
        return item

    def search(
        self,
        query: str,
        knowledge_type: KnowledgeType | None = None,
        min_priority: KnowledgePriority | None = None,
        tags: list[str] | None = None,
    ) -> list[KnowledgeItem]:
        """Search for knowledge items."""
        results = []
        query_lower = query.lower()
        priority_order = {
            KnowledgePriority.CRITICAL: 0,
            KnowledgePriority.HIGH: 1,
            KnowledgePriority.MEDIUM: 2,
            KnowledgePriority.LOW: 3,
        }
        min_priority_value = priority_order.get(min_priority, 3) if min_priority else 3

        for item in self._knowledge.values():
            # Filter by type
            if knowledge_type and item.knowledge_type != knowledge_type:
                continue

            # Filter by priority
            if priority_order[item.priority] > min_priority_value:
                continue

            # Filter by tags
            if tags and not any(tag in item.tags for tag in tags):
                continue

            # Search in content
            if query_lower in item.content.lower():
                results.append(item)
                continue

            # Search in tags
            if any(query_lower in tag.lower() for tag in item.tags):
                results.append(item)

        return results

    def get_by_type(self, knowledge_type: KnowledgeType) -> list[KnowledgeItem]:
        """Get all items of a specific type."""
        return [item for item in self._knowledge.values() if item.knowledge_type == knowledge_type]

    def get_critical(self) -> list[KnowledgeItem]:
        """Get all critical knowledge items."""
        return [
            item for item in self._knowledge.values() if item.priority == KnowledgePriority.CRITICAL
        ]

    def prune_low_priority(self, max_age_days: int = 30) -> int:
        """Remove old low-priority items."""
        now = datetime.now(timezone.utc)
        to_remove = []

        for item_id, item in self._knowledge.items():
            if item.priority == KnowledgePriority.LOW:
                age_days = (now - item.last_accessed).days
                if age_days > max_age_days:
                    to_remove.append(item_id)

        for item_id in to_remove:
            del self._knowledge[item_id]

        if to_remove:
            self.save()

        return len(to_remove)

    def count(self) -> int:
        """Get total count of knowledge items."""
        return len(self._knowledge)


class LearningExtractor:
    """Extract learnings from session activity."""

    # Patterns that indicate a learning
    LEARNING_PATTERNS = [
        r"fixed by",
        r"solution:",
        r"the issue was",
        r"root cause:",
        r"resolved by",
        r"workaround:",
        r"lesson learned:",
        r"note:",
        r"important:",
        r"remember:",
    ]

    def __init__(self) -> None:
        """Initialize extractor."""
        self._patterns = [re.compile(p, re.IGNORECASE) for p in self.LEARNING_PATTERNS]

    def extract_from_text(self, text: str) -> list[str]:
        """Extract learnings from text."""
        learnings = []
        lines = text.split("\n")

        for i, line in enumerate(lines):
            for pattern in self._patterns:
                if pattern.search(line):
                    # Get the context (current line and possibly next)
                    learning = line.strip()
                    if i + 1 < len(lines) and lines[i + 1].strip():
                        learning += " " + lines[i + 1].strip()
                    learnings.append(learning)
                    break

        return learnings

    def extract_from_commit_messages(self, messages: list[str]) -> list[str]:
        """Extract learnings from commit messages."""
        learnings = []

        for message in messages:
            # Look for fix/resolve patterns
            if re.search(r"fix|resolve|address|correct", message, re.IGNORECASE):
                learnings.append(f"Fix pattern: {message}")

            # Look for feature additions
            if re.search(r"add|implement|create|introduce", message, re.IGNORECASE):
                learnings.append(f"Implementation: {message}")

        return learnings


class DecisionExtractor:
    """Extract decisions from session activity."""

    DECISION_PATTERNS = [
        r"decided to",
        r"choosing",
        r"selected",
        r"opted for",
        r"will use",
        r"going with",
        r"approach:",
        r"strategy:",
    ]

    def __init__(self) -> None:
        """Initialize extractor."""
        self._patterns = [re.compile(p, re.IGNORECASE) for p in self.DECISION_PATTERNS]

    def extract_from_text(self, text: str) -> list[str]:
        """Extract decisions from text."""
        decisions = []
        lines = text.split("\n")

        for line in lines:
            for pattern in self._patterns:
                if pattern.search(line):
                    decisions.append(line.strip())
                    break

        return decisions


class KnowledgeDistiller:
    """Main class for distilling knowledge from sessions."""

    def __init__(self, store_path: Path | None = None):
        """Initialize distiller."""
        self.store = KnowledgeStore(store_path)
        self.learning_extractor = LearningExtractor()
        self.decision_extractor = DecisionExtractor()
        self._next_id = self.store.count() + 1

    def _generate_id(self) -> str:
        """Generate a unique ID."""
        item_id = f"KN-{self._next_id:05d}"
        self._next_id += 1
        return item_id

    def distill_from_session(
        self,
        session_id: str,
        files_modified: list[str],
        commit_messages: list[str],
        session_notes: str | None = None,
    ) -> list[KnowledgeItem]:
        """Distill knowledge from a session."""
        items = []
        now = datetime.now(timezone.utc)

        # Extract learnings from commit messages
        learnings = self.learning_extractor.extract_from_commit_messages(commit_messages)
        for learning in learnings:
            item = KnowledgeItem(
                id=self._generate_id(),
                knowledge_type=KnowledgeType.PROCEDURAL,
                priority=KnowledgePriority.MEDIUM,
                content=learning,
                source="commit_message",
                session_id=session_id,
                created_at=now,
                last_accessed=now,
                related_files=files_modified[:5],  # Limit to 5 files
            )
            items.append(item)
            self.store.add(item)

        # Extract learnings from session notes
        if session_notes:
            learnings = self.learning_extractor.extract_from_text(session_notes)
            for learning in learnings:
                item = KnowledgeItem(
                    id=self._generate_id(),
                    knowledge_type=KnowledgeType.PROCEDURAL,
                    priority=KnowledgePriority.HIGH,
                    content=learning,
                    source="session_notes",
                    session_id=session_id,
                    created_at=now,
                    last_accessed=now,
                )
                items.append(item)
                self.store.add(item)

            # Extract decisions
            decisions = self.decision_extractor.extract_from_text(session_notes)
            for decision in decisions:
                item = KnowledgeItem(
                    id=self._generate_id(),
                    knowledge_type=KnowledgeType.DECISION,
                    priority=KnowledgePriority.HIGH,
                    content=decision,
                    source="session_notes",
                    session_id=session_id,
                    created_at=now,
                    last_accessed=now,
                )
                items.append(item)
                self.store.add(item)

        # Record modified files as contextual knowledge
        if files_modified:
            item = KnowledgeItem(
                id=self._generate_id(),
                knowledge_type=KnowledgeType.CONTEXTUAL,
                priority=KnowledgePriority.MEDIUM,
                content=f"Modified {len(files_modified)} files: {', '.join(files_modified[:10])}",
                source="file_changes",
                session_id=session_id,
                created_at=now,
                last_accessed=now,
                related_files=files_modified,
            )
            items.append(item)
            self.store.add(item)

        return items

    def add_pattern_knowledge(
        self,
        pattern_id: str,
        pattern_description: str,
        resolution_steps: list[str],
        session_id: str,
    ) -> KnowledgeItem:
        """Add knowledge about a discovered pattern."""
        now = datetime.now(timezone.utc)
        content = (
            f"Pattern {pattern_id}: {pattern_description}\n"
            f"Resolution: {'; '.join(resolution_steps)}"
        )

        item = KnowledgeItem(
            id=self._generate_id(),
            knowledge_type=KnowledgeType.PATTERN,
            priority=KnowledgePriority.HIGH,
            content=content,
            source="pattern_discovery",
            session_id=session_id,
            created_at=now,
            last_accessed=now,
            tags=[pattern_id],
        )
        self.store.add(item)
        return item

    def add_critical_knowledge(
        self,
        content: str,
        source: str,
        session_id: str,
        tags: list[str] | None = None,
    ) -> KnowledgeItem:
        """Add critical knowledge that must always be retained."""
        now = datetime.now(timezone.utc)

        item = KnowledgeItem(
            id=self._generate_id(),
            knowledge_type=KnowledgeType.FACTUAL,
            priority=KnowledgePriority.CRITICAL,
            content=content,
            source=source,
            session_id=session_id,
            created_at=now,
            last_accessed=now,
            tags=tags or [],
        )
        self.store.add(item)
        return item

    def get_session_context(
        self,
        limit: int = 20,
        min_priority: KnowledgePriority = KnowledgePriority.MEDIUM,
    ) -> list[KnowledgeItem]:
        """Get relevant context for starting a new session."""
        # Get all critical items
        critical = self.store.get_critical()

        # Get recent high/medium priority items
        all_items = list(self.store._knowledge.values())
        all_items.sort(key=lambda x: x.last_accessed, reverse=True)

        priority_order = {
            KnowledgePriority.CRITICAL: 0,
            KnowledgePriority.HIGH: 1,
            KnowledgePriority.MEDIUM: 2,
            KnowledgePriority.LOW: 3,
        }
        min_value = priority_order[min_priority]

        filtered = [item for item in all_items if priority_order[item.priority] <= min_value]

        # Combine, deduplicate, and limit
        seen_ids = set()
        result = []
        for item in critical + filtered:
            if item.id not in seen_ids:
                seen_ids.add(item.id)
                result.append(item)
                if len(result) >= limit:
                    break

        return result

    def summarize_for_handoff(self, session_id: str) -> str:
        """Generate a summary of session knowledge for handoff."""
        items = [item for item in self.store._knowledge.values() if item.session_id == session_id]

        if not items:
            return "No knowledge distilled from this session."

        summary_parts = ["## Session Knowledge Summary\n"]

        # Group by type
        by_type: dict[KnowledgeType, list[KnowledgeItem]] = {}
        for item in items:
            by_type.setdefault(item.knowledge_type, []).append(item)

        for ktype, type_items in by_type.items():
            summary_parts.append(f"\n### {ktype.value.title()}\n")
            for item in type_items:
                summary_parts.append(f"- {item.content[:100]}...")

        return "\n".join(summary_parts)
