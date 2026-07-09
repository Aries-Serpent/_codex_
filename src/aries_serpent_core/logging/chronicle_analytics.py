"""
Chronicle Analytics: Session history analysis and personalized tips.

Provides:
- Session pattern detection
- Usage trend analysis
- Personalized recommendations based on user behavior
- Performance insights and improvement suggestions
"""

import json
import logging
import sqlite3
from collections import Counter, defaultdict
from datetime import datetime
from typing import Any

from .session_database import SessionDatabase

logger = logging.getLogger(__name__)


class ChronicleAnalytics:
    """
    Analyze session history and generate personalized tips.

    Analyzes user behavior patterns including:
    - Session frequency and duration
    - Tool usage patterns
    - Success/failure rates by tool
    - Time-of-day patterns
    - Agent delegation patterns
    - Error patterns and recovery strategies
    """

    def __init__(self, db: SessionDatabase) -> None:
        """Initialize chronicle analytics with database instance."""
        self.db = db
        self.sessions = []
        self._load_sessions()

    def _load_sessions(self) -> None:
        """Load all sessions from database."""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT id, created_at, status, agent_name, repository "
                    "FROM sessions ORDER BY created_at DESC"
                )
                self.sessions = [
                    {
                        "id": row[0],
                        "created_at": row[1],
                        "status": row[2],
                        "agent_name": row[3],
                        "repository": row[4],
                    }
                    for row in cursor.fetchall()
                ]
        except sqlite3.Error as exc:
            logger.warning("Failed to load chronicle sessions: %s", exc)
            self.sessions = []

    def analyze_patterns(self) -> dict[str, Any]:
        """
        Analyze all session patterns and generate insights.

        Returns:
            Dictionary containing:
            - frequency: Session frequency metrics
            - tools: Tool usage patterns
            - agents: Agent delegation patterns
            - time_patterns: Time-based activity patterns
            - performance: Success/failure metrics
            - trends: Usage trends over time
        """
        if not self.sessions:
            return {
                "frequency": {},
                "tools": {},
                "agents": {},
                "time_patterns": {},
                "performance": {},
                "trends": {},
                "insights": [],
            }

        return {
            "frequency": self._analyze_frequency(),
            "tools": self._analyze_tool_usage(),
            "agents": self._analyze_agent_usage(),
            "time_patterns": self._analyze_time_patterns(),
            "performance": self._analyze_performance(),
            "trends": self._analyze_trends(),
            "status_distribution": self._analyze_status(),
        }

    def _analyze_frequency(self) -> dict[str, Any]:
        """Analyze session frequency patterns."""
        if not self.sessions:
            return {}

        total = len(self.sessions)

        # Get date range
        dates = [
            datetime.fromisoformat(s["created_at"].replace("Z", "+00:00")).date()
            for s in self.sessions
        ]
        date_range = (min(dates), max(dates)) if dates else None

        # Sessions per day (last 7 days)
        today = datetime.utcnow().date()
        last_7_days = defaultdict(int)
        for s in self.sessions:
            try:
                session_date = datetime.fromisoformat(s["created_at"].replace("Z", "+00:00")).date()
                days_ago = (today - session_date).days
                if days_ago < 7:
                    last_7_days[f"{days_ago}d_ago"] += 1
            except (ValueError, TypeError):
                pass

        return {
            "total_sessions": total,
            "date_range": f"{date_range[0]} to {date_range[1]}" if date_range else None,
            "sessions_last_7_days": dict(sorted(last_7_days.items())),
            "avg_sessions_per_day": (
                round(
                    total / max(1, (date_range[1] - date_range[0]).days + 1),
                    2,
                )
                if date_range
                else 0
            ),
        }

    def _analyze_tool_usage(self) -> dict[str, Any]:
        """Analyze which tools are most frequently used."""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT tool_name, COUNT(*) as count "
                    "FROM tool_calls GROUP BY tool_name "
                    "ORDER BY count DESC LIMIT 10"
                )
                tools = {row[0]: row[1] for row in cursor.fetchall()}

                # Get tool success rates
                tool_stats = {}
                top_tools = list(tools.keys())[:5]
                if top_tools:
                    placeholders = ", ".join("?" for _ in top_tools)
                    cursor.execute(
                        "SELECT tool_name, COUNT(*) as total, "
                        "SUM(CASE WHEN success THEN 1 ELSE 0 END) as successful "
                        f"FROM tool_calls WHERE tool_name IN ({placeholders}) "
                        "GROUP BY tool_name",
                        top_tools,
                    )
                    for row in cursor.fetchall():
                        tool_name = row[0]
                        total_runs = row[1]
                        successful = row[2] or 0
                        if total_runs > 0:
                            success_rate = successful / total_runs
                            tool_stats[tool_name] = {
                                "usage_count": tools[tool_name],
                                "success_rate": round(success_rate * 100, 1),
                            }

                return {
                    "top_tools": tools,
                    "tool_success_rates": tool_stats,
                }
        except sqlite3.Error as exc:
            logger.warning("Failed to analyze chronicle tool usage: %s", exc)
            return {"top_tools": {}, "tool_success_rates": {}}

    def _analyze_agent_usage(self) -> dict[str, Any]:
        """Analyze agent delegation patterns."""
        agent_counter = Counter(s["agent_name"] for s in self.sessions if s["agent_name"])

        return {
            "total_agents_used": len(agent_counter),
            "top_agents": dict(agent_counter.most_common(5)),
        }

    def _analyze_time_patterns(self) -> dict[str, Any]:
        """Analyze time-based activity patterns."""
        hour_counter = Counter()
        day_counter = Counter()

        for s in self.sessions:
            try:
                dt = datetime.fromisoformat(s["created_at"].replace("Z", "+00:00"))
                hour_counter[dt.hour] += 1
                day_counter[dt.strftime("%A")] += 1
            except (ValueError, TypeError):
                pass

        return {
            "peak_hours": dict(hour_counter.most_common(3)),
            "active_days": dict(day_counter.most_common(3)),
        }

    def _analyze_performance(self) -> dict[str, Any]:
        """Analyze success/failure rates."""
        total = len(self.sessions)

        # Count by status
        status_counter = Counter(s["status"] for s in self.sessions)
        success_count = status_counter.get("completed", 0) + status_counter.get("succeeded", 0)
        failure_count = status_counter.get("failed", 0) + status_counter.get("error", 0)

        success_rate = (success_count / total * 100) if total > 0 else 0

        return {
            "total_sessions": total,
            "successful": success_count,
            "failed": failure_count,
            "success_rate": round(success_rate, 1),
            "status_breakdown": dict(status_counter),
        }

    def _analyze_trends(self) -> dict[str, Any]:
        """Analyze trends over time (increasing/decreasing usage)."""
        if len(self.sessions) < 2:
            return {"trend": "insufficient_data"}

        # Split sessions into first half and second half
        mid = len(self.sessions) // 2
        recent = self.sessions[:mid]
        older = self.sessions[mid:]

        # Dates in each period
        try:
            recent_dates = [
                datetime.fromisoformat(s["created_at"].replace("Z", "+00:00")).date()
                for s in recent
            ]
            older_dates = [
                datetime.fromisoformat(s["created_at"].replace("Z", "+00:00")).date() for s in older
            ]

            recent_range = (max(recent_dates) - min(recent_dates)).days + 1 if recent_dates else 1
            older_range = (max(older_dates) - min(older_dates)).days + 1 if older_dates else 1

            recent_per_day = len(recent) / recent_range if recent_range > 0 else 0
            older_per_day = len(older) / older_range if older_range > 0 else 0

            if older_per_day == 0:
                trend_direction = "increasing"
            else:
                change = ((recent_per_day - older_per_day) / older_per_day) * 100
                trend_direction = (
                    "increasing" if change > 10 else "decreasing" if change < -10 else "stable"
                )

            return {
                "trend": trend_direction,
                "recent_sessions_per_day": round(recent_per_day, 2),
                "older_sessions_per_day": round(older_per_day, 2),
            }
        except (ValueError, TypeError):
            return {"trend": "unknown"}

    def _analyze_status(self) -> dict[str, int]:
        """Analyze status distribution."""
        return dict(Counter(s["status"] for s in self.sessions))

    def generate_tips(self) -> list[dict[str, str]]:
        """
        Generate personalized tips based on analyzed patterns.

        Returns:
            List of tip dictionaries with category, title, and description
        """
        patterns = self.analyze_patterns()
        tips = []

        # Tip 1: Session frequency
        freq = patterns.get("frequency", {})
        avg_per_day = freq.get("avg_sessions_per_day", 0)
        if avg_per_day > 5:
            tips.append(
                {
                    "category": "productivity",
                    "title": "High Session Activity Detected",
                    "description": (
                        f"You're averaging {avg_per_day} sessions per day. Consider "
                        "using longer sessions to batch related work together and "
                        "reduce context switching overhead."
                    ),
                }
            )
        elif avg_per_day < 1:
            tips.append(
                {
                    "category": "engagement",
                    "title": "Low Session Frequency",
                    "description": (
                        "Your sessions are infrequent. Regular consistent sessions "
                        "can help build better patterns and outcomes."
                    ),
                }
            )

        # Tip 2: Tool usage patterns
        tools = patterns.get("tools", {})
        if tools.get("top_tools"):
            top_tool = list(tools["top_tools"].keys())[0]
            tool_stats = tools.get("tool_success_rates", {})
            if top_tool in tool_stats:
                success_rate = tool_stats[top_tool]["success_rate"]
                if success_rate < 70:
                    tips.append(
                        {
                            "category": "efficiency",
                            "title": f"Low Success Rate for {top_tool}",
                            "description": (
                                f"Your most-used tool '{top_tool}' has a "
                                f"{success_rate}% success rate. Review error "
                                "patterns and consider alternative approaches."
                            ),
                        }
                    )

        # Tip 3: Agent delegation
        agents = patterns.get("agents", {})
        if agents.get("total_agents_used", 0) > 1:
            tips.append(
                {
                    "category": "coordination",
                    "title": "Multi-Agent Delegation",
                    "description": (
                        f"You're using {agents['total_agents_used']} different "
                        "agents. Consider leveraging specialized agents more "
                        "(like unified-coverage-agent, ci-auto-healer-agent) "
                        "for focused work."
                    ),
                }
            )

        # Tip 4: Time patterns
        time_patterns = patterns.get("time_patterns", {})
        peak_hours = time_patterns.get("peak_hours", {})
        if peak_hours:
            peak_hour = list(peak_hours.keys())[0]
            tips.append(
                {
                    "category": "scheduling",
                    "title": "Peak Activity Hours",
                    "description": (
                        f"You're most active around {peak_hour}:00. Schedule "
                        "complex tasks during your peak hours for better "
                        "performance."
                    ),
                }
            )

        # Tip 5: Performance trend
        performance = patterns.get("performance", {})
        success_rate = performance.get("success_rate", 0)
        if success_rate > 90:
            tips.append(
                {
                    "category": "recognition",
                    "title": "Excellent Success Rate",
                    "description": (
                        f"Your sessions have a {success_rate}% success rate. "
                        "Keep up the excellent work!"
                    ),
                }
            )
        elif success_rate < 50:
            tips.append(
                {
                    "category": "improvement",
                    "title": "Session Success Rate Below 50%",
                    "description": (
                        "Consider breaking down complex tasks into smaller "
                        "sessions and using more comprehensive planning before "
                        "execution."
                    ),
                }
            )

        # Tip 6: Session duration trend
        trends = patterns.get("trends", {})
        trend = trends.get("trend", "unknown")
        if trend == "increasing":
            tips.append(
                {
                    "category": "momentum",
                    "title": "Increasing Session Activity",
                    "description": (
                        "Your session frequency is increasing. This momentum is "
                        "great - maintain consistent engagement patterns."
                    ),
                }
            )
        elif trend == "decreasing":
            tips.append(
                {
                    "category": "engagement",
                    "title": "Decreasing Session Frequency",
                    "description": (
                        "Your session frequency has been decreasing. Try to "
                        "establish a regular routine for consistent progress."
                    ),
                }
            )

        # Tip 7: Agent specialization
        top_agents = agents.get("top_agents", {})
        if not top_agents:
            tips.append(
                {
                    "category": "strategy",
                    "title": "Use Specialized Agents",
                    "description": (
                        "Consider using specialized agents like "
                        "unified-coverage-agent, ci-failure-resolution-agent, "
                        "or autonomous-test-healer-agent for focused "
                        "improvements."
                    ),
                }
            )

        return tips

    def generate_summary(self) -> str:
        """Generate a text summary of session analysis and tips."""
        patterns = self.analyze_patterns()
        tips = self.generate_tips()

        summary_lines = [
            "# 📊 Chronicle Tips Analysis\n",
            "## Session History Summary\n",
        ]

        # Frequency section
        freq = patterns.get("frequency", {})
        summary_lines.extend(
            [
                f"- **Total Sessions**: {freq.get('total_sessions', 0)}",
                f"- **Date Range**: {freq.get('date_range', 'N/A')}",
                f"- **Average Sessions/Day**: {freq.get('avg_sessions_per_day', 0)}\n",
            ]
        )

        # Performance section
        perf = patterns.get("performance", {})
        summary_lines.extend(
            [
                f"- **Success Rate**: {perf.get('success_rate', 0)}%",
                f"- **Successful**: {perf.get('successful', 0)}",
                f"- **Failed**: {perf.get('failed', 0)}\n",
            ]
        )

        # Personalized Tips section
        summary_lines.append("## 💡 Personalized Tips\n")
        if tips:
            for idx, tip in enumerate(tips, 1):
                summary_lines.extend(
                    [
                        f"### {idx}. {tip['title']}",
                        f"**Category**: {tip['category']}",
                        f"\n{tip['description']}\n",
                    ]
                )
        else:
            summary_lines.append("No specific tips at this time. Keep up the great work!\n")

        # Patterns section
        summary_lines.append("## 📈 Usage Patterns\n")

        time_patterns = patterns.get("time_patterns", {})
        if time_patterns.get("peak_hours"):
            summary_lines.append(
                "**Peak Hours**: "
                + ", ".join(
                    [f"{h}:00" for h in list(time_patterns.get("peak_hours", {}).keys())[:3]]
                )
                + "\n"
            )

        agents = patterns.get("agents", {})
        if agents.get("top_agents"):
            summary_lines.append(
                "**Top Agents**: " + ", ".join(list(agents.get("top_agents", {}).keys())[:3]) + "\n"
            )

        tools = patterns.get("tools", {})
        if tools.get("top_tools"):
            summary_lines.append(
                "**Top Tools**: " + ", ".join(list(tools.get("top_tools", {}).keys())[:3]) + "\n"
            )

        return "\n".join(summary_lines)

    def export_json(self) -> str:
        """Export analysis results as JSON."""
        return json.dumps(
            {
                "timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
                "patterns": self.analyze_patterns(),
                "tips": self.generate_tips(),
            },
            indent=2,
        )
