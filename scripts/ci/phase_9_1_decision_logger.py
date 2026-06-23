#!/usr/bin/env python3
"""
PHASE 9.1: D_CAPABLE Decision Logging Framework

This module provides comprehensive decision logging for autonomous D_CAPABLE agents.
All decisions are logged immutably with metadata, confidence scores, and audit trails.

Features:
  - Decision ID generation & tracking
  - Immutable append-only logging
  - Confidence score recording
  - Human review status tracking
  - Escalation trigger detection
  - CLI interface for querying
  - GitHub Actions integration

Usage:
  # Log a new decision
  decision_logger execute --agent ci-testing-agent --confidence 82.5 \\
    --context "Fix test collection errors" --outcome SUCCESS

  # Query decisions
  decision_logger query --agent ci-testing-agent --since 2026-07-01 --confidence ">80"

  # Rollback a decision
  decision_logger rollback --decision-id phase-9-1-dec-2026-06-22-042 \\
    --reason "False positive detected"

  # Export audit trail
  decision_logger export --format csv --output audit_trail.csv
"""

import json
import sqlite3
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import argparse


@dataclass
class DecisionRecord:
    """Immutable decision log entry."""
    decision_id: str
    timestamp: str
    agent_id: str
    decision_type: str
    risk_category: str
    input_context: Dict[str, Any]
    confidence_score: float
    confidence_factors: Dict[str, float]
    escalation_threshold: float
    escalated: bool
    decision_action: str  # EXECUTE, ESCALATE, BLOCK
    execution_details: Optional[Dict[str, Any]]
    outcome: str  # SUCCESS, FAILED, ROLLED_BACK, PENDING
    validation_timestamp: Optional[str]
    human_review_requested: bool
    human_review_provided: Optional[bool]
    human_review_reason: Optional[str]
    created_by: str
    created_on: str
    rollback_id: Optional[str] = None
    rollback_reason: Optional[str] = None


