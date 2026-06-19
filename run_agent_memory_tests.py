
import sys
import pytest

# Run tests for agent_memory
result = pytest.main([
    "tests/agents/test_agent_memory.py",
    "tests/agents/test_agent_memory_comprehensive.py",
    "tests/agents/test_agent_memory_mutation_killers.py",
    "-v", "--tb=short", "-x"
])

sys.exit(result)
