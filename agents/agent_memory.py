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
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

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
    context: Dict[str, Any]
    confidence: float = 0.8
    access_count: int = 0
    last_accessed: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    tags: List[str] = field(default_factory=list)
    related_memories: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'memory_id': self.memory_id,
            'category': self.category,
            'content': self.content,
            'context': self.context,
            'confidence': self.confidence,
            'access_count': self.access_count,
            'last_accessed': self.last_accessed,
            'created_at': self.created_at,
            'tags': self.tags,
            'related_memories': self.related_memories,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MemoryEntry':
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
    active_memories: List[str] = field(default_factory=list)
    decisions_made: List[Dict[str, Any]] = field(default_factory=list)
    lessons_learned: List[str] = field(default_factory=list)
    
    # Environment context
    repository: Optional[str] = None
    branch: Optional[str] = None
    files_modified: List[str] = field(default_factory=list)
    
    # Performance metrics
    tokens_used: int = 0
    actions_taken: int = 0
    errors_encountered: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'frame_id': self.frame_id,
            'task_description': self.task_description,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'status': self.status,
            'active_memories': self.active_memories,
            'decisions_made': self.decisions_made,
            'lessons_learned': self.lessons_learned,
            'repository': self.repository,
            'branch': self.branch,
            'files_modified': self.files_modified,
            'tokens_used': self.tokens_used,
            'actions_taken': self.actions_taken,
            'errors_encountered': self.errors_encountered,
        }


