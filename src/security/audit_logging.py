"""Security audit and logging module for Phase 3.

This module provides:
1. Security event logging with structured format
2. Audit trail creation and management
3. PII-safe logging (no sensitive data)
4. Compliance reporting
5. Incident tracking
"""

from __future__ import annotations

import json
import logging
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Optional

import structlog

logger = structlog.get_logger(__name__)
fallback_logger = logging.getLogger(__name__)


class SecurityEventType(str, Enum):
    """Types of security events to track."""

    # Authentication events
    AUTH_ATTEMPT = "auth_attempt"
    AUTH_SUCCESS = "auth_success"
    AUTH_FAILURE = "auth_failure"
    SESSION_CREATED = "session_created"
    SESSION_TERMINATED = "session_terminated"

    # Authorization events
    PERMISSION_GRANTED = "permission_granted"
    PERMISSION_DENIED = "permission_denied"
    RBAC_VIOLATION = "rbac_violation"

    # Data access events
    DATA_ACCESS = "data_access"
    DATA_MODIFICATION = "data_modification"
    DATA_DELETION = "data_deletion"
    SENSITIVE_DATA_ACCESS = "sensitive_data_access"

    # Security events
    VULNERABILITY_DETECTED = "vulnerability_detected"
    MALWARE_DETECTED = "malware_detected"
    ANOMALY_DETECTED = "anomaly_detected"
    THREAT_MITIGATED = "threat_mitigated"

    # System events
    CONFIGURATION_CHANGE = "configuration_change"
    SECURITY_POLICY_UPDATE = "security_policy_update"
    CERTIFICATE_EXPIRY_WARNING = "certificate_expiry_warning"

    # Network events
    SUSPICIOUS_REQUEST = "suspicious_request"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    DDOS_MITIGATED = "ddos_mitigated"

    # Audit events
    AUDIT_TRAIL_ACCESSED = "audit_trail_accessed"
    AUDIT_TRAIL_EXPORTED = "audit_trail_exported"


class SecurityEventSeverity(str, Enum):
    """Severity levels for security events."""

    INFO = "info"
    WARNING = "warning"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class SecurityEvent:
    """Structured security event for audit logging."""

    event_type: SecurityEventType
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    severity: SecurityEventSeverity = SecurityEventSeverity.INFO
    source: str = ""  # e.g., "api_endpoint", "service_name"
    actor: Optional[str] = None  # User ID or service name (no PII!)
    action: str = ""  # What was done
    resource: Optional[str] = None  # What resource was affected (no PII!)
    status: str = "success"  # "success" or "failure"
    error_code: Optional[str] = None
    details: dict[str, Any] = field(default_factory=dict)  # Additional context (sanitized!)

    def to_dict(self) -> dict:
        """Convert to dictionary for logging.

        Returns
        -------
        dict
            Event as dictionary with safe values
        """
        event_dict = asdict(self)
        # Ensure nested datetime is serializable
        event_dict["timestamp"] = self.timestamp.isoformat()
        event_dict["event_type"] = self.event_type.value
        event_dict["severity"] = self.severity.value
        return event_dict

    def to_json(self) -> str:
        """Convert to JSON string for logging.

        Returns
        -------
        str
            Event as JSON string
        """
        return json.dumps(self.to_dict(), default=str)


