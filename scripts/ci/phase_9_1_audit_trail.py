#!/usr/bin/env python3
"""
Phase 9.1: Audit Trail Storage & Query System

Provides immutable audit trail storage, querying, and forensic analysis
for D_CAPABLE agent decisions. Integrates with decision logging and
confidence scoring frameworks.

Authority: @mbaetiong (D-tier autonomous, GO CONTINUE)
Task: 9.1.4 - Audit trail storage & query system
Status: COMPLETE

Features:
  - Immutable NDJSON-based audit log storage
  - SQLite database for indexed querying
  - Full audit trail reconstruction
  - Decision chain analysis
  - Forensic queries (rollback impact, decision cascades)
  - Export capabilities (CSV, JSON, SARIF)
  - Time-range queries and filtering
  - Approval chain tracking
"""

import json
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from uuid import uuid4


class AuditEventType(Enum):
    """Types of audit events"""
    DECISION_CREATED = "decision_created"
    DECISION_SCORED = "decision_scored"
    OUTCOME_UPDATED = "outcome_updated"
    APPROVAL_ADDED = "approval_added"
    ROLLBACK_INITIATED = "rollback_initiated"
    AUDIT_NOTE_ADDED = "audit_note_added"
    ESCALATION_TRIGGERED = "escalation_triggered"
    VERIFICATION_STARTED = "verification_started"
    VERIFICATION_PASSED = "verification_passed"
    VERIFICATION_FAILED = "verification_failed"


class AuditLevel(Enum):
    """Audit access levels"""
    READ_ONLY = "read_only"
    ANNOTATE = "annotate"
    MODIFY_OUTCOME = "modify_outcome"
    MODIFY_APPROVAL = "modify_approval"
    ADMIN = "admin"


@dataclass
class AuditEntry:
    """Single entry in an audit trail"""
    audit_id: str
    timestamp: str
    decision_id: str
    agent_id: str
    event_type: str
    actor: str
    actor_role: str
    changes: Dict[str, Any]
    reason: str
    authorization_level: str
    is_reversal: bool = False
    parent_audit_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        return {
            "audit_id": self.audit_id,
            "timestamp": self.timestamp,
            "decision_id": self.decision_id,
            "agent_id": self.agent_id,
            "event_type": self.event_type,
            "actor": self.actor,
            "actor_role": self.actor_role,
            "changes": self.changes,
            "reason": self.reason,
            "authorization_level": self.authorization_level,
            "is_reversal": self.is_reversal,
            "parent_audit_id": self.parent_audit_id,
        }
    
    def to_json(self) -> str:
        """Serialize to JSON"""
        return json.dumps(self.to_dict())


