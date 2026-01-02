"""
Cognitive Brain - Centralized Learning and Pattern Storage
SQLite-based storage for cross-agent learning, pattern recognition, and decision history.

#AFTERMATH_PATTERN_IDENTIFIED: Centralized learning enables cross-agent collaboration
All agents contribute to and benefit from shared cognitive brain.
"""
import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from contextlib import contextmanager


class CognitiveBrain:
    """
    Centralized learning and memory system for all cognitive agents.
    
    Stores:
    - Session history and metrics
    - Pattern occurrences and scores
    - Lessons learned across agents
    - Decision rationales and outcomes
    
    Uses SQLite for persistent storage in `.codex/brain.db`
    """
    
    def __init__(self, db_path: Optional[Path] = None):
        """
        Initialize cognitive brain with SQLite storage.
        
        Args:
            db_path: Path to SQLite database (default: .codex/brain.db)
        """
        self.db_path = db_path or Path(".codex/brain.db")
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize_schema()
    
    @contextmanager
    def _get_connection(self):
        """Context manager for database connections."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
    
    def _initialize_schema(self):
        """Create database schema if it doesn't exist."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Sessions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    agent_name TEXT NOT NULL,
                    agent_version TEXT NOT NULL,
                    start_time TEXT NOT NULL,
                    end_time TEXT,
                    status TEXT,
                    task_type TEXT,
                    metrics TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Patterns table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS patterns (
                    pattern_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pattern_name TEXT NOT NULL UNIQUE,
                    pattern_type TEXT NOT NULL,
                    description TEXT,
                    occurrences INTEGER DEFAULT 0,
                    confidence_score REAL DEFAULT 0.0,
                    first_seen TEXT DEFAULT CURRENT_TIMESTAMP,
                    last_seen TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Pattern occurrences table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS pattern_occurrences (
                    occurrence_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pattern_id INTEGER NOT NULL,
                    session_id TEXT NOT NULL,
                    context TEXT,
                    timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (pattern_id) REFERENCES patterns(pattern_id),
                    FOREIGN KEY (session_id) REFERENCES sessions(session_id)
                )
            """)
            
            # Lessons table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS lessons (
                    lesson_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    lesson_text TEXT NOT NULL,
                    category TEXT,
                    confidence REAL DEFAULT 0.8,
                    validated BOOLEAN DEFAULT 0,
                    timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (session_id) REFERENCES sessions(session_id)
                )
            """)
            
            # Decisions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS decisions (
                    decision_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    context TEXT NOT NULL,
                    decision TEXT NOT NULL,
                    rationale TEXT,
                    outcome TEXT,
                    success BOOLEAN,
                    timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (session_id) REFERENCES sessions(session_id)
                )
            """)
            
            # Create indices for better performance
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_sessions_agent 
                ON sessions(agent_name, start_time)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_patterns_name 
                ON patterns(pattern_name)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_lessons_session 
                ON lessons(session_id, timestamp)
            """)
    
    def start_session(
        self, 
        session_id: str, 
        agent_name: str, 
        agent_version: str,
        task_type: str
    ) -> None:
        """
        Start a new agent session.
        
        Args:
            session_id: Unique session identifier
            agent_name: Name of the agent
            agent_version: Agent version
            task_type: Type of task being executed
        """
        with self._get_connection() as conn:
            conn.execute("""
                INSERT INTO sessions 
                (session_id, agent_name, agent_version, start_time, task_type, status)
                VALUES (?, ?, ?, ?, ?, 'running')
            """, (session_id, agent_name, agent_version, datetime.now().isoformat(), task_type))
    
    def end_session(
        self, 
        session_id: str, 
        status: str, 
        metrics: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        End an agent session and store metrics.
        
        Args:
            session_id: Session identifier
            status: Final status ('success', 'failure', 'error')
            metrics: Performance metrics dictionary
        """
        with self._get_connection() as conn:
            conn.execute("""
                UPDATE sessions 
                SET end_time = ?, status = ?, metrics = ?
                WHERE session_id = ?
            """, (
                datetime.now().isoformat(),
                status,
                json.dumps(metrics) if metrics else None,
                session_id
            ))
    
    def record_pattern(
        self, 
        session_id: str,
        pattern_name: str, 
        pattern_type: str,
        description: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Record a pattern occurrence.
        
        Args:
            session_id: Current session ID
            pattern_name: Name of the pattern
            pattern_type: Type (e.g., 'exception', 'import', 'test')
            description: Pattern description
            context: Additional context
        
        Returns:
            Pattern ID
        
        #AFTERMATH_PATTERN_IDENTIFIED: pattern_recording
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Get or create pattern
            cursor.execute(
                "SELECT pattern_id FROM patterns WHERE pattern_name = ?",
                (pattern_name,)
            )
            row = cursor.fetchone()
            
            if row:
                pattern_id = row["pattern_id"]
                # Update occurrence count and last_seen
                cursor.execute("""
                    UPDATE patterns 
                    SET occurrences = occurrences + 1, 
                        last_seen = ?
                    WHERE pattern_id = ?
                """, (datetime.now().isoformat(), pattern_id))
            else:
                # Create new pattern
                cursor.execute("""
                    INSERT INTO patterns 
                    (pattern_name, pattern_type, description, occurrences)
                    VALUES (?, ?, ?, 1)
                """, (pattern_name, pattern_type, description))
                pattern_id = cursor.lastrowid
            
            # Record occurrence
            cursor.execute("""
                INSERT INTO pattern_occurrences 
                (pattern_id, session_id, context)
                VALUES (?, ?, ?)
            """, (pattern_id, session_id, json.dumps(context) if context else None))
            
            return pattern_id
    
    def record_lesson(
        self,
        session_id: str,
        lesson_text: str,
        category: Optional[str] = None,
        confidence: float = 0.8
    ) -> int:
        """
        Record a lesson learned.
        
        Args:
            session_id: Current session ID
            lesson_text: Lesson description
            category: Lesson category
            confidence: Confidence score (0.0-1.0)
        
        Returns:
            Lesson ID
        
        #AFTERMATH_LESSON_LEARNED: lessons_stored_in_brain
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO lessons 
                (session_id, lesson_text, category, confidence)
                VALUES (?, ?, ?, ?)
            """, (session_id, lesson_text, category, confidence))
            return cursor.lastrowid
    
    def record_decision(
        self,
        session_id: str,
        context: Dict[str, Any],
        decision: Dict[str, Any],
        rationale: Optional[str] = None,
        outcome: Optional[Dict[str, Any]] = None,
        success: Optional[bool] = None
    ) -> int:
        """
        Record a decision and its outcome.
        
        Args:
            session_id: Current session ID
            context: Decision context
            decision: Decision made
            rationale: Reasoning for decision
            outcome: Decision outcome
            success: Whether decision was successful
        
        Returns:
            Decision ID
        
        #AFTERMATH_DECISION_RATIONALE: decisions_tracked_for_learning
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO decisions 
                (session_id, context, decision, rationale, outcome, success)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                session_id,
                json.dumps(context),
                json.dumps(decision),
                rationale,
                json.dumps(outcome) if outcome else None,
                success
            ))
            return cursor.lastrowid
    
    def get_similar_patterns(
        self, 
        pattern_name: str, 
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get similar patterns by name matching.
        
        Args:
            pattern_name: Pattern to search for
            limit: Maximum results
        
        Returns:
            List of pattern dictionaries
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT pattern_name, pattern_type, description, 
                       occurrences, confidence_score, last_seen
                FROM patterns
                WHERE pattern_name LIKE ?
                ORDER BY occurrences DESC
                LIMIT ?
            """, (f"%{pattern_name}%", limit))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def get_recent_lessons(
        self, 
        category: Optional[str] = None, 
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get recent lessons learned.
        
        Args:
            category: Filter by category (optional)
            limit: Maximum results
        
        Returns:
            List of lesson dictionaries
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            if category:
                cursor.execute("""
                    SELECT lesson_text, category, confidence, timestamp
                    FROM lessons
                    WHERE category = ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                """, (category, limit))
            else:
                cursor.execute("""
                    SELECT lesson_text, category, confidence, timestamp
                    FROM lessons
                    ORDER BY timestamp DESC
                    LIMIT ?
                """, (limit,))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def get_session_history(
        self, 
        agent_name: Optional[str] = None, 
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get session history.
        
        Args:
            agent_name: Filter by agent name (optional)
            limit: Maximum results
        
        Returns:
            List of session dictionaries
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            if agent_name:
                cursor.execute("""
                    SELECT session_id, agent_name, agent_version, 
                           start_time, end_time, status, task_type, metrics
                    FROM sessions
                    WHERE agent_name = ?
                    ORDER BY start_time DESC
                    LIMIT ?
                """, (agent_name, limit))
            else:
                cursor.execute("""
                    SELECT session_id, agent_name, agent_version, 
                           start_time, end_time, status, task_type, metrics
                    FROM sessions
                    ORDER BY start_time DESC
                    LIMIT ?
                """, (limit,))
            
            results = []
            for row in cursor.fetchall():
                result = dict(row)
                if result["metrics"]:
                    result["metrics"] = json.loads(result["metrics"])
                results.append(result)
            
            return results
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get cognitive brain statistics.
        
        Returns:
            Dictionary with counts and metrics
        
        #AFTERMATH_METRIC: cognitive_brain_stats
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) as count FROM sessions")
            total_sessions = cursor.fetchone()["count"]
            
            cursor.execute("SELECT COUNT(*) as count FROM patterns")
            total_patterns = cursor.fetchone()["count"]
            
            cursor.execute("SELECT COUNT(*) as count FROM lessons")
            total_lessons = cursor.fetchone()["count"]
            
            cursor.execute("SELECT COUNT(*) as count FROM decisions")
            total_decisions = cursor.fetchone()["count"]
            
            cursor.execute("""
                SELECT pattern_name, occurrences 
                FROM patterns 
                ORDER BY occurrences DESC 
                LIMIT 5
            """)
            top_patterns = [dict(row) for row in cursor.fetchall()]
            
            return {
                "total_sessions": total_sessions,
                "total_patterns": total_patterns,
                "total_lessons": total_lessons,
                "total_decisions": total_decisions,
                "top_patterns": top_patterns,
                "database_path": str(self.db_path)
            }
