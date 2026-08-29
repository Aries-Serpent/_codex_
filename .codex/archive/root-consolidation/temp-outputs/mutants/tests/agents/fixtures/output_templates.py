"""
Expected output templates for agent test validation.
"""

# Success outputs
SUCCESS_OUTPUT_TEMPLATE = {
    "status": "success",
    "data": {
        # Agent-specific data
    },
    "metadata": {
        "execution_time_ms": 100,
        "timestamp": "2024-01-01T00:00:00Z"
    }
}

# Partial success outputs
PARTIAL_OUTPUT_TEMPLATE = {
    "status": "partial",
    "data": {
        "completed": 0,
        "failed": 0,
        "results": []
    },
    "warnings": [],
    "metadata": {
        "execution_time_ms": 100
    }
}

# Error outputs
ERROR_OUTPUT_TEMPLATE = {
    "status": "error",
    "error": "Error message",
    "code": "ERROR_CODE",
    "details": {
        "type": "error_type",
        "traceback": ""
    },
    "metadata": {
        "execution_time_ms": 50
    }
}

# Execution context output
EXECUTION_CONTEXT_TEMPLATE = {
    "agent_id": "agent-001",
    "agent_type": "test",
    "session_id": "session-001",
    "status": "completed",
    "started_at": "2024-01-01T00:00:00Z",
    "completed_at": "2024-01-01T00:00:01Z",
    "duration_ms": 1000
}

# Multi-agent orchestration output
ORCHESTRATION_OUTPUT_TEMPLATE = {
    "status": "success",
    "orchestration": {
        "workflow": "sequential",
        "agents_executed": ["agent1", "agent2"],
        "total_duration_ms": 2000
    },
    "results": {
        "agent1": {"status": "success", "data": {}},
        "agent2": {"status": "success", "data": {}}
    }
}

# Handoff output
HANDOFF_OUTPUT_TEMPLATE = {
    "status": "success",
    "handoff": {
        "from_agent": "agent1",
        "to_agent": "agent2",
        "data_passed": {}
    },
    "result": {"status": "success", "data": {}}
}