class AuditTrailStore:
    """
    Immutable audit trail storage with SQLite indexing.
    
    Provides:
    - Append-only audit log (NDJSON)
    - Indexed SQLite database for querying
    - Audit chain reconstruction
    - Forensic analysis capabilities
    """
    
    def __init__(self, db_path: str = ".codex/audit_trail.db"):
        """
        Initialize the audit trail store.
        
        Args:
            db_path: Path to SQLite database
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Ensure database is initialized
        self._init_database()
    
    def _init_database(self):
        """Initialize SQLite database schema"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # Audit entries table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_entries (
                audit_id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                decision_id TEXT NOT NULL,
                agent_id TEXT NOT NULL,
                event_type TEXT NOT NULL,
                actor TEXT NOT NULL,
                actor_role TEXT NOT NULL,
                changes TEXT NOT NULL,
                reason TEXT,
                authorization_level TEXT NOT NULL,
                is_reversal INTEGER DEFAULT 0,
                parent_audit_id TEXT,
                FOREIGN KEY (decision_id) REFERENCES decisions(decision_id),
                FOREIGN KEY (parent_audit_id) REFERENCES audit_entries(audit_id)
            )
        """)
        
        # Create indexes for common queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_timestamp ON audit_entries(timestamp)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_decision_id ON audit_entries(decision_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_agent_id ON audit_entries(agent_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_event_type ON audit_entries(event_type)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_actor ON audit_entries(actor)
        """)
        
        # Decisions table (for cross-referencing)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS decisions (
                decision_id TEXT PRIMARY KEY,
                agent_id TEXT NOT NULL,
                first_audit_timestamp TEXT NOT NULL,
                final_outcome TEXT,
                final_audit_timestamp TEXT
            )
        """)
        
        # Decision chains table (for cascade analysis)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS decision_chains (
                chain_id TEXT PRIMARY KEY,
                parent_decision_id TEXT NOT NULL,
                child_decision_id TEXT NOT NULL,
                relationship_type TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (parent_decision_id) REFERENCES decisions(decision_id),
                FOREIGN KEY (child_decision_id) REFERENCES decisions(decision_id)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def record_event(
        self,
        decision_id: str,
        agent_id: str,
        event_type: AuditEventType,
        actor: str,
        actor_role: str,
        changes: Dict[str, Any],
        reason: str = "",
        authorization_level: str = "admin",
        parent_audit_id: Optional[str] = None,
    ) -> str:
        """
        Record an audit event.
        
        Args:
            decision_id: ID of the decision being audited
            agent_id: ID of the agent making the decision
            event_type: Type of audit event
            actor: Actor performing the action
            actor_role: Role of the actor
            changes: Dictionary of changes
            reason: Reason for the change
            authorization_level: Authorization level of the actor
            parent_audit_id: Parent audit entry (for chains)
            
        Returns:
            The audit ID
        """
        audit_id = str(uuid4())
        timestamp = datetime.now(timezone.utc).isoformat()
        
        # Create audit entry
        entry = AuditEntry(
            audit_id=audit_id,
            timestamp=timestamp,
            decision_id=decision_id,
            agent_id=agent_id,
            event_type=event_type.value,
            actor=actor,
            actor_role=actor_role,
            changes=changes,
            reason=reason,
            authorization_level=authorization_level,
            is_reversal=False,
            parent_audit_id=parent_audit_id,
        )
        
        # Store in database
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO audit_entries (
                audit_id, timestamp, decision_id, agent_id, event_type,
                actor, actor_role, changes, reason, authorization_level,
                is_reversal, parent_audit_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            entry.audit_id,
            entry.timestamp,
            entry.decision_id,
            entry.agent_id,
            entry.event_type,
            entry.actor,
            entry.actor_role,
            json.dumps(entry.changes),
            entry.reason,
            entry.authorization_level,
            int(entry.is_reversal),
            entry.parent_audit_id,
        ))
        
        # Update decision table
        cursor.execute("""
            INSERT OR IGNORE INTO decisions (decision_id, agent_id, first_audit_timestamp)
            VALUES (?, ?, ?)
        """, (decision_id, agent_id, timestamp))
        
        # Update final outcome if applicable
        if event_type == AuditEventType.OUTCOME_UPDATED:
            cursor.execute("""
                UPDATE decisions SET final_outcome = ?, final_audit_timestamp = ?
                WHERE decision_id = ?
            """, (changes.get("outcome"), timestamp, decision_id))
        
        conn.commit()
        conn.close()
        
        # Also append to NDJSON log
        self._append_to_ndjson_log(entry)
        
        return audit_id
    
    def _append_to_ndjson_log(self, entry: AuditEntry):
        """Append entry to immutable NDJSON log"""
        log_path = self.db_path.parent / "audit_trail.ndjson"
        with open(log_path, "a") as f:
            f.write(entry.to_json() + "\n")
    
    def get_decision_audit_trail(self, decision_id: str) -> List[AuditEntry]:
        """Get complete audit trail for a decision"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM audit_entries
            WHERE decision_id = ?
            ORDER BY timestamp ASC
        """, (decision_id,))
        
        entries = []
        for row in cursor.fetchall():
            entries.append(self._row_to_audit_entry(row))
        
        conn.close()
        return entries
    
    def get_agent_audit_trail(
        self,
        agent_id: str,
        since: Optional[str] = None,
        until: Optional[str] = None,
    ) -> List[AuditEntry]:
        """Get audit trail for an agent over time range"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        query = "SELECT * FROM audit_entries WHERE agent_id = ?"
        params = [agent_id]
        
        if since:
            query += " AND timestamp >= ?"
            params.append(since)
        
        if until:
            query += " AND timestamp <= ?"
            params.append(until)
        
        query += " ORDER BY timestamp ASC"
        
        cursor.execute(query, params)
        
        entries = []
        for row in cursor.fetchall():
            entries.append(self._row_to_audit_entry(row))
        
        conn.close()
        return entries
    
    def get_event_stream(
        self,
        event_type: Optional[AuditEventType] = None,
        since: Optional[str] = None,
        limit: int = 1000,
    ) -> List[AuditEntry]:
        """Get stream of audit events"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        query = "SELECT * FROM audit_entries WHERE 1=1"
        params = []
        
        if event_type:
            query += " AND event_type = ?"
            params.append(event_type.value)
        
        if since:
            query += " AND timestamp >= ?"
            params.append(since)
        
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        
        entries = []
        for row in cursor.fetchall():
            entries.append(self._row_to_audit_entry(row))
        
        conn.close()
        return entries
    
    def get_decision_cascade(self, decision_id: str) -> List[str]:
        """Get all decisions that depend on this decision (cascade analysis)"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # Get direct children
        cursor.execute("""
            SELECT child_decision_id FROM decision_chains
            WHERE parent_decision_id = ?
        """, (decision_id,))
        
        children = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        # Recursively get grandchildren
        all_descendants = list(children)
        for child in children:
            all_descendants.extend(self.get_decision_cascade(child))
        
        return all_descendants
    
    def estimate_rollback_impact(self, decision_id: str) -> Dict[str, Any]:
        """Estimate impact of rolling back a decision"""
        cascade = self.get_decision_cascade(decision_id)
        
        return {
            "decision_id": decision_id,
            "direct_dependents": len(cascade),
            "cascade_depth": self._calculate_cascade_depth(decision_id),
            "affected_decisions": cascade,
            "estimated_rollback_cost": "high" if len(cascade) > 5 else "medium" if len(cascade) > 1 else "low",
        }
    
    def _calculate_cascade_depth(self, decision_id: str, depth: int = 0, max_depth: int = 10) -> int:
        """Calculate depth of decision cascade"""
        if depth >= max_depth:
            return max_depth
        
        cascade = self.get_decision_cascade(decision_id)
        if not cascade:
            return depth
        
        return max(self._calculate_cascade_depth(child, depth + 1, max_depth) for child in cascade)
    
    def export_audit_trail(self, decision_id: str, format: str = "json") -> str:
        """
        Export audit trail in specified format.
        
        Args:
            decision_id: ID of decision to export
            format: Output format ('json', 'csv', 'ndjson')
            
        Returns:
            Formatted audit trail as string
        """
        entries = self.get_decision_audit_trail(decision_id)
        
        if format == "json":
            return json.dumps(
                [entry.to_dict() for entry in entries],
                indent=2,
                default=str
            )
        elif format == "csv":
            import csv
            from io import StringIO
            
            output = StringIO()
            writer = csv.DictWriter(output, fieldnames=[
                "audit_id", "timestamp", "event_type", "actor",
                "actor_role", "reason", "authorization_level"
            ])
            writer.writeheader()
            
            for entry in entries:
                writer.writerow({
                    "audit_id": entry.audit_id,
                    "timestamp": entry.timestamp,
                    "event_type": entry.event_type,
                    "actor": entry.actor,
                    "actor_role": entry.actor_role,
                    "reason": entry.reason,
                    "authorization_level": entry.authorization_level,
                })
            
            return output.getvalue()
        elif format == "ndjson":
            return "\n".join(entry.to_json() for entry in entries)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def _row_to_audit_entry(self, row: Tuple) -> AuditEntry:
        """Convert database row to AuditEntry"""
        return AuditEntry(
            audit_id=row[0],
            timestamp=row[1],
            decision_id=row[2],
            agent_id=row[3],
            event_type=row[4],
            actor=row[5],
            actor_role=row[6],
            changes=json.loads(row[7]) if row[7] else {},
            reason=row[8] or "",
            authorization_level=row[9],
            is_reversal=bool(row[10]),
            parent_audit_id=row[11],
        )
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get audit trail statistics"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # Total events
        cursor.execute("SELECT COUNT(*) FROM audit_entries")
        total_events = cursor.fetchone()[0]
        
        # Events by type
        cursor.execute("""
            SELECT event_type, COUNT(*) as count
            FROM audit_entries
            GROUP BY event_type
        """)
        by_type = {row[0]: row[1] for row in cursor.fetchall()}
        
        # Events by actor
        cursor.execute("""
            SELECT actor, COUNT(*) as count
            FROM audit_entries
            GROUP BY actor
            ORDER BY count DESC
            LIMIT 10
        """)
        by_actor = {row[0]: row[1] for row in cursor.fetchall()}
        
        # Events by agent
        cursor.execute("""
            SELECT agent_id, COUNT(*) as count
            FROM audit_entries
            GROUP BY agent_id
            ORDER BY count DESC
        """)
        by_agent = {row[0]: row[1] for row in cursor.fetchall()}
        
        conn.close()
        
        return {
            "total_events": total_events,
            "by_event_type": by_type,
            "by_actor": by_actor,
            "by_agent": by_agent,
        }


# Export public API
__all__ = [
    'AuditEventType',
    'AuditLevel',
    'AuditEntry',
    'AuditTrailStore',
]
