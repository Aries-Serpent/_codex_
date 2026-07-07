#!/usr/bin/env python3
"""
Core Event Schema Validator (v1.0.0)

Validates all core events against the schema defined in TELEMETRY_SCHEMA.md.

Phase 12 Wave 2 - D3.2 Deliverable
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Tuple
import logging

logger = logging.getLogger(__name__)


class CoreEventValidator:
    """
    Validates core telemetry events against schema v1.0.0.
    """
    
    SCHEMA_VERSION = "1.0.0"
    
    REQUIRED_FIELDS = {
        "version",
        "timestamp",
        "event_type",
        "domain",
    }
    
    VALID_DOMAINS = {
        "agent_lifecycle",
        "workflow_execution",
        "permission_access_control",
        "configuration_management",
        "secret_token_management",
    }
    
    VALID_EVENT_TYPES = {
        "agent.launched",
        "agent.stopped",
        "agent.restarted",
        "workflow.triggered",
        "workflow.completed",
        "rbac.role.check",
        "rbac.access.denied",
        "config.changed",
        "config.drift",
        "secret.accessed",
        "secret.rotated",
    }
    
    def __init__(self, strict_mode: bool = True):
        self.strict_mode = strict_mode
    
    def validate_event(self, event: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate a single event."""
        errors = []
        
        for field in self.REQUIRED_FIELDS:
            if field not in event:
                errors.append(f"Missing required field: {field}")
        
        if errors:
            return (False, errors)
        
        version = event.get("version", "")
        if not self._is_compatible_version(version):
            errors.append(f"Version {version} incompatible with {self.SCHEMA_VERSION}.")
        
        event_type = event.get("event_type")
        if event_type and event_type not in self.VALID_EVENT_TYPES:
            errors.append(f"Invalid event_type: {event_type}")
            
        domain = event.get("domain")
        if domain and domain not in self.VALID_DOMAINS:
            errors.append(f"Invalid domain: {domain}")
            
        try:
            datetime.fromisoformat(event.get("timestamp", "").replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            errors.append(f"Invalid timestamp format: {event.get('timestamp')}")
            
        return (len(errors) == 0, errors)
        
    def _is_compatible_version(self, version: str) -> bool:
        try:
            parts = version.split(".")
            major = int(parts[0])
            return major == 1
        except (ValueError, IndexError):
            return False

if __name__ == "__main__":
    validator = CoreEventValidator()
    event = {
        "version": "1.0.0",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event_type": "agent.launched",
        "domain": "agent_lifecycle",
        "agent_id": "agent-01"
    }
    is_valid, errors = validator.validate_event(event)
    print(f"Valid event: {is_valid}")
    if errors:
        print(f"Errors: {errors}")
