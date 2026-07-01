#!/usr/bin/env python3
"""
Copilot Tool Contract Specification

Standardized interface for all Copilot tools operating on canonical execution states.

KEY PRINCIPLE:
All tools MUST operate only on structured data (canonical state schema).
No markdown files, no implicit context, no unstructured reasoning.

TOOL CATEGORIES:
1. Context Retrieval: get_agent_context, get_task_brief
2. State Operations: validate_state_tool, checkpoint_state, resume_state
3. Agent Coordination: handoff_state
4. Universal Query: query_state (replaces ad-hoc file reads)
"""

import json
from typing import Any, Dict, Optional


class CopilotToolContract:
    """Base contract for Copilot tools."""
    
    @staticmethod
    def validate_input(**kwargs) -> Dict[str, Any]:
        """Validate tool input parameters."""
        return {"valid": True, "errors": []}
    
    @staticmethod
    def ensure_structured_output(result: Any) -> Dict[str, Any]:
        """Ensure output is valid JSON/dict."""
        if isinstance(result, dict):
            return result
        elif isinstance(result, str):
            try:
                return json.loads(result)
            except json.JSONDecodeError:
                return {"error": "Output is not valid JSON", "raw_output": result}
        else:
            return {"error": f"Output type {type(result)} not supported"}


class ContextRetrievalTools:
    """Tools for retrieving agent and task context."""
    
    @staticmethod
    def get_agent_context(agent_id: str) -> Dict[str, Any]:
        """
        Get current context for an agent.
        
        Returns agent state, current phase, execution step, and next actions.
        
        Args:
            agent_id: The agent identifier
            
        Returns:
            {
                "agent_id": str,
                "current_state_id": str,
                # observe|context|decide|act|validate|persist|handoff|complete
                "execution_step": str,
                "phase": str,
                "track": str,
                "task": str,
                "status": str,
                "confidence": float,
                "dependencies": [],    # Blocking dependencies
                "next_actions": [],    # Proposed next steps
                "requires_validation": bool,
                "risk_flags": [],
                "checkpoint_available": bool,
                "last_checkpoint_id": str|null
            }
        """
        # In real implementation, would load from state storage/checkpoint manager
        return {
            "agent_id": agent_id,
            "current_state_id": "state-id-placeholder",
            "execution_step": "decide",
            "phase": "phase-10",
            "track": "track-001",
            "task": "task-001",
            "status": "in_progress",
            "confidence": 0.85,
            "dependencies": [],
            "next_actions": ["validate_state", "create_checkpoint"],
            "requires_validation": True,
            "risk_flags": [],
            "checkpoint_available": False,
            "last_checkpoint_id": None
        }
    
    @staticmethod
    def get_task_brief(task_id: str) -> Dict[str, Any]:
        """
        Get task brief from structured state, NOT markdown files.
        
        Returns task metadata, objectives, constraints, and acceptance criteria.
        
        Args:
            task_id: The task identifier
            
        Returns:
            {
                "task_id": str,
                "title": str,
                "description": str,
                "phase": str,
                "track": str,
                "status": str,
                "objectives": [str],
                "constraints": [str],
                "acceptance_criteria": [str],
                "owner": str,
                "dependencies": [str],
                "priority": str,
                "estimated_effort": str,
                "current_progress": float,
                "blockers": []
            }
        """
        # In real implementation, would load from canonical state storage
        # NOT from markdown files
        return {
            "task_id": task_id,
            "title": "Example Task",
            "description": "Task description loaded from canonical state",
            "phase": "phase-10",
            "track": "track-001",
            "status": "in_progress",
            "objectives": [
                "Objective 1",
                "Objective 2"
            ],
            "constraints": [
                "Constraint 1",
                "Constraint 2"
            ],
            "acceptance_criteria": [
                "Criterion 1",
                "Criterion 2"
            ],
            "owner": "agent-orchestrator",
            "dependencies": ["dep-1", "dep-2"],
            "priority": "high",
            "estimated_effort": "8 hours",
            "current_progress": 0.5,
            "blockers": []
        }


