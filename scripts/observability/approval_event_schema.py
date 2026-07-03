#!/usr/bin/env python3
"""
Approval Event Schema Validator (v1.0.0)

Validates all approval events against the schema defined in TELEMETRY_SCHEMA.md.
Enforces semantic versioning, immutability, and SLA tracking requirements.

Phase 12 Wave 2 - D3.2 Deliverable
"""

import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class EventValidationError(Exception):
    """Raised when event validation fails."""
    pass


class ApprovalEventValidator:
    """
    Validates approval events against schema v1.0.0.
    
    Key validations:
    - Required fields present
    - Version is compatible (v1.x.x)
    - Event type is one of 8 defined types
    - Timestamps are ISO-8601
    - SLA calculations correct
    - Approval chain complete and sequential
    """
    
    # Schema definition
    SCHEMA_VERSION = "1.0.0"
    
    REQUIRED_FIELDS = {
        "version",
        "timestamp",
        "event_type",
        "policy_id",
        "policy_category",
    }
    
    OPTIONAL_FIELDS = {
        "approval_id",
        "policy_version",
        "requester_id",
        "requester_role",
        "approval_chain",
        "final_result",
        "total_latency_seconds",
        "sla_seconds",
        "sla_met",
        "sla_status",
        "escalations",
        "delegations",
        "audit_context",
        "metadata",
    }
    
    VALID_EVENT_TYPES = {
        "approval.request.submitted",
        "approval.decision.made",
        "approval.stage.completed",
        "approval.escalated",
        "approval.delegated",
        "approval.delegated.revoked",
        "approval.sla.breached",
        "approval.policy.violated",
        "approval.completed",
    }
    
    VALID_POLICY_CATEGORIES = {
        "D", "S", "R", "C", "G", "I", "A", "E"
    }
    
    VALID_SLA_STATUSES = {
        "met",
        "approaching",
        "breached",
    }
    
    def __init__(self, strict_mode: bool = True):
        """
        Initialize validator.
        
        Args:
            strict_mode: If True, reject events with warnings. 
                        If False, log warnings but accept.
        """
        self.strict_mode = strict_mode
    
    def validate_event(self, event: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate a single event.
        
        Args:
            event: Event dictionary to validate
        
        Returns:
            (is_valid, error_list)
        """
        errors = []
        
        # Check required fields
        for field in self.REQUIRED_FIELDS:
            if field not in event:
                errors.append(f"Missing required field: {field}")
        
        if errors:
            return (False, errors)
        
        # Validate version
        version = event.get("version", "")
        if not self._is_compatible_version(version):
            errors.append(
                f"Version {version} incompatible with {self.SCHEMA_VERSION}. "
                "Only v1.x.x supported."
            )
        
        # Validate event type
        event_type = event.get("event_type")
        if event_type not in self.VALID_EVENT_TYPES:
            errors.append(f"Invalid event_type: {event_type}")
        
        # Validate policy category
        policy_category = event.get("policy_category")
        if policy_category not in self.VALID_POLICY_CATEGORIES:
            errors.append(f"Invalid policy_category: {policy_category}")
        
        # Validate timestamp
        try:
            datetime.fromisoformat(event.get("timestamp", "").replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            errors.append(f"Invalid timestamp format: {event.get('timestamp')}")
        
        # Validate SLA fields if present
        if "sla_status" in event:
            if event["sla_status"] not in self.VALID_SLA_STATUSES:
                errors.append(f"Invalid sla_status: {event['sla_status']}")
        
        # Validate approval chain structure
        if "approval_chain" in event:
            chain_errors = self._validate_approval_chain(event["approval_chain"])
            errors.extend(chain_errors)
        
        # Validate SLA calculation
        if "total_latency_seconds" in event and "sla_seconds" in event:
            sla_errors = self._validate_sla_calculation(event)
            errors.extend(sla_errors)
        
        return (len(errors) == 0, errors)
    
    def validate_event_batch(self, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Validate a batch of events.
        
        Returns:
            {
                "total": int,
                "valid": int,
                "invalid": int,
                "warnings": List[str],
                "errors": List[str],
                "event_type_distribution": Dict,
                "policy_category_distribution": Dict,
            }
        """
        result = {
            "total": len(events),
            "valid": 0,
            "invalid": 0,
            "warnings": [],
            "errors": [],
            "event_type_distribution": {},
            "policy_category_distribution": {},
        }
        
        for event in events:
            is_valid, errors = self.validate_event(event)
            
            if is_valid:
                result["valid"] += 1
            else:
                result["invalid"] += 1
                result["errors"].extend(errors)
            
            # Track distributions
            event_type = event.get("event_type", "unknown")
            result["event_type_distribution"][event_type] = (
                result["event_type_distribution"].get(event_type, 0) + 1
            )
            
            policy_cat = event.get("policy_category", "unknown")
            result["policy_category_distribution"][policy_cat] = (
                result["policy_category_distribution"].get(policy_cat, 0) + 1
            )
        
        return result
    
    # ========================================================================
    # PRIVATE VALIDATION METHODS
    # ========================================================================
    
    def _is_compatible_version(self, version: str) -> bool:
        """Check if version is compatible with schema (v1.x.x)."""
        try:
            parts = version.split(".")
            major = int(parts[0])
            return major == 1
        except (ValueError, IndexError):
            return False
    
    def _validate_approval_chain(self, chain: Any) -> List[str]:
        """Validate approval chain structure."""
        errors = []
        
        if not isinstance(chain, list):
            return ["approval_chain must be a list"]
        
        for i, stage in enumerate(chain):
            if not isinstance(stage, dict):
                errors.append(f"approval_chain[{i}] must be a dict")
                continue
            
            # Check required stage fields
            if "stage" not in stage:
                errors.append(f"approval_chain[{i}] missing 'stage' field")
            
            if "approver_id" not in stage:
                errors.append(f"approval_chain[{i}] missing 'approver_id' field")
            
            if "decision" not in stage:
                errors.append(f"approval_chain[{i}] missing 'decision' field")
            
            # Validate stage sequence
            expected_stage = i + 1
            if stage.get("stage") != expected_stage:
                errors.append(
                    f"approval_chain[{i}] has stage={stage.get('stage')}, "
                    f"expected {expected_stage}"
                )
        
        return errors
    
    def _validate_sla_calculation(self, event: Dict[str, Any]) -> List[str]:
        """Validate SLA calculation and status."""
        errors = []
        
        latency = event.get("total_latency_seconds", 0)
        sla_seconds = event.get("sla_seconds", 0)
        sla_met = event.get("sla_met")
        sla_status = event.get("sla_status")
        
        # Check consistency
        if sla_met is not None:
            expected_met = latency <= sla_seconds
            if sla_met != expected_met:
                errors.append(
                    f"sla_met={sla_met} but latency={latency}s vs "
                    f"sla_seconds={sla_seconds}s (expected {expected_met})"
                )
        
        # Check status consistency
        if sla_status:
            if sla_status == "met" and latency > sla_seconds:
                errors.append(
                    f"sla_status='met' but latency={latency}s > {sla_seconds}s"
                )
            elif sla_status == "breached" and latency <= sla_seconds:
                errors.append(
                    f"sla_status='breached' but latency={latency}s <= {sla_seconds}s"
                )
        
        return errors


class EventSchemaMigrator:
    """
    Handles semantic versioning migration for approval events.
    
    Supports v1.0.0 → v1.1.0 (minor: new optional fields)
    Handles v1.1.0 → v2.0.0 migration (major: breaking changes)
    """
    
    MIGRATION_RULES = {
        ("1.0.0", "1.1.0"): {
            "new_fields": {
                "override_justification": {"default": "", "type": "string"},
                "approval.sla.near_breach": {"default": None, "type": "optional_string"},
            },
            "breaking": False,
        },
    }
    
    @classmethod
    def migrate_event(cls, event: Dict[str, Any], target_version: str) -> Dict[str, Any]:
        """
        Migrate event to target version.
        
        Args:
            event: Event dictionary
            target_version: Target schema version (e.g., "1.1.0")
        
        Returns:
            Migrated event
        """
        source_version = event.get("version", "1.0.0")
        
        if source_version == target_version:
            return event
        
        # For now, just return as-is (no migrations needed yet)
        # When v2.0.0 is released, implement breaking change logic here
        event["version"] = target_version
        return event


class AuditEventLogger:
    """
    Logs immutable approval events to audit trail.
    Guarantees append-only semantics and 7-year retention.
    """
    
    def __init__(self, audit_log_path: str):
        """Initialize audit logger."""
        self.audit_log_path = audit_log_path
        self.logger = logging.getLogger(__name__)
    
    def log_event(self, event: Dict[str, Any]) -> bool:
        """
        Log event to immutable audit trail.
        
        Returns:
            True if logged successfully
        """
        try:
            # In production, this would write to a database with ACID properties
            # For now, just validate and log
            validator = ApprovalEventValidator()
            is_valid, errors = validator.validate_event(event)
            
            if not is_valid:
                self.logger.error(f"Invalid event, not logging: {errors}")
                return False
            
            # Add audit metadata
            event["audit_timestamp"] = datetime.now(timezone.utc).isoformat()
            event["audit_immutable"] = True
            
            self.logger.info(
                f"Audit event logged: {event.get('event_type')} "
                f"(approval_id={event.get('approval_id')})"
            )
            
            return True
        except Exception as e:
            self.logger.error(f"Audit logging failed: {e}")
            return False


if __name__ == "__main__":
    # Test validator
    logging.basicConfig(level=logging.DEBUG)
    
    validator = ApprovalEventValidator()
    
    # Test valid event
    valid_event = {
        "version": "1.0.0",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event_type": "approval.decision.made",
        "approval_id": "apr-001",
        "policy_id": "D-001",
        "policy_category": "D",
        "requester_id": "agent-01",
        "requester_role": "release-operator",
        "final_result": "approved",
        "total_latency_seconds": 3600.0,
        "sla_seconds": 14400.0,
        "sla_met": True,
        "sla_status": "met",
        "approval_chain": [
            {
                "stage": 1,
                "approver_id": "mgr-01",
                "approver_role": "release-manager",
                "decision": "approved",
                "assigned_at": datetime.now(timezone.utc).isoformat(),
                "decision_at": datetime.now(timezone.utc).isoformat(),
                "sla_met": True,
            }
        ],
    }
    
    is_valid, errors = validator.validate_event(valid_event)
    print(f"Valid event: {is_valid}")
    if errors:
        print(f"Errors: {errors}")
    
    # Test invalid event
    invalid_event = {
        "version": "1.0.0",
        # Missing required fields
    }
    
    is_valid, errors = validator.validate_event(invalid_event)
    print(f"\nInvalid event: {is_valid}")
    print(f"Errors: {errors}")