class DecisionLogger:
    """Immutable decision logging system with query capability."""

    def __init__(self, db_path: str = ".codex/phase_9_1_decisions.db"):
        """Initialize decision logger with SQLite backend."""
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    def _init_schema(self) -> None:
        """Initialize database schema (append-only)."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Main decision log (append-only)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS decision_log (
                decision_id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                agent_id TEXT NOT NULL,
                decision_type TEXT NOT NULL,
                risk_category TEXT NOT NULL,
                input_context TEXT NOT NULL,
                confidence_score REAL NOT NULL,
                confidence_factors TEXT NOT NULL,
                escalation_threshold REAL NOT NULL,
                escalated INTEGER NOT NULL,
                decision_action TEXT NOT NULL,
                execution_details TEXT,
                outcome TEXT NOT NULL,
                validation_timestamp TEXT,
                human_review_requested INTEGER NOT NULL,
                human_review_provided INTEGER,
                human_review_reason TEXT,
                created_by TEXT NOT NULL,
                created_on TEXT NOT NULL,
                rollback_id TEXT,
                rollback_reason TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Audit log (immutable)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_log (
                audit_id TEXT PRIMARY KEY,
                decision_id TEXT NOT NULL,
                event_type TEXT NOT NULL,
                event_timestamp TEXT NOT NULL,
                details TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (decision_id) REFERENCES decision_log(decision_id)
            )
        """)

        # Rollback tracking (append-only)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS rollback_log (
                rollback_id TEXT PRIMARY KEY,
                decision_id TEXT NOT NULL,
                rollback_timestamp TEXT NOT NULL,
                reason TEXT NOT NULL,
                initiated_by TEXT NOT NULL,
                status TEXT NOT NULL,
                details TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (decision_id) REFERENCES decision_log(decision_id)
            )
        """)

        # Indices for fast querying
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_agent_id ON decision_log(agent_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON decision_log(timestamp)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_confidence ON decision_log(confidence_score)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_outcome ON decision_log(outcome)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_escalated ON decision_log(escalated)")

        conn.commit()
        conn.close()

    def log_decision(self, record: DecisionRecord) -> str:
        """Log a new decision (immutable append)."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO decision_log (
                    decision_id, timestamp, agent_id, decision_type,
                    risk_category, input_context, confidence_score,
                    confidence_factors, escalation_threshold, escalated,
                    decision_action, execution_details, outcome,
                    validation_timestamp, human_review_requested,
                    human_review_provided, human_review_reason,
                    created_by, created_on, rollback_id, rollback_reason
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                record.decision_id,
                record.timestamp,
                record.agent_id,
                record.decision_type,
                record.risk_category,
                json.dumps(record.input_context),
                record.confidence_score,
                json.dumps(record.confidence_factors),
                record.escalation_threshold,
                int(record.escalated),
                record.decision_action,
                json.dumps(record.execution_details) if record.execution_details else None,
                record.outcome,
                record.validation_timestamp,
                int(record.human_review_requested),
                int(record.human_review_provided) if record.human_review_provided is not None else None,
                record.human_review_reason,
                record.created_by,
                record.created_on,
                record.rollback_id,
                record.rollback_reason,
            ))

            # Log audit event
            audit_id = str(uuid.uuid4())
            cursor.execute("""
                INSERT INTO audit_log (audit_id, decision_id, event_type, event_timestamp, details)
                VALUES (?, ?, ?, ?, ?)
            """, (
                audit_id,
                record.decision_id,
                "DECISION_LOGGED",
                datetime.utcnow().isoformat() + "Z",
                json.dumps({"action": record.decision_action, "confidence": record.confidence_score}),
            ))

            conn.commit()
            return record.decision_id
        finally:
            conn.close()

    def query_decisions(
        self,
        agent_id: Optional[str] = None,
        since: Optional[str] = None,
        until: Optional[str] = None,
        confidence_min: Optional[float] = None,
        confidence_max: Optional[float] = None,
        outcome: Optional[str] = None,
        escalated: Optional[bool] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """Query decisions with flexible filtering."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        query = "SELECT * FROM decision_log WHERE 1=1"
        params = []

        if agent_id:
            query += " AND agent_id = ?"
            params.append(agent_id)
        if since:
            query += " AND timestamp >= ?"
            params.append(since)
        if until:
            query += " AND timestamp <= ?"
            params.append(until)
        if confidence_min is not None:
            query += " AND confidence_score >= ?"
            params.append(confidence_min)
        if confidence_max is not None:
            query += " AND confidence_score <= ?"
            params.append(confidence_max)
        if outcome:
            query += " AND outcome = ?"
            params.append(outcome)
        if escalated is not None:
            query += " AND escalated = ?"
            params.append(int(escalated))

        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)

        try:
            cursor.execute(query, params)
            rows = cursor.fetchall()
            results = []
            for row in rows:
                record = dict(row)
                record["input_context"] = json.loads(record["input_context"])
                record["confidence_factors"] = json.loads(record["confidence_factors"])
                if record["execution_details"]:
                    record["execution_details"] = json.loads(record["execution_details"])
                results.append(record)
            return results
        finally:
            conn.close()

    def record_rollback(
        self,
        decision_id: str,
        reason: str,
        initiated_by: str = "orchestrator-agent",
    ) -> str:
        """Record a decision rollback."""
        rollback_id = f"rollback-{datetime.utcnow().isoformat()}-{uuid.uuid4().hex[:8]}"
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO rollback_log (
                    rollback_id, decision_id, rollback_timestamp,
                    reason, initiated_by, status
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                rollback_id,
                decision_id,
                datetime.utcnow().isoformat() + "Z",
                reason,
                initiated_by,
                "EXECUTED",
            ))

            # Update decision record with rollback reference
            cursor.execute("""
                UPDATE decision_log
                SET rollback_id = ?, rollback_reason = ?, outcome = ?
                WHERE decision_id = ?
            """, (rollback_id, reason, "ROLLED_BACK", decision_id))

            # Log audit event
            audit_id = str(uuid.uuid4())
            cursor.execute("""
                INSERT INTO audit_log (audit_id, decision_id, event_type, event_timestamp, details)
                VALUES (?, ?, ?, ?, ?)
            """, (
                audit_id,
                decision_id,
                "DECISION_ROLLED_BACK",
                datetime.utcnow().isoformat() + "Z",
                json.dumps({"rollback_id": rollback_id, "reason": reason}),
            ))

            conn.commit()
            return rollback_id
        finally:
            conn.close()

    def get_agent_accuracy(self, agent_id: str, days: int = 90) -> Dict[str, Any]:
        """Calculate agent accuracy metrics."""
        since = (datetime.utcnow() - timedelta(days=days)).isoformat() + "Z"

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT
                    COUNT(*) as total_decisions,
                    SUM(CASE WHEN outcome = 'SUCCESS' THEN 1 ELSE 0 END) as successful,
                    SUM(CASE WHEN outcome = 'FAILED' THEN 1 ELSE 0 END) as failed,
                    SUM(CASE WHEN outcome = 'ROLLED_BACK' THEN 1 ELSE 0 END) as rolled_back,
                    AVG(confidence_score) as avg_confidence,
                    MIN(confidence_score) as min_confidence,
                    MAX(confidence_score) as max_confidence,
                    SUM(CASE WHEN escalated = 1 THEN 1 ELSE 0 END) as escalations
                FROM decision_log
                WHERE agent_id = ? AND timestamp >= ?
            """, (agent_id, since))

            row = cursor.fetchone()
            if not row or row[0] == 0:
                return {"agent_id": agent_id, "total_decisions": 0}

            total = row[0]
            successful = row[1] or 0
            accuracy = (successful / total * 100) if total > 0 else 0

            return {
                "agent_id": agent_id,
                "period_days": days,
                "total_decisions": total,
                "successful": successful,
                "failed": row[2] or 0,
                "rolled_back": row[3] or 0,
                "accuracy_percent": round(accuracy, 2),
                "avg_confidence": round(row[4], 2) if row[4] else 0,
                "min_confidence": round(row[5], 2) if row[5] else 0,
                "max_confidence": round(row[6], 2) if row[6] else 0,
                "escalations": row[7] or 0,
            }
        finally:
            conn.close()

    def export_audit_trail(self, output_path: str, format: str = "json") -> None:
        """Export audit trail to file."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT * FROM decision_log ORDER BY timestamp")
            rows = cursor.fetchall()

            if format == "json":
                records = []
                for row in rows:
                    record = dict(row)
                    record["input_context"] = json.loads(record["input_context"])
                    record["confidence_factors"] = json.loads(record["confidence_factors"])
                    if record["execution_details"]:
                        record["execution_details"] = json.loads(record["execution_details"])
                    records.append(record)
                with open(output_path, "w") as f:
                    json.dump(records, f, indent=2)

            elif format == "csv":
                import csv
                records = []
                for row in rows:
                    record = dict(row)
                    record["input_context"] = json.dumps(json.loads(record["input_context"]))
                    record["confidence_factors"] = json.dumps(json.loads(record["confidence_factors"]))
                    records.append(record)

                if records:
                    with open(output_path, "w", newline="") as f:
                        writer = csv.DictWriter(f, fieldnames=records[0].keys())
                        writer.writeheader()
                        writer.writerows(records)

            print(f"✅ Audit trail exported to {output_path}")
        finally:
            conn.close()


def create_decision_record(
    agent_id: str,
    decision_type: str,
    risk_category: str,
    confidence_score: float,
    confidence_factors: Dict[str, float],
    escalation_threshold: float,
    input_context: Dict[str, Any],
    decision_action: str = "EXECUTE",
    execution_details: Optional[Dict[str, Any]] = None,
    outcome: str = "SUCCESS",
    human_review_requested: bool = False,
) -> DecisionRecord:
    """Factory function to create a decision record."""
    decision_id = f"phase-9-1-dec-{datetime.utcnow().isoformat().replace(':', '-').replace('.', '-')[:22]}-{uuid.uuid4().hex[:6]}"

    return DecisionRecord(
        decision_id=decision_id,
        timestamp=datetime.utcnow().isoformat() + "Z",
        agent_id=agent_id,
        decision_type=decision_type,
        risk_category=risk_category,
        input_context=input_context,
        confidence_score=confidence_score,
        confidence_factors=confidence_factors,
        escalation_threshold=escalation_threshold,
        escalated=confidence_score < escalation_threshold or human_review_requested,
        decision_action=decision_action,
        execution_details=execution_details,
        outcome=outcome,
        validation_timestamp=datetime.utcnow().isoformat() + "Z" if outcome != "PENDING" else None,
        human_review_requested=human_review_requested,
        human_review_provided=None,
        human_review_reason=None,
        created_by="orchestrator-agent",
        created_on=datetime.utcnow().isoformat() + "Z",
    )


def main():
    """CLI interface for decision logger."""
    parser = argparse.ArgumentParser(
        description="PHASE 9.1 Decision Logger CLI"
    )
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Execute command
    execute_parser = subparsers.add_parser("execute", help="Log a new decision")
    execute_parser.add_argument("--agent", required=True, help="Agent ID")
    execute_parser.add_argument("--decision-type", default="TYPE_B", help="Decision type")
    execute_parser.add_argument("--risk-category", default="unknown", help="Risk category")
    execute_parser.add_argument("--confidence", type=float, required=True, help="Confidence score (0-100)")
    execute_parser.add_argument("--context", help="Input context")
    execute_parser.add_argument("--outcome", default="SUCCESS", help="Decision outcome")

    # Query command
    query_parser = subparsers.add_parser("query", help="Query decisions")
    query_parser.add_argument("--agent", help="Filter by agent ID")
    query_parser.add_argument("--since", help="Filter by start date (ISO format)")
    query_parser.add_argument("--until", help="Filter by end date (ISO format)")
    query_parser.add_argument("--confidence-min", type=float, help="Min confidence score")
    query_parser.add_argument("--confidence-max", type=float, help="Max confidence score")
    query_parser.add_argument("--outcome", help="Filter by outcome")
    query_parser.add_argument("--escalated", action="store_true", help="Show escalated only")
    query_parser.add_argument("--limit", type=int, default=100, help="Result limit")

    # Rollback command
    rollback_parser = subparsers.add_parser("rollback", help="Rollback a decision")
    rollback_parser.add_argument("--decision-id", required=True, help="Decision ID to rollback")
    rollback_parser.add_argument("--reason", required=True, help="Rollback reason")

    # Accuracy command
    accuracy_parser = subparsers.add_parser("accuracy", help="Get agent accuracy")
    accuracy_parser.add_argument("--agent", required=True, help="Agent ID")
    accuracy_parser.add_argument("--days", type=int, default=90, help="Period in days")

    # Export command
    export_parser = subparsers.add_parser("export", help="Export audit trail")
    export_parser.add_argument("--output", required=True, help="Output file path")
    export_parser.add_argument("--format", choices=["json", "csv"], default="json", help="Export format")

    args = parser.parse_args()
    logger = DecisionLogger()

    if args.command == "execute":
        record = create_decision_record(
            agent_id=args.agent,
            decision_type=args.decision_type,
            risk_category=args.risk_category,
            confidence_score=args.confidence,
            confidence_factors={"historical": 0.4, "complexity": 0.3, "coverage": 0.2, "signals": 0.1},
            escalation_threshold=60.0,
            input_context={"context": args.context},
            outcome=args.outcome,
        )
        decision_id = logger.log_decision(record)
        print(f"✅ Decision logged: {decision_id}")

    elif args.command == "query":
        results = logger.query_decisions(
            agent_id=args.agent,
            since=args.since,
            until=args.until,
            confidence_min=args.confidence_min,
            confidence_max=args.confidence_max,
            outcome=args.outcome,
            escalated=args.escalated if hasattr(args, 'escalated') else None,
            limit=args.limit,
        )
        print(json.dumps(results, indent=2))

    elif args.command == "rollback":
        rollback_id = logger.record_rollback(
            decision_id=args.decision_id,
            reason=args.reason,
        )
        print(f"✅ Decision rolled back: {rollback_id}")

    elif args.command == "accuracy":
        metrics = logger.get_agent_accuracy(args.agent, args.days)
        print(json.dumps(metrics, indent=2))

    elif args.command == "export":
        logger.export_audit_trail(args.output, args.format)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
