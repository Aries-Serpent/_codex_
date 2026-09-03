"""
Metrics Collection System

This module provides metrics collection and reporting for the reviewer agent,
tracking review performance, suggestion acceptance, and learning progress.
"""

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class ReviewMetrics:
    """Metrics for a single review."""
    pr_number: int
    repo: str
    timestamp: datetime
    review_time_seconds: float
    confidence: float
    status: str
    suggestions_count: int
    knowledge_gaps_count: int
    files_changed: int


@dataclass
class AggregateMetrics:
    """Aggregate metrics over a time period."""
    total_reviews: int = 0
    average_review_time: float = 0.0
    average_confidence: float = 0.0
    average_suggestions: float = 0.0
    status_distribution: dict[str, int] = field(default_factory=dict)
    review_accuracy_rate: float = 0.0
    suggestion_acceptance_rate: float = 0.0
    knowledge_gaps_identified: int = 0

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "total_reviews": self.total_reviews,
            "average_review_time": round(self.average_review_time, 2),
            "average_confidence": round(self.average_confidence, 3),
            "average_suggestions": round(self.average_suggestions, 1),
            "status_distribution": self.status_distribution,
            "review_accuracy_rate": round(self.review_accuracy_rate, 3),
            "suggestion_acceptance_rate": round(self.suggestion_acceptance_rate, 3),
            "knowledge_gaps_identified": self.knowledge_gaps_identified,
        }


