#!/usr/bin/env python3
"""
Validation Engine for Canonical Execution States

Post-action evaluation and constraint verification for runtime systems.
Ensures states meet quality, integrity, and business rule requirements before
persistence and continuation.

INTEGRATION POINTS:
- ACT → VALIDATE → PASS → PERSIST or FAIL → BLOCK/ESCALATE
- Used by checkpoint manager before creating checkpoints
- Used by handoff protocol before agent transitions
- Used by runtime before step continuation
"""

import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set


class ValidationSeverity(str, Enum):
    """Severity levels for validation violations."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ValidationRule(str, Enum):
    """Predefined validation rules."""
    MISSING_REQUIRED_FIELD = "missing_required_field"
    INVALID_FIELD_TYPE = "invalid_field_type"
    INVALID_STATE_TRANSITION = "invalid_state_transition"
    DEPENDENCY_RESOLUTION_FAILED = "dependency_resolution_failed"
    CONFIDENCE_THRESHOLD_VIOLATION = "confidence_threshold_violation"
    DATA_INTEGRITY_VIOLATION = "data_integrity_violation"
    CIRCULAR_DEPENDENCY_DETECTED = "circular_dependency_detected"
    UNRESOLVED_BLOCKER = "unresolved_blocker"
    ESCALATION_REQUIRED = "escalation_required"
    ACTION_EXECUTION_FAILED = "action_execution_failed"


class ValidatorConfig:
    """Configuration for validation rules."""
    
    # Required top-level fields
    REQUIRED_FIELDS: Set[str] = {
        "state_id",
        "agent_id",
        "phase_id",
        "track_id",
        "task_id",
        "execution_step",
        "status",
        "timestamp"
    }
    
    # Valid execution steps
    VALID_EXECUTION_STEPS: Set[str] = {
        "observe",
        "context",
        "decide",
        "act",
        "validate",
        "persist",
        "handoff",
        "complete"
    }
    
    # Valid state statuses
    VALID_STATUSES: Set[str] = {
        "in_progress",
        "validated",
        "failed",
        "blocked",
        "escalated",
        "handoff_pending"
    }
    
    # Allowed status transitions (state_machine)
    VALID_TRANSITIONS: Dict[str, Set[str]] = {
        "in_progress": {"validated", "failed", "blocked", "escalated"},
        "validated": {"in_progress", "handoff_pending", "complete"},
        "failed": {"blocked", "escalated", "in_progress"},
        "blocked": {"in_progress", "escalated"},
        "escalated": {"in_progress", "failed", "blocked"},
        "handoff_pending": {"in_progress", "complete"}
    }
    
    # Minimum confidence thresholds by execution step
    MIN_CONFIDENCE_BY_STEP: Dict[str, float] = {
        "observe": 0.5,
        "context": 0.6,
        "decide": 0.7,
        "act": 0.75,
        "validate": 0.8,
        "persist": 0.85,
        "handoff": 0.9,
        "complete": 0.9
    }
    
    # Global minimum confidence threshold
    GLOBAL_MIN_CONFIDENCE: float = 0.5


def validate_state(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate a canonical execution state.
    
    Post-action evaluation of system state before persistence and continuation.
    
    Args:
        state: The state dict to validate
        
    Returns:
        {
            "valid": bool,
            "violations": [],  # Critical/High/Medium violations
            "warnings": [],    # Low/advisory warnings
            "confidence_adjustment": float,
            "requires_escalation": bool,
            "validation_timestamp": ISO8601,
            "validator_id": str
        }
    """
    validator_id = str(uuid.uuid4())[:8]
    validation_result = {
        "valid": True,
        "violations": [],
        "warnings": [],
        "confidence_adjustment": 0.0,
        "requires_escalation": False,
        "validation_timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "validator_id": validator_id
    }
    
    # Run all validation checks
    checks = [
        _check_required_fields,
        _check_field_types,
        _check_state_machine_transitions,
        _check_dependency_resolution,
        _check_confidence_thresholds,
        _check_data_integrity,
        _check_circular_dependencies,
        _check_unresolved_blockers,
        _check_action_execution_status,
    ]
    
    for check in checks:
        check(state, validation_result)
    
    # Determine overall validity
    critical_violations = [v for v in validation_result["violations"]
                          if v.get("severity") == ValidationSeverity.CRITICAL]
    high_violations = [v for v in validation_result["violations"]
                      if v.get("severity") == ValidationSeverity.HIGH]
    
    validation_result["valid"] = len(critical_violations) == 0 and len(high_violations) == 0
    validation_result["requires_escalation"] = (
        len(critical_violations) > 0 or
        state.get("status") == "escalated" or
        any(item.get("type") == "blocker"
            for item in state.get("unresolved_items", []))
    )
    
    return validation_result


