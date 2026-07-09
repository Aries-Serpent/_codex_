"""
PatternEventRecorder: Pattern and event recording operations.

Provides:
- Pattern recording for sessions
- Event logging and tracking
- Pattern success tracking
- Event type validation
"""

from typing import Optional

from .session_database import SessionDatabase


class PatternEventRecorder:
    """
    Records patterns and events associated with sessions.

    Provides:
    - Add pattern records to sessions
    - Log events with optional details
    - Validate pattern and event types
    - Maintain session activity history
    """

    def __init__(self, db: SessionDatabase) -> None:
        """
        Initialize recorder with database instance.

        Args:
            db: SessionDatabase instance for writing patterns and events
        """
        self.db = db

    def add_pattern_to_session(
        self, session_id: str, pattern_id: str, pattern_name: str, success: bool = True
    ) -> bool:
        """
        Add a pattern record to a session.

        Args:
            session_id: Session identifier
            pattern_id: Pattern identifier
            pattern_name: Human-readable pattern name
            success: Whether pattern was successfully applied

        Returns:
            True if added successfully.
        """
        self.db._invalidate_cache()

        with self.db._lock:
            with self.db._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO session_patterns (session_id, pattern_id, pattern_name, success)
                    VALUES (?, ?, ?, ?)
                    """,
                    (session_id, pattern_id, pattern_name, success),
                )
                conn.commit()
                return cursor.rowcount > 0

    def add_event_to_session(
        self, session_id: str, event_type: str, event_details: Optional[str] = None
    ) -> bool:
        """
        Add an event record to a session.

        Args:
            session_id: Session identifier
            event_type: Type of event ('start', 'pattern_applied', 'check_passed', 'check_failed', 'error', 'complete')
            event_details: Optional detailed information about event

        Returns:
            True if added successfully.

        Raises:
            ValueError: If event_type invalid.
        """  # noqa: E501
        valid_types = {
            "start",
            "pattern_applied",
            "check_passed",
            "check_failed",
            "error",
            "complete",
        }
        if event_type not in valid_types:
            raise ValueError(f"Invalid event_type: {event_type}")

        self.db._invalidate_cache()

        with self.db._lock:
            with self.db._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO session_events (session_id, event_type, event_details)
                    VALUES (?, ?, ?)
                    """,
                    (session_id, event_type, event_details),
                )
                conn.commit()
                return cursor.rowcount > 0