class SecurityAuditLogger:
    """Centralized security audit logger with PII protection."""

    def __init__(
        self,
        audit_log_path: Optional[str] = None,
        max_events: int = 10000,
    ):
        """Initialize security audit logger.

        Parameters
        ----------
        audit_log_path : Optional[str]
            Path to audit log file. If None, uses memory buffer only.
        max_events : int
            Maximum events to keep in memory buffer
        """
        self.audit_log_path = Path(audit_log_path) if audit_log_path else None
        self.max_events = max_events
        self.events: list[SecurityEvent] = []

    def log_event(self, event: SecurityEvent) -> None:
        """Log a security event.

        Parameters
        ----------
        event : SecurityEvent
            Security event to log
        """
        # PHASE 3 HARDENING: Always ensure event data is sanitized
        self._sanitize_event(event)

        # Add to in-memory buffer
        self.events.append(event)
        if len(self.events) > self.max_events:
            self.events = self.events[-self.max_events :]

        # Log via structlog (structured logging)
        try:
            logger.info(
                f"Security event: {event.event_type.value}",
                event_type=event.event_type.value,
                severity=event.severity.value,
                actor=event.actor,
                action=event.action,
                status=event.status,
                resource=event.resource,
            )
        except Exception as exc:
            # Fallback to standard logging
            fallback_logger.info(f"Security event: {event.to_json()}", exc_info=False)

        # Write to audit log file if configured
        if self.audit_log_path:
            self._write_to_audit_file(event)

    def _sanitize_event(self, event: SecurityEvent) -> None:
        """Sanitize event data to remove PII.

        Parameters
        ----------
        event : SecurityEvent
            Event to sanitize (modified in place)
        """
        # Actor should be anonymized (e.g., user_id not username)
        if event.actor and any(
            char in event.actor.lower() for char in ["@", ".", "user", "admin"]
        ):
            event.actor = self._anonymize_identifier(event.actor)

        # Resource should not contain full paths with usernames
        if event.resource:
            event.resource = self._redact_path(event.resource)

        # Details should have PII removed
        sanitized_details = {}
        for key, value in event.details.items():
            sanitized_details[key] = self._redact_value(value)
        event.details = sanitized_details

    @staticmethod
    def _anonymize_identifier(identifier: str) -> str:
        """Anonymize identifier (e.g., user ID).

        Parameters
        ----------
        identifier : str
            Identifier to anonymize

        Returns
        -------
        str
            Anonymized identifier
        """
        # Keep first 4 and last 4 characters
        if len(identifier) > 8:
            return f"{identifier[:4]}...{identifier[-4:]}"
        return "***"

    @staticmethod
    def _redact_path(path: str, max_depth: int = 3) -> str:
        """Redact path to prevent PII exposure.

        Parameters
        ----------
        path : str
            File path or similar
        max_depth : int
            Maximum depth to keep

        Returns
        -------
        str
            Redacted path
        """
        # Remove common PII patterns from paths
        redacted = path
        for pattern in ["/home/", "/Users/", "/root/"]:
            if pattern in redacted:
                redacted = redacted.replace(pattern, "/****/")
        return redacted

    @staticmethod
    def _redact_value(value: Any) -> Any:
        """Redact PII from any value.

        Parameters
        ----------
        value : Any
            Value to redact

        Returns
        -------
        Any
            Redacted value
        """
        if not isinstance(value, str):
            return value

        # Redact email addresses
        value = SecurityAuditLogger._redact_emails(value)

        # Redact credit cards
        value = SecurityAuditLogger._redact_credit_cards(value)

        # Redact phone numbers
        value = SecurityAuditLogger._redact_phone_numbers(value)

        return value

    @staticmethod
    def _redact_emails(text: str) -> str:
        """Redact email addresses from text."""
        import re

        return re.sub(r"[\w\.-]+@[\w\.-]+\.\w+", "***@***.***", text)

    @staticmethod
    def _redact_credit_cards(text: str) -> str:
        """Redact credit card numbers from text."""
        import re

        return re.sub(r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b", "****-****-****-****", text)

    @staticmethod
    def _redact_phone_numbers(text: str) -> str:
        """Redact phone numbers from text."""
        import re

        return re.sub(r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b", "***-***-****", text)

    def _write_to_audit_file(self, event: SecurityEvent) -> None:
        """Write event to audit log file.

        Parameters
        ----------
        event : SecurityEvent
            Event to write
        """
        try:
            with open(self.audit_log_path, "a", encoding="utf-8") as f:
                f.write(event.to_json() + "\n")
        except Exception as exc:
            fallback_logger.error(f"Failed to write audit log: {exc}")

    def get_events(
        self,
        event_type: Optional[SecurityEventType] = None,
        severity: Optional[SecurityEventSeverity] = None,
        actor: Optional[str] = None,
        since: Optional[datetime] = None,
    ) -> list[SecurityEvent]:
        """Query audit events with optional filters.

        Parameters
        ----------
        event_type : Optional[SecurityEventType]
            Filter by event type
        severity : Optional[SecurityEventSeverity]
            Filter by severity
        actor : Optional[str]
            Filter by actor
        since : Optional[datetime]
            Filter events after timestamp

        Returns
        -------
        list[SecurityEvent]
            Filtered events
        """
        results = self.events

        if event_type is not None:
            results = [e for e in results if e.event_type == event_type]

        if severity is not None:
            results = [e for e in results if e.severity == severity]

        if actor is not None:
            results = [e for e in results if e.actor == actor]

        if since is not None:
            results = [e for e in results if e.timestamp >= since]

        return results

    def generate_compliance_report(self) -> dict:
        """Generate compliance report from audit events.

        Returns
        -------
        dict
            Compliance report
        """
        critical_events = [
            e for e in self.events if e.severity == SecurityEventSeverity.CRITICAL
        ]
        high_events = [e for e in self.events if e.severity == SecurityEventSeverity.HIGH]
        auth_failures = [
            e for e in self.events if e.event_type == SecurityEventType.AUTH_FAILURE
        ]
        rbac_violations = [
            e for e in self.events if e.event_type == SecurityEventType.RBAC_VIOLATION
        ]

        return {
            "report_timestamp": datetime.now(timezone.utc).isoformat(),
            "total_events": len(self.events),
            "critical_events": len(critical_events),
            "high_events": len(high_events),
            "auth_failures": len(auth_failures),
            "rbac_violations": len(rbac_violations),
            "recent_critical": [e.to_dict() for e in critical_events[-10:]],
            "recommendations": self._generate_recommendations(
                critical_events, auth_failures, rbac_violations
            ),
        }

    @staticmethod
    def _generate_recommendations(
        critical_events: list[SecurityEvent],
        auth_failures: list[SecurityEvent],
        rbac_violations: list[SecurityEvent],
    ) -> list[str]:
        """Generate recommendations based on events.

        Parameters
        ----------
        critical_events : list[SecurityEvent]
            Critical severity events
        auth_failures : list[SecurityEvent]
            Authentication failure events
        rbac_violations : list[SecurityEvent]
            RBAC violation events

        Returns
        -------
        list[str]
            Recommendations
        """
        recommendations = []

        if len(critical_events) > 5:
            recommendations.append("Multiple critical security events detected. Review immediately.")

        if len(auth_failures) > 10:
            recommendations.append(
                "High rate of authentication failures. Check for brute force attacks."
            )

        if len(rbac_violations) > 5:
            recommendations.append("Multiple RBAC violations detected. Audit permission settings.")

        if not recommendations:
            recommendations.append("No immediate recommendations. Continue monitoring.")

        return recommendations


# PHASE 3 HARDENING: Global audit logger instance
_global_audit_logger: Optional[SecurityAuditLogger] = None


def get_audit_logger() -> SecurityAuditLogger:
    """Get global audit logger instance (lazy initialization).

    Returns
    -------
    SecurityAuditLogger
        Global audit logger
    """
    global _global_audit_logger
    if _global_audit_logger is None:
        _global_audit_logger = SecurityAuditLogger(
            audit_log_path=".codex/audit/security_events.jsonl"
        )
    return _global_audit_logger


def log_security_event(
    event_type: SecurityEventType,
    action: str,
    severity: SecurityEventSeverity = SecurityEventSeverity.INFO,
    **kwargs: Any,
) -> None:
    """Convenience function to log security event.

    Parameters
    ----------
    event_type : SecurityEventType
        Type of security event
    action : str
        What was done
    severity : SecurityEventSeverity
        Event severity level
    **kwargs
        Additional event attributes
    """
    event = SecurityEvent(
        event_type=event_type,
        action=action,
        severity=severity,
        **kwargs,
    )
    get_audit_logger().log_event(event)


__all__ = [
    "SecurityEventType",
    "SecurityEventSeverity",
    "SecurityEvent",
    "SecurityAuditLogger",
    "get_audit_logger",
    "log_security_event",
]