def _check_required_fields(state: Dict[str, Any],
                          result: Dict[str, Any]) -> None:
    """Check that all required fields are present."""
    for field in ValidatorConfig.REQUIRED_FIELDS:
        if field not in state or state[field] is None:
            result["violations"].append({
                "rule": ValidationRule.MISSING_REQUIRED_FIELD,
                "severity": ValidationSeverity.CRITICAL,
                "field": field,
                "message": f"Required field '{field}' is missing or null"
            })


def _check_field_types(state: Dict[str, Any],
                       result: Dict[str, Any]) -> None:
    """Check that fields have expected types."""
    type_checks = {
        "state_id": str,
        "agent_id": str,
        "phase_id": str,
        "track_id": str,
        "task_id": str,
        "execution_step": str,
        "status": str,
        "timestamp": str,
        "confidence_score": (int, float),
        "input_context": dict,
        "decision_context": dict,
        "actions_taken": list,
        "validation_results": dict,
        "dependencies": list,
        "unresolved_items": list,
    }
    
    for field, expected_type in type_checks.items():
        if field in state and state[field] is not None:
            if not isinstance(state[field], expected_type):
                result["violations"].append({
                    "rule": ValidationRule.INVALID_FIELD_TYPE,
                    "severity": ValidationSeverity.HIGH,
                    "field": field,
                    "expected_type": str(expected_type),
                    "actual_type": str(type(state[field])),
                    "message": f"Field '{field}' has type {type(state[field])}, "
                               f"expected {expected_type}"
                })


def _check_state_machine_transitions(state: Dict[str, Any],
                                    result: Dict[str, Any]) -> None:
    """Check that status transitions are valid (state machine)."""
    current_status = state.get("status")
    previous_state_id = state.get("previous_state_id")
    
    # Validate current status is in valid set
    if current_status not in ValidatorConfig.VALID_STATUSES:
        result["violations"].append({
            "rule": ValidationRule.INVALID_STATE_TRANSITION,
            "severity": ValidationSeverity.HIGH,
            "current_status": current_status,
            "valid_statuses": list(ValidatorConfig.VALID_STATUSES),
            "message": f"Status '{current_status}' is not in valid states"
        })
        return
    
    # Validate execution step is valid
    execution_step = state.get("execution_step")
    if execution_step not in ValidatorConfig.VALID_EXECUTION_STEPS:
        result["violations"].append({
            "rule": ValidationRule.INVALID_STATE_TRANSITION,
            "severity": ValidationSeverity.HIGH,
            "execution_step": execution_step,
            "valid_steps": list(ValidatorConfig.VALID_EXECUTION_STEPS),
            "message": f"Execution step '{execution_step}' is not valid"
        })
    
    # If there's a previous state, we could validate the transition
    # (In a full implementation, would load previous state from checkpoint storage)
    if previous_state_id and previous_state_id != "null":
        result["warnings"].append({
            "rule": "state_transition_not_fully_validated",
            "message": f"Full transition validation requires loading previous state "
                      f"{previous_state_id} from checkpoint storage"
        })


def _check_dependency_resolution(state: Dict[str, Any],
                                result: Dict[str, Any]) -> None:
    """Check that dependencies are resolved."""
    dependencies = state.get("dependencies", [])
    
    for dep in dependencies:
        dep_status = dep.get("status", "")
        dep_type = dep.get("type", "")
        dep_id = dep.get("id", "")
        
        if dep_status == "blocked":
            result["violations"].append({
                "rule": ValidationRule.DEPENDENCY_RESOLUTION_FAILED,
                "severity": ValidationSeverity.HIGH,
                "dependency_type": dep_type,
                "dependency_id": dep_id,
                "message": f"Dependency {dep_type}:{dep_id} is blocked"
            })
        elif dep_status == "failed":
            result["violations"].append({
                "rule": ValidationRule.DEPENDENCY_RESOLUTION_FAILED,
                "severity": ValidationSeverity.CRITICAL,
                "dependency_type": dep_type,
                "dependency_id": dep_id,
                "message": f"Dependency {dep_type}:{dep_id} has failed"
            })
        elif dep_status not in {"pending", "resolved", "failed", "blocked"}:
            result["warnings"].append({
                "rule": "unknown_dependency_status",
                "dependency_type": dep_type,
                "dependency_id": dep_id,
                "status": dep_status,
                "message": f"Unknown dependency status: {dep_status}"
            })


