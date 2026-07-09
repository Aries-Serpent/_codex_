"""
SessionAnalytics: Analytics, statistics, and reporting operations.

Provides:
- Aggregated session statistics
- Status distribution analysis
- Agent performance metrics
- Branch activity metrics
- Success rate calculations
"""

import time
from datetime import datetime, timedelta
from typing import Any

from .session_database import CacheEntry, SessionDatabase


class SessionAnalytics:
    """
    Analytics and statistics for session data.

    Provides:
    - Aggregated statistics over time ranges
    - Distribution analysis by status, agent, branch
    - Success rate calculations
    - Result caching with configurable TTL
    """

    def __init__(self, db: SessionDatabase) -> None:
        """
        Initialize analytics with database instance.

        Args:
            db: SessionDatabase instance for querying
        """
        self.db = db

    def get_stats(self, timeframe: str = "7d") -> dict[str, Any]:
        """
        Get aggregated statistics for sessions.

        Args:
            timeframe: Time period ('24h', '7d', '30d', 'all')

        Returns:
            Dictionary with statistics:
            {
                'total': int,
                'by_status': {'pending': int, ...},
                'by_agent': {'agent_name': int, ...},
                'by_branch': {'branch': int, ...},
                'success_rate': float
            }
        """
        cache_key = f"stats_{timeframe}"

        with self.db._lock:
            if cache_key in self.db._cache:
                entry = self.db._cache[cache_key]
                if not entry.is_expired(self.db._cache_ttl):
                    return entry.data

        # Calculate time filter
        now = datetime.utcnow()
        if timeframe == "24h":
            start_time = now - timedelta(hours=24)
        elif timeframe == "7d":
            start_time = now - timedelta(days=7)
        elif timeframe == "30d":
            start_time = now - timedelta(days=30)
        else:
            start_time = datetime.min

        start_str = start_time.isoformat() + "Z" if timeframe != "all" else None

        with self.db._lock:
            with self.db._get_connection() as conn:
                cursor = conn.cursor()

                # Total sessions
                if start_str:
                    cursor.execute(
                        "SELECT COUNT(*) FROM sessions WHERE timestamp >= ?",
                        (start_str,),
                    )
                else:
                    cursor.execute("SELECT COUNT(*) FROM sessions")
                total = cursor.fetchone()[0]

                # By status
                if start_str:
                    cursor.execute(
                        "SELECT status, COUNT(*) FROM sessions WHERE timestamp >= ? GROUP BY status",  # noqa: E501
                        (start_str,),
                    )
                else:
                    cursor.execute("SELECT status, COUNT(*) FROM sessions GROUP BY status")
                by_status = {row[0]: row[1] for row in cursor.fetchall()}

                # By agent
                if start_str:
                    cursor.execute(
                        "SELECT agent_name, COUNT(*) FROM sessions WHERE timestamp >= ? GROUP BY agent_name",  # noqa: E501
                        (start_str,),
                    )
                else:
                    cursor.execute("SELECT agent_name, COUNT(*) FROM sessions GROUP BY agent_name")
                by_agent = {row[0]: row[1] for row in cursor.fetchall() if row[0]}

                # By branch
                if start_str:
                    cursor.execute(
                        "SELECT branch, COUNT(*) FROM sessions WHERE timestamp >= ? GROUP BY branch",  # noqa: E501
                        (start_str,),
                    )
                else:
                    cursor.execute("SELECT branch, COUNT(*) FROM sessions GROUP BY branch")
                by_branch = {row[0]: row[1] for row in cursor.fetchall() if row[0]}

                # Success rate (complete / total)
                completed = by_status.get("complete", 0)
                success_rate = (completed / total * 100) if total > 0 else 0.0

            stats = {
                "total": total,
                "by_status": by_status,
                "by_agent": by_agent,
                "by_branch": by_branch,
                "success_rate": round(success_rate, 2),
                "timeframe": timeframe,
            }

            self.db._cache[cache_key] = CacheEntry(stats, time.time())

        return stats
