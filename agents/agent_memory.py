"""
Agent Memory System for Context Preservation and Learning

This module extends the mental mapping model with:
1. Persistent memory storage across sessions
2. Context sharing between agent invocations
3. Pattern recognition for similar tasks
4. Learning from past decisions

Integrates with:
- Mental Mapping Model (agents/mental_mapping.py)
- Physics Orchestrator (agents/physics_orchestrator.py)
- Quantum Game Theory (agents/quantum_game_theory.py)
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import sqlite3
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Optional, Union

logger = logging.getLogger(__name__)

__all__ = [
    "AgentMemory",
    "MemoryEntry",
    "ContextFrame",
    "PatternLibrary",
    "AgentMemorySystem",
]


@dataclass
class MemoryEntry:
    """A single memory entry representing a learned fact or decision.

    Attributes:
        memory_id: Unique identifier
        category: Type of memory (decision, fact, pattern, lesson)
        content: The actual memory content
        context: Contextual information when memory was created
        confidence: Confidence in this memory's validity (0-1)
        access_count: Number of times this memory was accessed
        last_accessed: Timestamp of last access
        created_at: Timestamp of creation
        tags: Searchable tags
        related_memories: IDs of related memories
    """

    memory_id: str
    category: str
    content: str
    context: dict[str, Any]
    confidence: float = 0.8
    access_count: int = 0
    last_accessed: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    tags: list[str] = field(default_factory=list)
    related_memories: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "memory_id": self.memory_id,
            "category": self.category,
            "content": self.content,
            "context": self.context,
            "confidence": self.confidence,
            "access_count": self.access_count,
            "last_accessed": self.last_accessed,
            "created_at": self.created_at,
            "tags": self.tags,
            "related_memories": self.related_memories,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "MemoryEntry":
        return cls(**data)


@dataclass
class ContextFrame:
    """A snapshot of context for a specific task or session.

    Represents the working memory during a task execution.
    """

    frame_id: str
    task_description: str
    start_time: str
    end_time: Optional[str] = None
    status: str = "active"  # active, completed, failed, paused

    # Working memory
    active_memories: list[str] = field(default_factory=list)
    decisions_made: list[dict[str, Any]] = field(default_factory=list)
    lessons_learned: list[str] = field(default_factory=list)

    # Environment context
    repository: Optional[str] = None
    branch: Optional[str] = None
    files_modified: list[str] = field(default_factory=list)

    # Performance metrics
    tokens_used: int = 0
    actions_taken: int = 0
    errors_encountered: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "frame_id": self.frame_id,
            "task_description": self.task_description,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "status": self.status,
            "active_memories": self.active_memories,
            "decisions_made": self.decisions_made,
            "lessons_learned": self.lessons_learned,
            "repository": self.repository,
            "branch": self.branch,
            "files_modified": self.files_modified,
            "tokens_used": self.tokens_used,
            "actions_taken": self.actions_taken,
            "errors_encountered": self.errors_encountered,
        }


class PatternLibrary:
    """Library of recognized patterns for decision support.

    Patterns are extracted from successful decisions and can be
    matched against new situations for guidance.
    """

    def __init__(self):
        self.patterns: dict[str, dict[str, Any]] = {}
        self.pattern_index: dict[str, list[str]] = {}  # tag -> pattern_ids

    def add_pattern(
        self,
        pattern_id: str,
        name: str,
        description: str,
        triggers: list[str],
        recommended_actions: list[str],
        success_rate: float,
        examples: list[dict[str, Any]],
        tags: list[str],
    ) -> None:
        """Add a new pattern to the library."""
        self.patterns[pattern_id] = {
            "pattern_id": pattern_id,
            "name": name,
            "description": description,
            "triggers": triggers,
            "recommended_actions": recommended_actions,
            "success_rate": success_rate,
            "examples": examples,
            "tags": tags,
            "usage_count": 0,
            "created_at": datetime.now().isoformat(),
        }

        # Index by tags
        for tag in tags:
            if tag not in self.pattern_index:
                self.pattern_index[tag] = []
            self.pattern_index[tag].append(pattern_id)

    def match_patterns(
        self,
        situation: str,
        tags: list[str] = None,
        min_success_rate: float = 0.5,
    ) -> list[dict[str, Any]]:
        """Find patterns matching the current situation."""
        matches = []

        # Get candidate patterns by tags
        candidate_ids = set()
        if tags:
            for tag in tags:
                candidate_ids.update(self.pattern_index.get(tag, []))
        else:
            candidate_ids = set(self.patterns.keys())

        # Score each candidate
        situation_lower = situation.lower()
        for pattern_id in candidate_ids:
            pattern = self.patterns[pattern_id]

            if pattern["success_rate"] < min_success_rate:
                continue

            # Check trigger words
            trigger_matches = sum(
                1 for trigger in pattern["triggers"] if trigger.lower() in situation_lower
            )

            if trigger_matches > 0:
                score = trigger_matches / len(pattern["triggers"])
                matches.append(
                    {
                        "pattern": pattern,
                        "match_score": score,
                        "trigger_matches": trigger_matches,
                    }
                )

        # Sort by match score
        matches.sort(key=lambda x: x["match_score"], reverse=True)

        return matches

    def record_pattern_usage(self, pattern_id: str, success: bool) -> None:
        """Record usage of a pattern and update success rate."""
        if pattern_id in self.patterns:
            pattern = self.patterns[pattern_id]
            old_count = pattern["usage_count"]
            old_rate = pattern["success_rate"]

            new_count = old_count + 1
            # Exponential moving average
            alpha = 0.1
            new_rate = old_rate * (1 - alpha) + (1.0 if success else 0.0) * alpha

            pattern["usage_count"] = new_count
            pattern["success_rate"] = new_rate

    def to_dict(self) -> dict[str, Any]:
        return {
            "patterns": self.patterns,
            "pattern_index": self.pattern_index,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "PatternLibrary":
        lib = cls()
        lib.patterns = data.get("patterns", {})
        lib.pattern_index = data.get("pattern_index", {})
        return lib


class AgentMemory:
    """SQLite-backed persistent memory storage for agent context.

    Provides:
    - Long-term memory storage across sessions
    - Fast retrieval by category, tags, or similarity
    - Memory consolidation and pruning
    - Cross-session context sharing
    """

    def __init__(self, db_path: Path = None):
        """Initialize agent memory with SQLite storage.

        Args:
            db_path: Path to SQLite database file. If None, uses CODEX_LOG_DB_PATH
                     environment variable or defaults to '.codex/agent_memory.db'.
                     Path is validated to prevent traversal attacks.
        """
        if db_path is None:
            env_path = os.getenv("CODEX_LOG_DB_PATH", ".codex/agent_memory.db")
            db_path = Path(env_path)

        # Validate path to prevent traversal attacks
        # Resolve to absolute path and ensure it's within expected directories
        db_path = Path(db_path).resolve()

        # Allow paths within current directory, home directory, or /tmp
        allowed_roots = [
            Path.cwd().resolve(),
            Path.home().resolve(),
            Path("/tmp").resolve(),
        ]

        is_allowed = any(
            str(db_path).startswith(str(root)) for root in allowed_roots if root.exists()
        )

        if not is_allowed:
            raise ValueError(
                f"Database path {db_path} is outside allowed directories. "
                f"Must be within current directory, home directory, or /tmp."
            )

        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        self._init_database()

    def _init_database(self) -> None:
        """Initialize database schema."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS memories (
                    memory_id TEXT PRIMARY KEY,
                    category TEXT NOT NULL,
                    content TEXT NOT NULL,
                    context TEXT,
                    confidence REAL DEFAULT 0.8,
                    access_count INTEGER DEFAULT 0,
                    last_accessed TEXT,
                    created_at TEXT NOT NULL,
                    tags TEXT,
                    related_memories TEXT
                )
            """
            )

            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS context_frames (
                    frame_id TEXT PRIMARY KEY,
                    task_description TEXT,
                    start_time TEXT NOT NULL,
                    end_time TEXT,
                    status TEXT DEFAULT 'active',
                    data TEXT
                )
            """
            )

            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS patterns (
                    pattern_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    data TEXT
                )
            """
            )

            # Create indexes
            conn.execute("CREATE INDEX IF NOT EXISTS idx_memories_category ON memories(category)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_memories_created ON memories(created_at)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_frames_status ON context_frames(status)")

            conn.commit()

    def store_memory(self, entry: Union["MemoryEntry", dict, None] = None, **kwargs: Any) -> None:
        """
        Store a memory entry.

        Args:
            entry (Union[MemoryEntry, dict, None]): The memory entry to store. If None, kwargs are used.
            **kwargs: Alternative way to provide memory data (backward compatibility).
                Accepts keys: memory_id/key, category, content/value, context, confidence, access_count,
                last_accessed, created_at, tags, related_memories.
        """
        # Handle backward compatibility: dict or kwargs
        if entry is None:
            # Create MemoryEntry from kwargs
            # Support both old style (key, value) and new style (explicit fields)
            if "key" in kwargs and "value" in kwargs:
                # Old style: key-value pair
                entry = MemoryEntry(
                    memory_id=kwargs.get("key", str(uuid.uuid4())),
                    category=kwargs.get("category", "fact"),
                    content=str(kwargs.get("value", "")),
                    context=kwargs.get("context", {}),
                    confidence=kwargs.get("confidence", 0.8),
                    tags=kwargs.get("tags", []),
                    related_memories=kwargs.get("related_memories", []),
                )
            else:
                # New style: explicit MemoryEntry fields
                entry = MemoryEntry(
                    memory_id=kwargs.get("memory_id", str(uuid.uuid4())),
                    category=kwargs.get("category", "fact"),
                    content=kwargs.get("content", ""),
                    context=kwargs.get("context", {}),
                    confidence=kwargs.get("confidence", 0.8),
                    access_count=kwargs.get("access_count", 0),
                    last_accessed=kwargs.get("last_accessed"),
                    created_at=kwargs.get("created_at", datetime.now().isoformat()),
                    tags=kwargs.get("tags", []),
                    related_memories=kwargs.get("related_memories", []),
                )
        elif isinstance(entry, dict):
            # Handle dict input
            entry = MemoryEntry(
                memory_id=entry.get("memory_id", entry.get("key", str(uuid.uuid4()))),
                category=entry.get("category", "fact"),
                content=entry.get("content", str(entry.get("value", ""))),
                context=entry.get("context", {}),
                confidence=entry.get("confidence", 0.8),
                access_count=entry.get("access_count", 0),
                last_accessed=entry.get("last_accessed"),
                created_at=entry.get("created_at", datetime.now().isoformat()),
                tags=entry.get("tags", []),
                related_memories=entry.get("related_memories", []),
            )

        # Store the entry
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO memories 
                (memory_id, category, content, context, confidence, 
                 access_count, last_accessed, created_at, tags, related_memories)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    entry.memory_id,
                    entry.category,
                    entry.content,
                    json.dumps(entry.context),
                    entry.confidence,
                    entry.access_count,
                    entry.last_accessed,
                    entry.created_at,
                    json.dumps(entry.tags),
                    json.dumps(entry.related_memories),
                ),
            )
            conn.commit()

    def add_memory(
        self, entry: Union["MemoryEntry", dict, None] = None, **kwargs: Any
    ) -> None:
        """
        Add a memory entry (alias for store_memory for API consistency).

        This method provides compatibility with tests and external callers
        that expect add_memory() as the primary API.

        Args:
            entry: MemoryEntry object, dict, or None
            **kwargs: Alternative memory data (memory_id, category, content, etc.)
                - memory_id: Unique identifier for the memory
                - category: Category of memory (decision, observation, learning)
                - content: The actual memory content
                - confidence: Float 0-1 indicating confidence
                - context: Additional context dict

        Returns:
            None

        Examples:
            >>> memory.add_memory({"category": "decision", "content": "test"})
            >>> memory.add_memory(memory_id="123", category="observation", content="data")
        """
        return self.store_memory(entry=entry, **kwargs)

    def retrieve_memory(
        self, memory_id: str = None, key: str = None
    ) -> Optional[Union[MemoryEntry, str]]:
        """
        Retrieve a memory by ID or key.

        Args:
            memory_id: The memory ID to retrieve
            key: Alternative parameter name for backward compatibility (deprecated, use retrieve_content instead)

        Returns:
            MemoryEntry object, or the content string if using key parameter (for backward compatibility)

        Note:
            When using key parameter, returns content string only.
            For new code, use retrieve_content(key) to get content or retrieve_memory(memory_id) to get MemoryEntry.
        """
        # Handle backward compatibility with 'key' parameter
        if key is not None and memory_id is None:
            memory_id = key
            return_content_only = True
        else:
            return_content_only = False

        if memory_id is None:
            return None

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT * FROM memories WHERE memory_id = ?", (memory_id,))
            row = cursor.fetchone()

            if row:
                # Update access count
                conn.execute(
                    """
                    UPDATE memories 
                    SET access_count = access_count + 1,
                        last_accessed = ?
                    WHERE memory_id = ?
                """,
                    (datetime.now().isoformat(), memory_id),
                )
                conn.commit()

                memory_entry = self._row_to_memory(row)
                # Return just content if using key parameter (backward compat)
                if return_content_only:
                    return memory_entry.content
                return memory_entry

        return None

    def retrieve_content(self, key: Optional[str]) -> Optional[str]:
        """
        Retrieve memory content by key.

        Args:
            key: The memory key to retrieve (optional)

        Returns:
            Memory content string, or None if not found or key is None
        """
        if key is None:
            return None

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT * FROM memories WHERE memory_id = ?", (key,))
            row = cursor.fetchone()

            if row:
                # Update access count
                conn.execute(
                    """
                    UPDATE memories 
                    SET access_count = access_count + 1,
                        last_accessed = ?
                    WHERE memory_id = ?
                """,
                    (datetime.now().isoformat(), key),
                )
                conn.commit()

                memory_entry = self._row_to_memory(row)
                return memory_entry.content

        return None

    def clear(self) -> None:
        """Clear all memories from the database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM memories")
            conn.commit()

    def search_memories(
        self,
        category: str = None,
        tags: list[str] = None,
        min_confidence: float = 0.0,
        limit: int = 50,
    ) -> list[MemoryEntry]:
        """Search memories by criteria."""
        query = "SELECT * FROM memories WHERE 1=1"
        params = []

        if category:
            query += " AND category = ?"
            params.append(category)

        if min_confidence > 0:
            query += " AND confidence >= ?"
            params.append(min_confidence)

        query += " ORDER BY confidence DESC, access_count DESC LIMIT ?"
        params.append(limit)

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(query, params)
            rows = cursor.fetchall()

        memories = [self._row_to_memory(row) for row in rows]

        # Filter by tags if specified
        if tags:
            memories = [m for m in memories if any(tag in m.tags for tag in tags)]

        return memories

    def _row_to_memory(self, row: tuple) -> MemoryEntry:
        """Convert database row to MemoryEntry."""
        return MemoryEntry(
            memory_id=row[0],
            category=row[1],
            content=row[2],
            context=json.loads(row[3]) if row[3] else {},
            confidence=row[4],
            access_count=row[5],
            last_accessed=row[6],
            created_at=row[7],
            tags=json.loads(row[8]) if row[8] else [],
            related_memories=json.loads(row[9]) if row[9] else [],
        )

    def store_context_frame(self, frame: ContextFrame) -> None:
        """Store a context frame."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO context_frames
                (frame_id, task_description, start_time, end_time, status, data)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
                (
                    frame.frame_id,
                    frame.task_description,
                    frame.start_time,
                    frame.end_time,
                    frame.status,
                    json.dumps(frame.to_dict()),
                ),
            )
            conn.commit()

    def get_recent_context_frames(self, limit: int = 10) -> list[ContextFrame]:
        """Get recent context frames."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """
                SELECT data FROM context_frames
                ORDER BY start_time DESC
                LIMIT ?
            """,
                (limit,),
            )
            rows = cursor.fetchall()

        frames = []
        for row in rows:
            data = json.loads(row[0])
            frames.append(
                ContextFrame(
                    **{k: v for k, v in data.items() if k in ContextFrame.__dataclass_fields__}
                )
            )

        return frames

    def consolidate_memories(self, older_than_days: int = 30) -> int:
        """Consolidate old memories by reducing detail but keeping key facts.

        Returns number of memories consolidated.
        """
        cutoff = datetime.now().isoformat()[:10]  # Date only

        with sqlite3.connect(self.db_path) as conn:
            # Get old, low-access memories
            cursor = conn.execute(
                """
                SELECT memory_id, content, confidence 
                FROM memories 
                WHERE created_at < ? AND access_count < 3
            """,
                (cutoff,),
            )
            rows = cursor.fetchall()

            consolidated = 0
            for row in rows:
                # Reduce confidence of rarely accessed old memories
                new_confidence = row[2] * 0.9
                if new_confidence < 0.3:
                    # Delete very low confidence old memories
                    conn.execute("DELETE FROM memories WHERE memory_id = ?", (row[0],))
                else:
                    conn.execute(
                        """
                        UPDATE memories SET confidence = ?
                        WHERE memory_id = ?
                    """,
                        (new_confidence, row[0]),
                    )
                consolidated += 1

            conn.commit()

        return consolidated

    def get_memory_stats(self) -> dict[str, Any]:
        """Get statistics about stored memories."""
        with sqlite3.connect(self.db_path) as conn:
            total = conn.execute("SELECT COUNT(*) FROM memories").fetchone()[0]
            by_category = dict(
                conn.execute(
                    """
                SELECT category, COUNT(*) FROM memories GROUP BY category
            """
                ).fetchall()
            )
            avg_confidence = (
                conn.execute("SELECT AVG(confidence) FROM memories").fetchone()[0] or 0.0
            )
            total_accesses = (
                conn.execute("SELECT SUM(access_count) FROM memories").fetchone()[0] or 0
            )

        return {
            "total_memories": total,
            "by_category": by_category,
            "average_confidence": avg_confidence,
            "total_accesses": total_accesses,
        }

    def statistics(self) -> dict[str, Any]:
        """Alias for get_memory_stats (backward compatibility)."""
        return self.get_memory_stats()

    def search(self, query: str = None, **kwargs) -> list[MemoryEntry]:
        """
        Search memories with text query (alias for search_memories).

        Args:
            query: Search query string
            **kwargs: Additional search parameters

        Returns:
            list of matching MemoryEntry objects
        """
        # Simple text search in content
        if query:
            memories = self.search_memories(**kwargs)
            query_lower = query.lower()
            return [m for m in memories if query_lower in m.content.lower()]
        return self.search_memories(**kwargs)

    def filter(self, criteria: dict[str, Any] = None, **kwargs) -> list[MemoryEntry]:
        """
        Filter memories by criteria dictionary.

        Args:
            criteria: Filter criteria as dict (e.g., {"type": "concept"})
            **kwargs: Additional filter parameters

        Returns:
            list of matching MemoryEntry objects
        """
        if not criteria:
            return self.search_memories(**kwargs)

        # Convert criteria to search parameters
        category = criteria.get("type") or criteria.get("category")
        return self.search_memories(category=category, **kwargs)

    def update(self, memory_id: str, new_content: str) -> bool:
        """
        Update an existing memory entry.

        Args:
            memory_id: ID of memory to update
            new_content: New content to store

        Returns:
            True if successful, False otherwise
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT * FROM memories WHERE memory_id = ?", (memory_id,))
            if not cursor.fetchone():
                return False

            conn.execute(
                "UPDATE memories SET content = ? WHERE memory_id = ?", (new_content, memory_id)
            )
            conn.commit()
            return True