class MetricsCollector:
    """
    Collects and aggregates metrics for the reviewer agent.

    Provides methods for recording review metrics, calculating aggregates,
    and generating reports for monitoring dashboards.

    Implements buffering for better I/O performance.
    """

    def __init__(self, storage_path: Optional[Path] = None, buffer_size: int = 10):
        """
        Initialize metrics collector.

        Args:
            storage_path: Path to store metrics data (default: .codex/agent-metrics/)
            buffer_size: Number of records to buffer before writing (default: 10)
        """
        self.storage_path = storage_path or Path(".codex/agent-metrics")
        self.storage_path.mkdir(parents=True, exist_ok=True)

        self.metrics_file = self.storage_path / "reviews.jsonl"
        self.feedback_file = self.storage_path / "feedback.jsonl"

        # Buffering for performance
        self.buffer_size = buffer_size
        self._metrics_buffer: list[dict] = []
        self._feedback_buffer: list[dict] = []

    def _flush_metrics(self):
        """Flush metrics buffer to disk."""
        if not self._metrics_buffer:
            return

        with open(self.metrics_file, 'a', encoding='utf-8') as f:
            for record in self._metrics_buffer:
                f.write(json.dumps(record) + '\n')

        logger.info(f"Flushed {len(self._metrics_buffer)} metrics records")  # codeql[py/clear-text-logging-sensitive-data]
        self._metrics_buffer.clear()

    def _flush_feedback(self):
        """Flush feedback buffer to disk."""
        if not self._feedback_buffer:
            return

        with open(self.feedback_file, 'a', encoding='utf-8') as f:
            for record in self._feedback_buffer:
                f.write(json.dumps(record) + '\n')

        logger.info(f"Flushed {len(self._feedback_buffer)} feedback records")  # codeql[py/clear-text-logging-sensitive-data]
        self._feedback_buffer.clear()

    def record_review(self, metrics: ReviewMetrics, flush_immediately: bool = False):
        """
        Record metrics for a completed review.

        Args:
            metrics: Review metrics to record
            flush_immediately: If True, bypass buffering and write immediately
        """
        record = {
            "pr_number": metrics.pr_number,
            "repo": metrics.repo,
            "timestamp": metrics.timestamp.isoformat(),
            "review_time_seconds": metrics.review_time_seconds,
            "confidence": metrics.confidence,
            "status": metrics.status,
            "suggestions_count": metrics.suggestions_count,
            "knowledge_gaps_count": metrics.knowledge_gaps_count,
            "files_changed": metrics.files_changed,
        }

        self._metrics_buffer.append(record)

        if flush_immediately or len(self._metrics_buffer) >= self.buffer_size:
            self._flush_metrics()

        logger.info(f"Recorded metrics for PR #{metrics.pr_number}")  # codeql[py/clear-text-logging-sensitive-data]

    def record_feedback(self, pr_number: int, feedback: dict, flush_immediately: bool = False):
        """
        Record feedback for a review.

        Args:
            pr_number: PR number
            feedback: Feedback data (accepted/rejected suggestions, etc.)
            flush_immediately: If True, bypass buffering and write immediately
        """
        record = {
            "pr_number": pr_number,
            "timestamp": datetime.utcnow().isoformat(),
            "feedback": feedback,
        }

        self._feedback_buffer.append(record)

        if flush_immediately or len(self._feedback_buffer) >= self.buffer_size:
            self._flush_feedback()

        logger.info(f"Recorded feedback for PR #{pr_number}")  # codeql[py/clear-text-logging-sensitive-data]

    def flush_all(self):
        """Flush all buffers to disk."""
        self._flush_metrics()
        self._flush_feedback()

    def close(self):
        """Explicit lifecycle hook for buffered metrics cleanup."""
        self.flush_all()

    def get_recent_metrics(self, days: int = 30) -> list[ReviewMetrics]:
        """
        Get metrics for recent reviews.

        Args:
            days: Number of days to look back

        Returns:
            List of review metrics
        """
        if not self.metrics_file.exists():
            return []

        cutoff = datetime.utcnow() - timedelta(days=days)
        metrics = []

        with open(self.metrics_file, 'r', encoding='utf-8') as f:
            for line in f:
                record = json.loads(line)
                timestamp = datetime.fromisoformat(record["timestamp"])

                if timestamp >= cutoff:
                    metrics.append(ReviewMetrics(
                        pr_number=record["pr_number"],
                        repo=record["repo"],
                        timestamp=timestamp,
                        review_time_seconds=record["review_time_seconds"],
                        confidence=record["confidence"],
                        status=record["status"],
                        suggestions_count=record["suggestions_count"],
                        knowledge_gaps_count=record["knowledge_gaps_count"],
                        files_changed=record["files_changed"],
                    ))

        return metrics

    def calculate_aggregates(self, days: int = 30) -> AggregateMetrics:
        """
        Calculate aggregate metrics.

        Args:
            days: Number of days to aggregate over

        Returns:
            Aggregate metrics
        """
        metrics = self.get_recent_metrics(days)

        if not metrics:
            return AggregateMetrics()

        total = len(metrics)
        avg_time = sum(m.review_time_seconds for m in metrics) / total
        avg_confidence = sum(m.confidence for m in metrics) / total
        avg_suggestions = sum(m.suggestions_count for m in metrics) / total

        # Status distribution
        status_dist = {}
        for m in metrics:
            status_dist[m.status] = status_dist.get(m.status, 0) + 1

        # Knowledge gaps
        total_gaps = sum(m.knowledge_gaps_count for m in metrics)

        # Calculate acceptance rate from feedback
        acceptance_rate = self._calculate_acceptance_rate(days)

        return AggregateMetrics(
            total_reviews=total,
            average_review_time=avg_time,
            average_confidence=avg_confidence,
            average_suggestions=avg_suggestions,
            status_distribution=status_dist,
            review_accuracy_rate=avg_confidence,  # Simplified estimate
            suggestion_acceptance_rate=acceptance_rate,
            knowledge_gaps_identified=total_gaps,
        )

    def _calculate_acceptance_rate(self, days: int) -> float:
        """Calculate suggestion acceptance rate from feedback."""
        if not self.feedback_file.exists():
            return 0.0

        cutoff = datetime.utcnow() - timedelta(days=days)
        total_suggestions = 0
        accepted_suggestions = 0

        with open(self.feedback_file, 'r', encoding='utf-8') as f:
            for line in f:
                record = json.loads(line)
                timestamp = datetime.fromisoformat(record["timestamp"])

                if timestamp >= cutoff:
                    feedback = record["feedback"]
                    accepted = len(feedback.get("accepted_suggestions", []))
                    rejected = len(feedback.get("rejected_suggestions", []))

                    total_suggestions += accepted + rejected
                    accepted_suggestions += accepted

        if total_suggestions == 0:
            return 0.0

        return accepted_suggestions / total_suggestions

    def generate_report(self, days: int = 30) -> str:
        """
        Generate markdown report of metrics.

        Args:
            days: Number of days to report on

        Returns:
            Markdown formatted report
        """
        aggregates = self.calculate_aggregates(days)
        recent_metrics = self.get_recent_metrics(days=7)  # Last week for trend

        report = []
        report.append("# Codex Quantum Reviewer - Metrics Report")
        report.append(f"**Period**: Last {days} days")
        report.append(f"**Generated**: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC\n")

        report.append("## Summary Statistics\n")
        report.append(f"- **Total Reviews**: {aggregates.total_reviews}")
        report.append(f"- **Average Review Time**: {aggregates.average_review_time:.1f}s")
        report.append(f"- **Average Confidence**: {aggregates.average_confidence:.1%}")
        report.append(f"- **Average Suggestions**: {aggregates.average_suggestions:.1f}")
        report.append(f"- **Suggestion Acceptance Rate**: {aggregates.suggestion_acceptance_rate:.1%}")
        report.append(f"- **Knowledge Gaps Identified**: {aggregates.knowledge_gaps_identified}\n")

        report.append("## Review Status Distribution\n")
        for status, count in sorted(aggregates.status_distribution.items()):
            percentage = (count / aggregates.total_reviews) * 100
            report.append(f"- **{status}**: {count} ({percentage:.1f}%)")

        report.append("\n## Recent Activity (Last 7 Days)\n")
        if recent_metrics:
            report.append(f"- Reviews: {len(recent_metrics)}")
            avg_conf_recent = sum(m.confidence for m in recent_metrics) / len(recent_metrics)
            report.append(f"- Average Confidence: {avg_conf_recent:.1%}")
        else:
            report.append("- No recent activity")

        report.append("\n## Performance Trends\n")
        report.append("*Trend analysis requires at least 14 days of data*\n")

        return "\n".join(report)

    def export_metrics(self, output_path: Path):
        """
        Export metrics to JSON file.

        Args:
            output_path: Path to write JSON export
        """
        aggregates = self.calculate_aggregates(days=90)  # 90-day export

        export_data = {
            "generated_at": datetime.utcnow().isoformat(),
            "period_days": 90,
            "metrics": aggregates.to_dict(),
        }

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2)

        logger.info(f"Exported metrics to {output_path}")  # codeql[py/clear-text-logging-sensitive-data]
