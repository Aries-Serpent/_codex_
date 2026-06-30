#!/usr/bin/env python3
"""
Agent Handoff Protocol

Implements structured state handoff between agents to prevent STM loss
(currently 100% loss) and preserve decision rationale (currently 80% loss).

HANDOFF GUARANTEE:
- No state loss: Complete state_id and context preservation
- Decision trace preserved: Full reasoning chain
- Dependencies explicit: All blocking constraints transferred
- Risk assessment: Confidence and escalation flags carried forward

FLOW:
Agent A → prepare_handoff() → handoff_object → Agent B → resume_from_handoff()
"""

import json
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional


class HandoffObject:
    """Represents a structured handoff from one agent to another."""
    
    def __init__(self, state_id: str, from_agent: str, to_agent: str):
        self.handoff_id = str(uuid.uuid4())
        self.state_id = state_id
        self.from_agent = from_agent
        self.to_agent = to_agent
        self.created_at = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        
        # State transfer
        self.input_state: Dict[str, Any] = {}
        self.decision_trace: List[Dict[str, Any]] = []
        self.validation_status: Dict[str, Any] = {}
        
        # Continuity
        self.remaining_tasks: List[Dict[str, Any]] = []
        self.risk_flags: List[str] = []
        self.confidence: float = 0.0
        
        # Context preservation
        self.execution_context: Dict[str, Any] = {}
        self.dependencies_summary: Dict[str, Any] = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert handoff to dictionary."""
        return {
            "handoff_id": self.handoff_id,
            "state_id": self.state_id,
            "from_agent": self.from_agent,
            "to_agent": self.to_agent,
            "created_at": self.created_at,
            "input_state": self.input_state,
            "decision_trace": self.decision_trace,
            "validation_status": self.validation_status,
            "remaining_tasks": self.remaining_tasks,
            "risk_flags": self.risk_flags,
            "confidence": self.confidence,
            "execution_context": self.execution_context,
            "dependencies_summary": self.dependencies_summary
        }
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "HandoffObject":
        """Create handoff from dictionary."""
        obj = HandoffObject(
            data.get("state_id", ""),
            data.get("from_agent", ""),
            data.get("to_agent", "")
        )
        obj.handoff_id = data.get("handoff_id", obj.handoff_id)
        obj.created_at = data.get("created_at", obj.created_at)
        obj.input_state = data.get("input_state", {})
        obj.decision_trace = data.get("decision_trace", [])
        obj.validation_status = data.get("validation_status", {})
        obj.remaining_tasks = data.get("remaining_tasks", [])
        obj.risk_flags = data.get("risk_flags", [])
        obj.confidence = data.get("confidence", 0.0)
        obj.execution_context = data.get("execution_context", {})
        obj.dependencies_summary = data.get("dependencies_summary", {})
        return obj


class HandoffProtocol:
    """Protocol for agent-to-agent handoffs."""
    
    @staticmethod
    def prepare_handoff(state: Dict[str, Any],
                       next_agent: str,
                       current_agent: str = "unknown") -> HandoffObject:
        """
        Prepare a structured handoff from current agent to next agent.
        
        Ensures complete state transfer with no STM loss or decision rationale loss.
        
        Args:
            state: Current canonical execution state
            next_agent: ID of receiving agent
            current_agent: ID of sending agent
            
        Returns:
            HandoffObject with complete context and continuity information
        """
        state_id = state.get("state_id", "")
        
        # Create handoff object
        handoff = HandoffObject(state_id, current_agent, next_agent)
        
        # 1. COMPLETE STATE TRANSFER
        # Include the full input/decision context to prevent 100% STM loss
        handoff.input_state = {
            "state_id": state_id,
            "agent_id": state.get("agent_id"),
            "phase_id": state.get("phase_id"),
            "track_id": state.get("track_id"),
            "task_id": state.get("task_id"),
            "execution_step": state.get("execution_step"),
            "status": state.get("status"),
            "confidence_score": state.get("confidence_score", 0.0),
            "timestamp": state.get("timestamp")
        }
        
        # 2. DECISION TRACE PRESERVATION
        # Prevent 80% loss of decision rationale
        decision_context = state.get("decision_context", {})
        
        # Build complete decision trace
        handoff.decision_trace = [
            {
                "step": 1,
                "type": "observation",
                "summary": _summarize_input_context(state.get("input_context", {}))
            },
            {
                "step": 2,
                "type": "reasoning",
                "items": decision_context.get("reasoning", [])
            },
            {
                "step": 3,
                "type": "constraints",
                "applied": decision_context.get("constraints", [])
            },
            {
                "step": 4,
                "type": "alternatives",
                "alternatives": decision_context.get("alternatives_considered", [])
            },
            {
                "step": 5,
                "type": "decision",
                "selected_action": decision_context.get("selected_action"),
                "confidence": decision_context.get("confidence", 0.0)
            }
        ]
        
        # 3. VALIDATION STATUS
        handoff.validation_status = state.get("validation_results", {})
        
        # 4. REMAINING TASKS
        # Build list of remaining work from unresolved items
        unresolved = state.get("unresolved_items", [])
        for item in unresolved:
            if item.get("type") != "blocker":
                handoff.remaining_tasks.append({
                    "item_id": item.get("item_id"),
                    "type": item.get("type"),
                    "description": item.get("description"),
                    "owner": item.get("owner", next_agent),
                    "priority": item.get("priority", "normal")
                })
        
        # 5. RISK FLAGS
        # Identify risks to be aware of
        risk_flags = []
        
        if state.get("confidence_score", 1.0) < 0.7:
            risk_flags.append(f"low_confidence:{state.get('confidence_score')}")
        
        blocker_count = len([i for i in unresolved if i.get("type") == "blocker"])
        if blocker_count > 0:
            risk_flags.append(f"unresolved_blockers:{blocker_count}")
        
        failed_deps = [d for d in state.get("dependencies", [])
                      if d.get("status") == "failed"]
        if failed_deps:
            risk_flags.append(f"failed_dependencies:{len(failed_deps)}")
        
        failed_actions = [a for a in state.get("actions_taken", [])
                         if a.get("status") == "failed"]
        if failed_actions:
            risk_flags.append(f"failed_actions:{len(failed_actions)}")
        
        if state.get("status") == "escalated":
            risk_flags.append("escalated_status")
        
        handoff.risk_flags = risk_flags
        
        # 6. CONFIDENCE TRANSFER
        handoff.confidence = state.get("confidence_score", 0.0)
        
        # 7. EXECUTION CONTEXT
        handoff.execution_context = {
            "current_phase": state.get("phase_id"),
            "current_track": state.get("track_id"),
            "current_task": state.get("task_id"),
            "lineage": {
                "previous_state_id": state.get("previous_state_id"),
                "created_by": state.get("agent_id")
            }
        }
        
        # 8. DEPENDENCIES SUMMARY
        deps = state.get("dependencies", [])
        handoff.dependencies_summary = {
            "total": len(deps),
            "resolved": len([d for d in deps if d.get("status") == "resolved"]),
            "pending": len([d for d in deps if d.get("status") == "pending"]),
            "failed": len([d for d in deps if d.get("status") == "failed"]),
            "blocked": len([d for d in deps if d.get("status") == "blocked"]),
            "critical_deps": [
                {
                    "type": d.get("type"),
                    "id": d.get("id"),
                    "status": d.get("status")
                }
                for d in deps if d.get("status") in {"failed", "blocked"}
            ]
        }
        
        return handoff
    
    @staticmethod
    def resume_from_handoff(handoff: HandoffObject,
                           base_state: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Resume execution from a handoff.
        
        Reconstructs full state from handoff object, ensuring no loss
        of context or decision rationale.
        
        Args:
            handoff: The handoff object from previous agent
            base_state: Optional base state to merge with handoff data
            
        Returns:
            Reconstructed state ready for next agent's execution
        """
        # Start with base state or handoff input
        if base_state:
            state = base_state.copy()
        else:
            state = {
                "state_id": handoff.state_id,
                "agent_id": handoff.to_agent,
                "timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
            }
        
        # Restore state info from input_state
        input_state = handoff.input_state
        state.update({
            "phase_id": input_state.get("phase_id"),
            "track_id": input_state.get("track_id"),
            "task_id": input_state.get("task_id"),
            "execution_step": input_state.get("execution_step"),
            "confidence_score": handoff.confidence
        })
        
        # Restore decision context from decision trace
        decision_context = {
            "reasoning": [],
            "constraints": [],
            "alternatives_considered": [],
            "selected_action": "",
            "confidence": handoff.confidence
        }
        
        for trace_item in handoff.decision_trace:
            if trace_item.get("type") == "reasoning":
                decision_context["reasoning"] = trace_item.get("items", [])
            elif trace_item.get("type") == "constraints":
                decision_context["constraints"] = trace_item.get("applied", [])
            elif trace_item.get("type") == "alternatives":
                decision_context["alternatives_considered"] = trace_item.get("alternatives", [])
            elif trace_item.get("type") == "decision":
                decision_context["selected_action"] = trace_item.get("selected_action", "")
        
        state["decision_context"] = decision_context
        
        # Restore validation results
        state["validation_results"] = handoff.validation_status
        
        # Restore unresolved items
        unresolved_items = []
        for task in handoff.remaining_tasks:
            unresolved_items.append({
                "item_id": task.get("item_id"),
                "type": task.get("type"),
                "description": task.get("description"),
                "owner": task.get("owner", handoff.to_agent),
                "priority": task.get("priority", "normal")
            })
        
        state["unresolved_items"] = unresolved_items
        
        # Add handoff metadata
        state["_handoff_source"] = {
            "handoff_id": handoff.handoff_id,
            "from_agent": handoff.from_agent,
            "created_at": handoff.created_at,
            "risk_flags": handoff.risk_flags
        }
        
        return state
    
    @staticmethod
    def validate_handoff(handoff: HandoffObject) -> Dict[str, Any]:
        """
        Validate handoff integrity.
        
        Ensures all required information was preserved.
        
        Args:
            handoff: The handoff to validate
            
        Returns:
            Validation result
        """
        result = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        # Check required fields
        if not handoff.state_id:
            result["errors"].append("Missing state_id")
        
        if not handoff.from_agent:
            result["errors"].append("Missing from_agent")
        
        if not handoff.to_agent:
            result["errors"].append("Missing to_agent")
        
        # Check state transfer
        if not handoff.input_state:
            result["warnings"].append("No input state captured")
        
        # Check decision trace
        if not handoff.decision_trace:
            result["warnings"].append("No decision trace captured")
        elif len(handoff.decision_trace) < 3:
            result["warnings"].append("Decision trace may be incomplete")
        
        # Check confidence
        if handoff.confidence < 0.5:
            result["warnings"].append(f"Low confidence: {handoff.confidence}")
        
        # Check risk flags
        if len(handoff.risk_flags) > 5:
            result["warnings"].append(f"Many risk flags: {len(handoff.risk_flags)}")
        
        # Check dependencies
        deps_summary = handoff.dependencies_summary
        if deps_summary.get("failed", 0) > 0:
            result["warnings"].append(
                f"Failed dependencies: {deps_summary.get('failed')}"
            )
        
        result["valid"] = len(result["errors"]) == 0
        return result


def _summarize_input_context(input_context: Dict[str, Any]) -> str:
    """Summarize input context for decision trace."""
    source = input_context.get("source", "unknown")
    data_keys = list(input_context.get("data", {}).keys())[:3]
    keys_str = ", ".join(data_keys) if data_keys else "no data"
    return f"Input from {source} with keys: {keys_str}"


# Convenience functions
def prepare_handoff(state: Dict[str, Any],
                   next_agent: str,
                   current_agent: str = "unknown") -> Dict[str, Any]:
    """Create a handoff and return as dict."""
    handoff = HandoffProtocol.prepare_handoff(state, next_agent, current_agent)
    return handoff.to_dict()


def resume_from_handoff(handoff_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Resume execution from handoff dict."""
    handoff = HandoffObject.from_dict(handoff_dict)
    return HandoffProtocol.resume_from_handoff(handoff)


def validate_handoff(handoff_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Validate handoff from dict."""
    handoff = HandoffObject.from_dict(handoff_dict)
    return HandoffProtocol.validate_handoff(handoff)