def _check_confidence_thresholds(state: Dict[str, Any],
                                result: Dict[str, Any]) -> None:
    """Check that confidence scores meet thresholds for the execution step."""
    confidence = state.get("confidence_score", 0.0)
    execution_step = state.get("execution_step", "")
    
    # Check global minimum
    if confidence < ValidatorConfig.GLOBAL_MIN_CONFIDENCE:
        result["violations"].append({
            "rule": ValidationRule.CONFIDENCE_THRESHOLD_VIOLATION,
            "severity": ValidationSeverity.MEDIUM,
            "confidence": confidence,
            "minimum_required": ValidatorConfig.GLOBAL_MIN_CONFIDENCE,
            "message": f"Confidence {confidence} below global minimum "
                      f"{ValidatorConfig.GLOBAL_MIN_CONFIDENCE}"
        })
    
    # Check step-specific minimum
    if execution_step in ValidatorConfig.MIN_CONFIDENCE_BY_STEP:
        step_minimum = ValidatorConfig.MIN_CONFIDENCE_BY_STEP[execution_step]
        if confidence < step_minimum:
            result["violations"].append({
                "rule": ValidationRule.CONFIDENCE_THRESHOLD_VIOLATION,
                "severity": ValidationSeverity.HIGH,
                "execution_step": execution_step,
                "confidence": confidence,
                "step_minimum": step_minimum,
                "message": f"Confidence {confidence} below step minimum "
                          f"{step_minimum} for '{execution_step}'"
            })


def _check_data_integrity(state: Dict[str, Any],
                         result: Dict[str, Any]) -> None:
    """Check data integrity and consistency."""
    # Check UUID format for state_id
    state_id = state.get("state_id", "")
    if state_id and not _is_valid_uuid(state_id):
        result["violations"].append({
            "rule": ValidationRule.DATA_INTEGRITY_VIOLATION,
            "severity": ValidationSeverity.HIGH,
            "field": "state_id",
            "value": state_id,
            "message": f"state_id '{state_id}' is not a valid UUID"
        })
    
    # Check previous_state_id format if present
    previous_state_id = state.get("previous_state_id")
    if previous_state_id and previous_state_id != "null":
        if not _is_valid_uuid(previous_state_id):
            result["violations"].append({
                "rule": ValidationRule.DATA_INTEGRITY_VIOLATION,
                "severity": ValidationSeverity.MEDIUM,
                "field": "previous_state_id",
                "value": previous_state_id,
                "message": f"previous_state_id '{previous_state_id}' is not a valid UUID"
            })
    
    # Check timestamp format (should be ISO 8601)
    timestamp = state.get("timestamp", "")
    if timestamp and not _is_valid_iso8601(timestamp):
        result["violations"].append({
            "rule": ValidationRule.DATA_INTEGRITY_VIOLATION,
            "severity": ValidationSeverity.HIGH,
            "field": "timestamp",
            "value": timestamp,
            "message": f"timestamp '{timestamp}' is not ISO 8601 format"
        })
    
    # Check actions have required fields
    actions = state.get("actions_taken", [])
    for i, action in enumerate(actions):
        if not isinstance(action, dict):
            result["violations"].append({
                "rule": ValidationRule.DATA_INTEGRITY_VIOLATION,
                "severity": ValidationSeverity.MEDIUM,
                "field": f"actions_taken[{i}]",
                "message": f"Action at index {i} is not a dict"
            })
            continue
        
        required_action_fields = {"action_id", "action_type", "status"}
        missing = required_action_fields - set(action.keys())
        if missing:
            result["violations"].append({
                "rule": ValidationRule.DATA_INTEGRITY_VIOLATION,
                "severity": ValidationSeverity.MEDIUM,
                "field": f"actions_taken[{i}]",
                "missing_fields": list(missing),
                "message": f"Action at index {i} missing required fields: {missing}"
            })


