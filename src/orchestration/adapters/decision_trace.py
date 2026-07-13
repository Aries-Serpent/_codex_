"""Decision-Trace Writer — JSONL append-only audit log for decisions.

Implements immutable append-only JSONL logging of all decisions made
during lane execution for full auditability and replay.
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import jsonschema


class DecisionTraceError(Exception):
    """Raised when decision trace operations fail."""

    pass


class DecisionTraceWriter:
    """Writes immutable JSONL audit logs of decisions."""

    SCHEMA = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "title": "Decision Trace Entry",
        "type": "object",
        "required": ["timestamp", "lane_id", "decision_type", "input_lock_hash", "outcome"],
        "properties": {
            "timestamp": {
                "type": "string",
                "pattern": r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z$",
            },
            "lane_id": {
                "type": "string",
                "enum": ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K"],
            },
            "decision_type": {
                "type": "string",
                "enum": ["action", "gate_pass", "gate_fail", "escalation", "rollback"],
            },
            "input_lock_hash": {"type": "string", "pattern": "^[a-f0-9]{64}$"},
            "description": {"type": "string"},
            "outcome": {
                "type": "string",
                "enum": ["success", "failure", "pending", "escalated"],
            },
            "evidence": {"type": "array", "items": {"type": "string"}},
            "context": {"type": "object", "additionalProperties": True},
        },
    }

    def __init__(self, trace_path: Path):
        """Initialize decision trace writer.

        Args:
            trace_path: Path to JSONL trace file

        Raises:
            DecisionTraceError: If initialization fails
        """
        self.trace_path = Path(trace_path)
        self._entry_count = 0

        try:
            self.trace_path.parent.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            raise DecisionTraceError(f"Failed to create trace directory: {e}")

    @staticmethod
    def _utc_timestamp_ms() -> str:
        """Generate ISO 8601 UTC timestamp with milliseconds and Z suffix.

        Returns:
            Timestamp string like '2026-07-13T00:29:42.101Z'
        """
        return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"

    def append(
        self,
        lane_id: str,
        decision_type: str,
        input_lock_hash: str,
        outcome: str,
        description: Optional[str] = None,
        evidence: Optional[List[str]] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Append a decision entry to the trace.

        Args:
            lane_id: Lane identifier (A-K)
            decision_type: Type of decision (action, gate_pass, etc.)
            input_lock_hash: SHA256 hash of input lock
            outcome: Decision outcome (success, failure, etc.)
            description: Optional human-readable description
            evidence: Optional list of supporting artifact references
            context: Optional additional context

        Raises:
            DecisionTraceError: If append fails or validation fails
        """
        try:
            entry = {
                "timestamp": self._utc_timestamp_ms(),
                "lane_id": lane_id,
                "decision_type": decision_type,
                "input_lock_hash": input_lock_hash,
                "outcome": outcome,
            }

            if description is not None:
                entry["description"] = description
            if evidence is not None:
                entry["evidence"] = evidence
            if context is not None:
                entry["context"] = context

            # Validate against schema
            jsonschema.validate(entry, self.SCHEMA)

            # Append to file in append-only mode
            with open(self.trace_path, "a") as f:
                f.write(json.dumps(entry) + "\n")

            self._entry_count += 1

        except jsonschema.ValidationError as e:
            raise DecisionTraceError(f"Entry validation failed: {e}")
        except Exception as e:
            raise DecisionTraceError(f"Failed to append decision trace: {e}")

    def get_entry_count(self) -> int:
        """Get count of entries written to trace.

        Returns:
            Number of entries
        """
        return self._entry_count

    def read_all(self) -> List[Dict[str, Any]]:
        """Read all entries from the trace file.

        Returns:
            List of decision entries

        Raises:
            DecisionTraceError: If read fails
        """
        try:
            if not self.trace_path.exists():
                return []

            entries = []
            with open(self.trace_path, "r") as f:
                for line in f:
                    if line.strip():
                        entries.append(json.loads(line))
            return entries
        except Exception as e:
            raise DecisionTraceError(f"Failed to read trace file: {e}")

    def verify_integrity(self) -> bool:
        """Verify trace file integrity.

        Checks that:
        - File exists
        - All entries are valid JSON
        - All entries pass schema validation

        Returns:
            True if integrity check passes

        Raises:
            DecisionTraceError: If integrity check fails
        """
        try:
            if not self.trace_path.exists():
                raise DecisionTraceError("Trace file does not exist")

            entries = []
            with open(self.trace_path, "r") as f:
                for line_num, line in enumerate(f, 1):
                    if line.strip():
                        try:
                            entry = json.loads(line)
                            jsonschema.validate(entry, self.SCHEMA)
                            entries.append(entry)
                        except json.JSONDecodeError as e:
                            raise DecisionTraceError(
                                f"Invalid JSON at line {line_num}: {e}"
                            )
                        except jsonschema.ValidationError as e:
                            raise DecisionTraceError(
                                f"Schema validation failed at line {line_num}: {e}"
                            )

            if len(entries) == 0:
                raise DecisionTraceError("Trace file is empty")

            return True

        except DecisionTraceError:
            raise
        except Exception as e:
            raise DecisionTraceError(f"Integrity check failed: {e}")