class AgentMemorySystem:
    """High-level agent memory system integrating all components.

    Provides a unified interface for:
    - Storing and retrieving memories
    - Managing context frames
    - Pattern matching and learning
    - Cross-session context preservation
    """

    def __init__(
        self,
        agent_id: str = "default_agent",
        db_path: Path = None,
    ):
        self.agent_id = agent_id
        self.memory = AgentMemory(db_path)
        self.pattern_library = PatternLibrary()
        self.current_frame: Optional[ContextFrame] = None

        # Load existing patterns
        self._load_patterns()

        # Initialize with common patterns
        self._init_common_patterns()

    def _load_patterns(self) -> None:
        """Load patterns from database."""
        pass  # Patterns are stored in-memory for simplicity

    def _init_common_patterns(self) -> None:
        """Initialize common decision patterns."""
        # Code review pattern
        self.pattern_library.add_pattern(
            pattern_id="code_review_fix",
            name="Code Review Comment Resolution",
            description="Pattern for resolving code review comments",
            triggers=["review", "comment", "fix", "address", "feedback"],
            recommended_actions=[
                "Read and understand the comment",
                "Identify the specific change needed",
                "Make minimal targeted fix",
                "Verify fix doesn't break existing behavior",
                "Update tests if needed",
            ],
            success_rate=0.85,
            examples=[],
            tags=["code_review", "fix", "pr"],
        )

        # Security fix pattern
        self.pattern_library.add_pattern(
            pattern_id="security_fix",
            name="Security Vulnerability Fix",
            description="Pattern for fixing security vulnerabilities",
            triggers=["security", "vulnerability", "xss", "injection", "traversal"],
            recommended_actions=[
                "Identify vulnerability type",
                "Understand attack vector",
                "Implement defense-in-depth fix",
                "Add input validation",
                "Run security scans",
            ],
            success_rate=0.90,
            examples=[],
            tags=["security", "fix", "vulnerability"],
        )

        # Test failure pattern
        self.pattern_library.add_pattern(
            pattern_id="test_failure_debug",
            name="Test Failure Debugging",
            description="Pattern for debugging test failures",
            triggers=["test", "fail", "error", "assertion", "exception"],
            recommended_actions=[
                "Read error message carefully",
                "Identify failing test",
                "Check recent changes",
                "Run test in isolation",
                "Add debugging output",
            ],
            success_rate=0.80,
            examples=[],
            tags=["test", "debug", "failure"],
        )

    def start_task(self, task_description: str) -> ContextFrame:
        """Start a new task and create context frame."""
        frame_id = hashlib.sha256(
            f"{self.agent_id}:{task_description}:{datetime.now().isoformat()}".encode()
        ).hexdigest()[:16]

        self.current_frame = ContextFrame(
            frame_id=frame_id,
            task_description=task_description,
            start_time=datetime.now().isoformat(),
            repository=os.getenv("GITHUB_REPOSITORY"),
            branch=os.getenv("GITHUB_HEAD_REF"),
        )

        # Find relevant memories
        relevant = self.memory.search_memories(
            tags=task_description.lower().split()[:5],
            min_confidence=0.5,
            limit=10,
        )

        self.current_frame.active_memories = [m.memory_id for m in relevant]

        logger.info(f"Started task: {task_description}")
        logger.info(f"Found {len(relevant)} relevant memories")

        return self.current_frame

    def record_decision(
        self,
        decision: str,
        alternatives: list[str],
        confidence: float,
        reasoning: str,
    ) -> MemoryEntry:
        """Record a decision made during the task."""
        memory_id = hashlib.sha256(f"{decision}:{datetime.now().isoformat()}".encode()).hexdigest()[
            :16
        ]

        entry = MemoryEntry(
            memory_id=memory_id,
            category="decision",
            content=decision,
            context={
                "alternatives": alternatives,
                "reasoning": reasoning,
                "task_frame": self.current_frame.frame_id if self.current_frame else None,
            },
            confidence=confidence,
            tags=decision.lower().split()[:5],
        )

        self.memory.store_memory(entry)

        if self.current_frame:
            self.current_frame.decisions_made.append(
                {
                    "memory_id": memory_id,
                    "decision": decision,
                    "confidence": confidence,
                }
            )

        return entry

    def record_lesson(self, lesson: str, success: bool) -> MemoryEntry:
        """Record a lesson learned."""
        memory_id = hashlib.sha256(f"{lesson}:{datetime.now().isoformat()}".encode()).hexdigest()[
            :16
        ]

        entry = MemoryEntry(
            memory_id=memory_id,
            category="lesson",
            content=lesson,
            context={
                "success": success,
                "task_frame": self.current_frame.frame_id if self.current_frame else None,
            },
            confidence=0.9 if success else 0.7,
            tags=lesson.lower().split()[:5] + ["lesson"],
        )

        self.memory.store_memory(entry)

        if self.current_frame:
            self.current_frame.lessons_learned.append(lesson)

        return entry

    def get_guidance(self, situation: str) -> dict[str, Any]:
        """Get guidance for a situation based on patterns and memories."""
        # Find matching patterns
        pattern_matches = self.pattern_library.match_patterns(situation)

        # Find relevant memories
        relevant_memories = self.memory.search_memories(
            tags=situation.lower().split()[:5],
            min_confidence=0.6,
            limit=5,
        )

        guidance = {
            "patterns": [
                {
                    "name": m["pattern"]["name"],
                    "actions": m["pattern"]["recommended_actions"],
                    "success_rate": m["pattern"]["success_rate"],
                    "match_score": m["match_score"],
                }
                for m in pattern_matches[:3]
            ],
            "relevant_memories": [
                {
                    "content": m.content,
                    "confidence": m.confidence,
                    "category": m.category,
                }
                for m in relevant_memories
            ],
            "suggested_approach": None,
        }

        # Generate suggested approach
        if pattern_matches:
            best_pattern = pattern_matches[0]["pattern"]
            guidance["suggested_approach"] = {
                "based_on": best_pattern["name"],
                "steps": best_pattern["recommended_actions"],
                "confidence": best_pattern["success_rate"] * pattern_matches[0]["match_score"],
            }

        return guidance

    def complete_task(self, success: bool, summary: str) -> None:
        """Complete the current task and save context."""
        if self.current_frame:
            self.current_frame.end_time = datetime.now().isoformat()
            self.current_frame.status = "completed" if success else "failed"

            # Save context frame
            self.memory.store_context_frame(self.current_frame)

            # Record task outcome as memory
            outcome_entry = MemoryEntry(
                memory_id=hashlib.sha256(
                    f"outcome:{self.current_frame.frame_id}".encode()
                ).hexdigest()[:16],
                category="outcome",
                content=summary,
                context={
                    "task": self.current_frame.task_description,
                    "success": success,
                    "decisions_count": len(self.current_frame.decisions_made),
                    "lessons_count": len(self.current_frame.lessons_learned),
                },
                confidence=1.0,
                tags=["outcome", "task_completion"],
            )
            self.memory.store_memory(outcome_entry)

            logger.info(f"Task completed: {success}")
            logger.info(f"Summary: {summary}")

            self.current_frame = None

    def get_stats(self) -> dict[str, Any]:
        """Get memory system statistics."""
        memory_stats = self.memory.get_memory_stats()

        return {
            "agent_id": self.agent_id,
            "memory_stats": memory_stats,
            "patterns_count": len(self.pattern_library.patterns),
            "current_task": self.current_frame.task_description if self.current_frame else None,
        }

    # =========================================================================
    # Required API methods (per gap analysis Phase A.2)
    # =========================================================================

    def store_decision(
        self,
        task_id: str,
        decision: str,
        rationale: str,
        context: dict[str, Any] = None,
    ) -> str:
        """Store a decision with its rationale and context.

        This is the canonical API method for recording decisions.

        Args:
            task_id: Unique identifier for the task
            decision: The decision made
            rationale: Explanation of why this decision was made
            context: Additional context dictionary

        Returns:
            Memory ID of the stored decision
        """
        # Use task_id + decision content for deterministic ID generation.
        # Ensure different decisions receive different IDs while keeping 16-char length.
        content_hash = hashlib.sha256(f"{task_id}:{decision}:{rationale}".encode()).hexdigest()
        # Enforce strict 16-character IDs for downstream integrations
        memory_id = content_hash[:16]

        entry = MemoryEntry(
            memory_id=memory_id,
            category="decision",
            content=decision,
            context={
                "task_id": task_id,
                "rationale": rationale,
                **(context or {}),
            },
            confidence=0.8,
            tags=[task_id, "decision"] + decision.lower().split()[:3],
        )

        self.memory.store_memory(entry)
        logger.info(f"Stored decision for task {task_id}: {decision[:50]}...")
        return memory_id

    def retrieve_similar_context(
        self,
        task_description: str,
        limit: int = 5,
    ) -> list[dict[str, Any]]:
        """Retrieve similar contexts based on task description.

        Uses keyword matching and confidence scoring to find
        relevant past contexts and decisions.

        Args:
            task_description: Description of the current task
            limit: Maximum number of results to return

        Returns:
            list of context dictionaries with relevance scores
        """
        # Extract keywords from task description
        keywords = [
            word.lower() for word in task_description.split() if len(word) > 3  # Skip short words
        ][:10]

        if not keywords:
            fallback_memories = self.memory.search_memories(
                min_confidence=0.5,
                limit=limit,
            )

            return [
                {
                    "memory_id": memory.memory_id,
                    "content": memory.content,
                    "context": memory.context,
                    "category": memory.category,
                    "confidence": memory.confidence,
                    "relevance_score": memory.confidence,
                    "created_at": memory.created_at,
                }
                for memory in fallback_memories
            ]

        # Search memories by keywords
        all_relevant = []
        for keyword in keywords:
            memories = self.memory.search_memories(
                tags=[keyword],
                min_confidence=0.5,
                limit=limit * 2,
            )
            all_relevant.extend(memories)

        # Deduplicate and score
        seen_ids = set()
        scored_results = []

        for memory in all_relevant:
            if memory.memory_id in seen_ids:
                continue
            seen_ids.add(memory.memory_id)

            # Calculate relevance score
            matching_keywords = sum(
                1 for kw in keywords if kw in memory.content.lower() or kw in memory.tags
            )
            relevance = (matching_keywords / len(keywords)) * memory.confidence

            scored_results.append(
                {
                    "memory_id": memory.memory_id,
                    "content": memory.content,
                    "context": memory.context,
                    "category": memory.category,
                    "confidence": memory.confidence,
                    "relevance_score": relevance,
                    "created_at": memory.created_at,
                }
            )

        # Sort by relevance and return top results
        scored_results.sort(key=lambda x: x["relevance_score"], reverse=True)
        return scored_results[:limit]

    def get_pattern_library(self) -> list[dict[str, Any]]:
        """Get all patterns from the pattern library.

        Returns:
            list of pattern dictionaries with metadata
        """
        return [
            {
                "pattern_id": pattern_id,
                "name": pattern["name"],
                "description": pattern["description"],
                "triggers": pattern["triggers"],
                "recommended_actions": pattern["recommended_actions"],
                "success_rate": pattern["success_rate"],
                "usage_count": pattern.get("usage_count", 0),
                "tags": pattern["tags"],
            }
            for pattern_id, pattern in self.pattern_library.patterns.items()
        ]

    def invalidate_stale_contexts(self, age_days: int = 30) -> int:
        """Invalidate and clean up stale contexts older than specified days.

        Reduces confidence of old, rarely-accessed memories and
        removes very low confidence entries.

        Args:
            age_days: Age threshold in days for considering context stale

        Returns:
            Number of memories invalidated or removed
        """
        from datetime import timedelta

        cutoff_date = (datetime.now() - timedelta(days=age_days)).isoformat()

        invalidated = 0

        with sqlite3.connect(self.memory.db_path) as conn:
            # Get old memories with low access counts
            cursor = conn.execute(
                """
                SELECT memory_id, confidence, access_count
                FROM memories
                WHERE created_at < ? AND access_count < 5
            """,
                (cutoff_date,),
            )
            rows = cursor.fetchall()

            for memory_id, confidence, access_count in rows:
                # Calculate decay factor based on age and access
                decay = 0.8 if access_count > 2 else 0.6
                new_confidence = confidence * decay

                if new_confidence < 0.2:
                    # Remove very low confidence old memories
                    conn.execute("DELETE FROM memories WHERE memory_id = ?", (memory_id,))
                    logger.debug(f"Removed stale memory: {memory_id}")
                else:
                    # Reduce confidence
                    conn.execute(
                        """
                        UPDATE memories SET confidence = ?
                        WHERE memory_id = ?
                    """,
                        (new_confidence, memory_id),
                    )

                invalidated += 1

            conn.commit()

        logger.info(f"Invalidated {invalidated} stale contexts older than {age_days} days")
        return invalidated


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    print("=" * 60)
    print("Agent Memory System Demo")
    print("=" * 60)

    # Create memory system
    memory_system = AgentMemorySystem(
        agent_id="demo_agent",
        db_path=Path("/tmp/demo_agent_memory.db"),
    )

    # Start a task
    frame = memory_system.start_task("Fix code review comments in PR #2463")
    print(f"\nStarted task: {frame.task_description}")
    print(f"Frame ID: {frame.frame_id}")

    # Get guidance
    guidance = memory_system.get_guidance("fix security vulnerability path traversal")
    print(f"\nGuidance for situation:")
    print(f"  Patterns matched: {len(guidance['patterns'])}")
    if guidance["suggested_approach"]:
        print(f"  Suggested approach: {guidance['suggested_approach']['based_on']}")
        print(f"  Confidence: {guidance['suggested_approach']['confidence']:.2f}")

    # Record decisions
    memory_system.record_decision(
        decision="Use commonpath for path traversal prevention",
        alternatives=["Use startswith", "Use realpath only"],
        confidence=0.85,
        reasoning="commonpath handles edge cases better than startswith",
    )

    # Record lesson
    memory_system.record_lesson(
        "Always wrap commonpath in try/except for cross-platform compatibility",
        success=True,
    )

    # Complete task
    memory_system.complete_task(
        success=True,
        summary="Fixed 4 review comments including security vulnerability",
    )

    # Show stats
    stats = memory_system.get_stats()
    print(f"\nMemory System Stats:")
    print(f"  Total memories: {stats['memory_stats']['total_memories']}")
    print(f"  Patterns: {stats['patterns_count']}")

    print("\n" + "=" * 60)
    print("Demo Complete")
    print("=" * 60)