def _check_circular_dependencies(state: Dict[str, Any],
                                result: Dict[str, Any]) -> None:
    """Check for circular dependency chains."""
    dependencies = state.get("dependencies", [])
    state_id = state.get("state_id", "")
    
    dep_ids: Set[str] = set()
    dep_graph: Dict[str, List[str]] = {}
    
    for dep in dependencies:
        dep_id = dep.get("id", "")
        if dep_id:
            dep_ids.add(dep_id)
            dep_graph[dep_id] = []
    
    # Check if state_id is in its own dependency chain (direct self-reference)
    if state_id in dep_ids:
        result["violations"].append({
            "rule": ValidationRule.CIRCULAR_DEPENDENCY_DETECTED,
            "severity": ValidationSeverity.CRITICAL,
            "state_id": state_id,
            "message": f"State {state_id} is in its own dependency chain"
        })
    
    # Simple check: if we have the graph, do cycle detection
    # (Full implementation would need to load dependency states)
    if len(dep_ids) > 0:
        result["warnings"].append({
            "rule": "circular_dependency_check_incomplete",
            "message": "Full circular dependency checking requires loading dependent states "
                      "from checkpoint storage"
        })


def _check_unresolved_blockers(state: Dict[str, Any],
                              result: Dict[str, Any]) -> None:
    """Check for unresolved blocker items."""
    unresolved = state.get("unresolved_items", [])
    
    for i, item in enumerate(unresolved):
        item_type = item.get("type", "")
        if item_type == "blocker":
            result["violations"].append({
                "rule": ValidationRule.UNRESOLVED_BLOCKER,
                "severity": ValidationSeverity.HIGH,
                "item_id": item.get("item_id", f"unresolved[{i}]"),
                "description": item.get("description", ""),
                "owner": item.get("owner", "unassigned"),
                "message": f"Unresolved blocker: {item.get('description', 'No description')}"
            })


def _check_action_execution_status(state: Dict[str, Any],
                                  result: Dict[str, Any]) -> None:
    """Check that actions have valid execution status."""
    actions = state.get("actions_taken", [])
    
    valid_action_statuses = {"pending", "in_progress", "completed", "failed"}
    
    for i, action in enumerate(actions):
        if not isinstance(action, dict):
            continue
        
        action_status = action.get("status", "")
        if action_status not in valid_action_statuses:
            result["warnings"].append({
                "rule": "invalid_action_status",
                "action_id": action.get("action_id", f"action[{i}]"),
                "status": action_status,
                "valid_statuses": list(valid_action_statuses),
                "message": f"Action has invalid status: {action_status}"
            })
        
        # If execution_step is "validate" but action failed, flag it
        if action_status == "failed" and state.get("execution_step") == "validate":
            action_type = action.get("action_type", "unknown")
            action_target = action.get("target", "N/A")
            error_info = action.get("error", "No error details")
            result["violations"].append({
                "rule": ValidationRule.ACTION_EXECUTION_FAILED,
                "severity": ValidationSeverity.HIGH,
                "action_id": action.get("action_id", f"action[{i}]"),
                "message": (
                    f"Action failed: type={action_type}, target={action_target}, "
                    f"error={error_info}"
                )
            })


def _is_valid_uuid(value: str) -> bool:
    """Check if value is a valid UUID."""
    try:
        uuid.UUID(value)
        return True
    except (ValueError, AttributeError, TypeError):
        return False


def _is_valid_iso8601(value: str) -> bool:
    """Check if value is a valid ISO 8601 timestamp."""
    try:
        # Accept formats like "2026-06-30T23:44:58Z" or "2026-06-30T23:44:58+00:00"
        datetime.fromisoformat(value.replace('Z', '+00:00'))
        return True
    except (ValueError, AttributeError, TypeError):
        return False


def validate_state_transition(from_state: Optional[Dict[str, Any]],
                            to_state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate that a state transition is legal.
    
    Args:
        from_state: Previous state (None if initial state)
        to_state: New state to transition to
        
    Returns:
        Validation result including transition legality
    """
    result = validate_state(to_state)
    
    if from_state is None:
        # Initial state transition - allow any status
        return result
    
    from_status = from_state.get("status", "")
    to_status = to_state.get("status", "")
    
    # Check state machine transitions
    allowed_transitions = ValidatorConfig.VALID_TRANSITIONS.get(from_status, set())
    if to_status not in allowed_transitions:
        result["violations"].append({
            "rule": ValidationRule.INVALID_STATE_TRANSITION,
            "severity": ValidationSeverity.HIGH,
            "from_status": from_status,
            "to_status": to_status,
            "allowed_transitions": list(allowed_transitions),
            "message": f"Invalid transition from '{from_status}' to '{to_status}'"
        })
        result["valid"] = False
    
    return result