class PatternLibrary:
    """Library of recognized patterns for decision support.
    
    Patterns are extracted from successful decisions and can be
    matched against new situations for guidance.
    """
    
    def __init__(self):
        self.patterns: Dict[str, Dict[str, Any]] = {}
        self.pattern_index: Dict[str, List[str]] = {}  # tag -> pattern_ids
    
    def add_pattern(
        self,
        pattern_id: str,
        name: str,
        description: str,
        triggers: List[str],
        recommended_actions: List[str],
        success_rate: float,
        examples: List[Dict[str, Any]],
        tags: List[str],
    ) -> None:
        """Add a new pattern to the library."""
        self.patterns[pattern_id] = {
            'pattern_id': pattern_id,
            'name': name,
            'description': description,
            'triggers': triggers,
            'recommended_actions': recommended_actions,
            'success_rate': success_rate,
            'examples': examples,
            'tags': tags,
            'usage_count': 0,
            'created_at': datetime.now().isoformat(),
        }
        
        # Index by tags
        for tag in tags:
            if tag not in self.pattern_index:
                self.pattern_index[tag] = []
            self.pattern_index[tag].append(pattern_id)
    
    def match_patterns(
        self,
        situation: str,
        tags: List[str] = None,
        min_success_rate: float = 0.5,
    ) -> List[Dict[str, Any]]:
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
            
            if pattern['success_rate'] < min_success_rate:
                continue
            
            # Check trigger words
            trigger_matches = sum(
                1 for trigger in pattern['triggers']
                if trigger.lower() in situation_lower
            )
            
            if trigger_matches > 0:
                score = trigger_matches / len(pattern['triggers'])
                matches.append({
                    'pattern': pattern,
                    'match_score': score,
                    'trigger_matches': trigger_matches,
                })
        
        # Sort by match score
        matches.sort(key=lambda x: x['match_score'], reverse=True)
        
        return matches
    
    def record_pattern_usage(self, pattern_id: str, success: bool) -> None:
        """Record usage of a pattern and update success rate."""
        if pattern_id in self.patterns:
            pattern = self.patterns[pattern_id]
            old_count = pattern['usage_count']
            old_rate = pattern['success_rate']
            
            new_count = old_count + 1
            # Exponential moving average
            alpha = 0.1
            new_rate = old_rate * (1 - alpha) + (1.0 if success else 0.0) * alpha
            
            pattern['usage_count'] = new_count
            pattern['success_rate'] = new_rate
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'patterns': self.patterns,
            'pattern_index': self.pattern_index,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PatternLibrary':
        lib = cls()
        lib.patterns = data.get('patterns', {})
        lib.pattern_index = data.get('pattern_index', {})
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
            env_path = os.getenv('CODEX_LOG_DB_PATH', '.codex/agent_memory.db')
            db_path = Path(env_path)
        
        # Validate path to prevent traversal attacks
        # Resolve to absolute path and ensure it's within expected directories
        db_path = Path(db_path).resolve()
        
        # Allow paths within current directory, home directory, or /tmp
        allowed_roots = [
            Path.cwd().resolve(),
            Path.home().resolve(),
            Path('/tmp').resolve(),
        ]
        
        is_allowed = any(
            str(db_path).startswith(str(root))
            for root in allowed_roots
            if root.exists()
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
            conn.execute("""
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
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS context_frames (
                    frame_id TEXT PRIMARY KEY,
                    task_description TEXT,
                    start_time TEXT NOT NULL,
                    end_time TEXT,
                    status TEXT DEFAULT 'active',
                    data TEXT
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS patterns (
                    pattern_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    data TEXT
                )
            """)
            
            # Create indexes
            conn.execute("CREATE INDEX IF NOT EXISTS idx_memories_category ON memories(category)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_memories_created ON memories(created_at)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_frames_status ON context_frames(status)")
            
            conn.commit()
    
    def store_memory(self, entry: MemoryEntry) -> None:
        """Store a memory entry."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO memories 
                (memory_id, category, content, context, confidence, 
                 access_count, last_accessed, created_at, tags, related_memories)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
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
            ))
            conn.commit()
    
    def retrieve_memory(self, memory_id: str) -> Optional[MemoryEntry]:
        """Retrieve a memory by ID."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT * FROM memories WHERE memory_id = ?",
                (memory_id,)
            )
            row = cursor.fetchone()
            
            if row:
                # Update access count
                conn.execute("""
                    UPDATE memories 
                    SET access_count = access_count + 1,
                        last_accessed = ?
                    WHERE memory_id = ?
                """, (datetime.now().isoformat(), memory_id))
                conn.commit()
                
                return self._row_to_memory(row)
        
        return None
    
    def search_memories(
        self,
        category: str = None,
        tags: List[str] = None,
        min_confidence: float = 0.0,
        limit: int = 50,
    ) -> List[MemoryEntry]:
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
            memories = [
                m for m in memories
                if any(tag in m.tags for tag in tags)
            ]
        
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
            conn.execute("""
                INSERT OR REPLACE INTO context_frames
                (frame_id, task_description, start_time, end_time, status, data)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                frame.frame_id,
                frame.task_description,
                frame.start_time,
                frame.end_time,
                frame.status,
                json.dumps(frame.to_dict()),
            ))
            conn.commit()
    
    def get_recent_context_frames(self, limit: int = 10) -> List[ContextFrame]:
        """Get recent context frames."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT data FROM context_frames
                ORDER BY start_time DESC
                LIMIT ?
            """, (limit,))
            rows = cursor.fetchall()
        
        frames = []
        for row in rows:
            data = json.loads(row[0])
            frames.append(ContextFrame(**{
                k: v for k, v in data.items()
                if k in ContextFrame.__dataclass_fields__
            }))
        
        return frames
    
    def consolidate_memories(self, older_than_days: int = 30) -> int:
        """Consolidate old memories by reducing detail but keeping key facts.
        
        Returns number of memories consolidated.
        """
        cutoff = datetime.now().isoformat()[:10]  # Date only
        
        with sqlite3.connect(self.db_path) as conn:
            # Get old, low-access memories
            cursor = conn.execute("""
                SELECT memory_id, content, confidence 
                FROM memories 
                WHERE created_at < ? AND access_count < 3
            """, (cutoff,))
            rows = cursor.fetchall()
            
            consolidated = 0
            for row in rows:
                # Reduce confidence of rarely accessed old memories
                new_confidence = row[2] * 0.9
                if new_confidence < 0.3:
                    # Delete very low confidence old memories
                    conn.execute("DELETE FROM memories WHERE memory_id = ?", (row[0],))
                else:
                    conn.execute("""
                        UPDATE memories SET confidence = ?
                        WHERE memory_id = ?
                    """, (new_confidence, row[0]))
                consolidated += 1
            
            conn.commit()
        
        return consolidated
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get statistics about stored memories."""
        with sqlite3.connect(self.db_path) as conn:
            total = conn.execute("SELECT COUNT(*) FROM memories").fetchone()[0]
            by_category = dict(conn.execute("""
                SELECT category, COUNT(*) FROM memories GROUP BY category
            """).fetchall())
            avg_confidence = conn.execute(
                "SELECT AVG(confidence) FROM memories"
            ).fetchone()[0] or 0.0
            total_accesses = conn.execute(
                "SELECT SUM(access_count) FROM memories"
            ).fetchone()[0] or 0
            
        return {
            'total_memories': total,
            'by_category': by_category,
            'average_confidence': avg_confidence,
            'total_accesses': total_accesses,
        }


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
            repository=os.getenv('GITHUB_REPOSITORY'),
            branch=os.getenv('GITHUB_HEAD_REF'),
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
        alternatives: List[str],
        confidence: float,
        reasoning: str,
    ) -> MemoryEntry:
        """Record a decision made during the task."""
        memory_id = hashlib.sha256(
            f"{decision}:{datetime.now().isoformat()}".encode()
        ).hexdigest()[:16]
        
        entry = MemoryEntry(
            memory_id=memory_id,
            category="decision",
            content=decision,
            context={
                'alternatives': alternatives,
                'reasoning': reasoning,
                'task_frame': self.current_frame.frame_id if self.current_frame else None,
            },
            confidence=confidence,
            tags=decision.lower().split()[:5],
        )
        
        self.memory.store_memory(entry)
        
        if self.current_frame:
            self.current_frame.decisions_made.append({
                'memory_id': memory_id,
                'decision': decision,
                'confidence': confidence,
            })
        
        return entry
    
    def record_lesson(self, lesson: str, success: bool) -> MemoryEntry:
        """Record a lesson learned."""
        memory_id = hashlib.sha256(
            f"{lesson}:{datetime.now().isoformat()}".encode()
        ).hexdigest()[:16]
        
        entry = MemoryEntry(
            memory_id=memory_id,
            category="lesson",
            content=lesson,
            context={
                'success': success,
                'task_frame': self.current_frame.frame_id if self.current_frame else None,
            },
            confidence=0.9 if success else 0.7,
            tags=lesson.lower().split()[:5] + ['lesson'],
        )
        
        self.memory.store_memory(entry)
        
        if self.current_frame:
            self.current_frame.lessons_learned.append(lesson)
        
        return entry
    
    def get_guidance(self, situation: str) -> Dict[str, Any]:
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
            'patterns': [
                {
                    'name': m['pattern']['name'],
                    'actions': m['pattern']['recommended_actions'],
                    'success_rate': m['pattern']['success_rate'],
                    'match_score': m['match_score'],
                }
                for m in pattern_matches[:3]
            ],
            'relevant_memories': [
                {
                    'content': m.content,
                    'confidence': m.confidence,
                    'category': m.category,
                }
                for m in relevant_memories
            ],
            'suggested_approach': None,
        }
        
        # Generate suggested approach
        if pattern_matches:
            best_pattern = pattern_matches[0]['pattern']
            guidance['suggested_approach'] = {
                'based_on': best_pattern['name'],
                'steps': best_pattern['recommended_actions'],
                'confidence': best_pattern['success_rate'] * pattern_matches[0]['match_score'],
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
                    'task': self.current_frame.task_description,
                    'success': success,
                    'decisions_count': len(self.current_frame.decisions_made),
                    'lessons_count': len(self.current_frame.lessons_learned),
                },
                confidence=1.0,
                tags=['outcome', 'task_completion'],
            )
            self.memory.store_memory(outcome_entry)
            
            logger.info(f"Task completed: {success}")
            logger.info(f"Summary: {summary}")
            
            self.current_frame = None
    
    def get_stats(self) -> Dict[str, Any]:
        """Get memory system statistics."""
        memory_stats = self.memory.get_memory_stats()
        
        return {
            'agent_id': self.agent_id,
            'memory_stats': memory_stats,
            'patterns_count': len(self.pattern_library.patterns),
            'current_task': self.current_frame.task_description if self.current_frame else None,
        }


# Example usage
if __name__ == '__main__':
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
    if guidance['suggested_approach']:
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