class StateOperationTools:
    """Tools for state validation, checkpointing, and resumption."""
    
    @staticmethod
    def validate_state_tool(state_id: str) -> Dict[str, Any]:
        """
        Validate a canonical state.
        
        Returns validation results from validation_engine.
        
        Args:
            state_id: The state to validate
            
        Returns:
            {
                "state_id": str,
                "valid": bool,
                "violations": [
                    {
                        "rule": str,
                        "severity": str,  # critical|high|medium|low
                        "message": str,
                        "field": str (optional)
                    }
                ],
                "warnings": [str],
                "confidence_adjustment": float,
                "requires_escalation": bool,
                "next_action": str
            }
        """
        # In real implementation, would call validation_engine.validate_state()
        from scripts.core import validate_state
        
        # Would load state from storage using state_id
        state = {"state_id": state_id}  # Placeholder
        
        validation = validate_state(state)
        return {
            "state_id": state_id,
            **validation
        }
    
    @staticmethod
    def checkpoint_state(state_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a checkpoint of the current state.
        
        Persists state to checkpoint storage with metadata.
        
        Args:
            state_dict: The state to checkpoint
            
        Returns:
            {
                "checkpoint_id": str,
                "state_id": str,
                "created_at": str,
                "status": str,
                "location": str,
                "lineage_depth": int,
                "can_rollback": bool
            }
        """
        # In real implementation, would call checkpoint_manager.create_checkpoint()
        from scripts.core import create_checkpoint
        
        checkpoint_id = create_checkpoint(state_dict)
        
        return {
            "checkpoint_id": checkpoint_id,
            "state_id": state_dict.get("state_id"),
            "created_at": state_dict.get("timestamp"),
            "status": "created",
            "location": f"docs-data/runtime/checkpoints/{checkpoint_id}.json",
            "lineage_depth": 1,
            "can_rollback": True
        }
    
    @staticmethod
    def resume_state(checkpoint_id: str) -> Dict[str, Any]:
        """
        Resume execution from a checkpoint.
        
        Restores full state for continuation.
        
        Args:
            checkpoint_id: The checkpoint to resume from
            
        Returns:
            {
                "checkpoint_id": str,
                "restored_state": {},  # Full canonical state
                "execution_step": str,
                "status": str,
                "confidence": float,
                "lineage_depth": int,
                "ready_to_continue": bool
            }
        """
        # In real implementation, would call checkpoint_manager.resume_execution()
        from scripts.core import resume_execution
        
        restored_state = resume_execution(checkpoint_id)
        
        return {
            "checkpoint_id": checkpoint_id,
            "restored_state": restored_state,
            "execution_step": restored_state.get("execution_step"),
            "status": restored_state.get("status"),
            "confidence": restored_state.get("confidence_score"),
            "lineage_depth": 1,
            "ready_to_continue": True
        }


class AgentCoordinationTools:
    """Tools for multi-agent coordination and handoffs."""
    
    @staticmethod
    def handoff_state(
        state_id: str,
        from_agent: str,
        to_agent: str
    ) -> Dict[str, Any]:
        """
        Prepare state handoff from one agent to another.
        
        Ensures no STM loss or decision rationale loss.
        
        Args:
            state_id: The state to hand off
            from_agent: Current agent
            to_agent: Next agent
            
        Returns:
            {
                "handoff_id": str,
                "state_id": str,
                "from_agent": str,
                "to_agent": str,
                "created_at": str,
                "handoff_object": {},  # Full handoff with decision trace
                "validation_status": {},
                "risk_flags": [],
                "confidence": float,
                "ready_for_transfer": bool
            }
        """
        # In real implementation, would call handoff_protocol.prepare_handoff()
        from scripts.core import prepare_handoff
        
        # Would load state from storage
        state = {"state_id": state_id}  # Placeholder
        
        handoff = prepare_handoff(state, to_agent, from_agent)
        
        return {
            "handoff_id": handoff.get("handoff_id"),
            "state_id": state_id,
            "from_agent": from_agent,
            "to_agent": to_agent,
            "created_at": handoff.get("created_at"),
            "handoff_object": handoff,
            "validation_status": handoff.get("validation_status"),
            "risk_flags": handoff.get("risk_flags"),
            "confidence": handoff.get("confidence"),
            "ready_for_transfer": True
        }


class UniversalQueryTool:
    """Universal query abstraction for state data access."""
    
    @staticmethod
    def query_state(
        query: str,
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Universal query interface for structured state data.
        
        Replaces:
        ❌ direct file reads
        ❌ implicit context reasoning
        ✅ structured state queries
        
        Args:
            query: Query string (e.g., "state.decision_context.reasoning")
            filters: Optional filters (e.g., {"phase": "phase-10", "status": "in_progress"})
            
        Returns:
            {
                "query": str,
                "filters": dict,
                "results": [],
                "count": int,
                "query_status": str,
                "query_time_ms": float
            }
        """
        # Supported query patterns:
        # - "state.field" - Access state field
        # - "state.nested.field" - Access nested field
        # - "states.filter(phase='phase-10')" - Filter states
        # - "dependencies.status('resolved')" - Filter dependencies
        # - "actions.by_status('failed')" - Filter actions
        
        filters = filters or {}
        
        query_patterns = {
            "state.decision_context": "Get decision context from current state",
            "state.validation_results": "Get validation results",
            "state.confidence_score": "Get confidence score",
            "state.unresolved_items": "Get unresolved items",
            "dependencies.status": "Filter dependencies by status",
            "actions.by_status": "Filter actions by status",
            "checkpoints.list": "List checkpoints for current track",
            "handoffs.list": "List recent handoffs",
        }
        
        return {
            "query": query,
            "filters": filters,
            "results": [],
            "count": 0,
            "query_status": "supported",
            "query_time_ms": 0.0,
            "query_patterns": query_patterns
        }


# Tool Contract Compliance Checklist
TOOL_CONTRACT_COMPLIANCE = {
    "must_requirements": [
        "✓ Tool operates ONLY on structured data (canonical state schema)",
        "✓ Tool returns deterministic JSON output",
        "✓ Tool does NOT read markdown files",
        "✓ Tool does NOT depend on implicit context",
        "✓ Tool supports validation before use",
        "✓ Tool supports persistence after use",
        "✓ Tool includes lineage tracking",
        "✓ Tool includes error handling with structured errors",
    ],
    "should_requirements": [
        "✓ Tool documents input/output schemas",
        "✓ Tool validates all inputs",
        "✓ Tool includes confidence scores",
        "✓ Tool flags risk conditions",
        "✓ Tool enables audit trails",
        "✓ Tool supports rollback",
    ],
    "deprecated_patterns": [
        "❌ Direct file system reads",
        "❌ Implicit README parsing",
        "❌ Unstructured markdown extraction",
        "❌ Context-dependent logic",
        "❌ Non-deterministic outputs",
        "❌ Stateful tool behavior",
    ]
}


def get_tool_documentation() -> Dict[str, Any]:
    """Get documentation for all Copilot tools."""
    return {
        "tools": {
            "get_agent_context": ContextRetrievalTools.get_agent_context.__doc__,
            "get_task_brief": ContextRetrievalTools.get_task_brief.__doc__,
            "validate_state_tool": StateOperationTools.validate_state_tool.__doc__,
            "checkpoint_state": StateOperationTools.checkpoint_state.__doc__,
            "resume_state": StateOperationTools.resume_state.__doc__,
            "handoff_state": AgentCoordinationTools.handoff_state.__doc__,
            "query_state": UniversalQueryTool.query_state.__doc__,
        },
        "compliance": TOOL_CONTRACT_COMPLIANCE,
        "schema_reference": "docs-data/canonical/state_schema.json"
    }
