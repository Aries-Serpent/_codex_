"""
Sample test inputs and fixtures for agent testing.
"""

# Control flow test inputs
CONTROL_FLOW_INPUTS = {
    "basic": {
        "input": "test input",
        "config": {"mode": "test"}
    },
    "with_metadata": {
        "input": "test",
        "metadata": {"source": "test", "priority": "high"}
    }
}

# Integration test inputs
INTEGRATION_INPUTS = {
    "multi_agent": {
        "agents": ["agent1", "agent2"],
        "workflow": "sequential"
    },
    "handoff": {
        "from_agent": "agent1",
        "to_agent": "agent2",
        "data": {"result": "test"}
    }
}

# Quality test inputs
QUALITY_INPUTS = {
    "format_check": {
        "output": {"status": "success", "data": {}}
    },
    "performance": {
        "iterations": 10,
        "timeout_ms": 5000
    }
}

# Edge case inputs
EDGE_CASES = {
    "empty": {
        "input": "",
        "data": []
    },
    "large": {
        "input": "x" * 100000,
        "data": list(range(10000))
    },
    "null": {
        "input": None,
        "data": None
    }
}

# Error case inputs
ERROR_CASES = {
    "invalid_type": {
        "input": 123,
        "data": object()
    },
    "missing_required": {
        # Missing 'input' field
        "data": []
    },
    "invalid_config": {
        "config": {"invalid_key": "value"}
    }
}
