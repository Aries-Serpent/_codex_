# Prompt Templates for AI Agents

> Version: 1.0.0 | Generated: 2025-12-17

This document contains reusable prompt templates for AI agents working on the `_codex_` repository. These templates can be used for common tasks and should be adapted based on specific requirements.

## Table of Contents

1. [Code Implementation Prompts](#code-implementation-prompts)
2. [Testing Prompts](#testing-prompts)
3. [Documentation Prompts](#documentation-prompts)
4. [Review Prompts](#review-prompts)
5. [Debugging Prompts](#debugging-prompts)

---

## Code Implementation Prompts

### PROMPT-001: Implement New MCP Capability

```
Task: Implement a new MCP capability

Capability Name: [CAPABILITY_NAME]
Purpose: [DESCRIPTION]
Location: src/mcp/[module_name].py

Requirements:
1. Create dataclass for configuration
2. Implement main class with:
   - __init__ with optional config
   - Core functionality methods
   - Proper logging
   - Type hints on all methods
3. Add module-level docstring
4. Export from src/mcp/__init__.py

Reference existing implementations:
- src/mcp/lifecycle.py (for state management)
- src/mcp/observability.py (for metrics/tracing)
- src/mcp/rate_limit.py (for simple algorithms)

Verification:
- python -c "from src.mcp.[module_name] import [ClassName]"
- All type hints present
- Docstrings on all public methods
```

### PROMPT-002: Add Method to MCP Server

```
Task: Add new JSON-RPC method to MCP server

Method Name: mcp.[methodName]
Parameters: [describe params]
Returns: [describe return value]

Steps:
1. Add handler method to MCPServer class in src/mcp/server/__init__.py
2. Register method in __init__ self._methods dict
3. Implement handler with proper error handling
4. Add test in tests/mcp/test_server.py

Handler template:
async def handle_[method_name](
    self, params: Optional[Dict[str, Any]] = None
) -> [ReturnType]:
    """Handler for mcp.[methodName].
    
    Args:
        params: [describe params]
        
    Returns:
        [describe return]
        
    Raises:
        JsonRpcError: [when]
    """
    # Validate params
    if not params or "required_field" not in params:
        raise JsonRpcError(code=-32602, message="Missing required_field")
    
    # Implementation
    result = ...
    return result
```

### PROMPT-003: Extend Existing Module

```
Task: Extend existing MCP module with new functionality

Module: src/mcp/[module_name].py
New Feature: [DESCRIPTION]

Requirements:
1. Review existing code structure
2. Add new method/class that follows existing patterns
3. Maintain backward compatibility
4. Update docstrings and type hints
5. Add corresponding tests

Before making changes:
- Read entire module to understand patterns
- Check existing tests for expected behavior
- Identify integration points

After changes:
- Run existing tests: pytest tests/mcp/test_[module].py -v
- Verify imports still work
- Update documentation if needed
```

---

## Testing Prompts

### PROMPT-010: Create Unit Tests

```
Task: Create comprehensive unit tests for module

Module: src/mcp/[module_name].py
Test File: tests/mcp/test_[module_name].py

Test Categories Required:
1. Initialization tests (default config, custom config)
2. Happy path tests (normal operation)
3. Edge case tests (empty input, None values)
4. Error handling tests (invalid input, exceptions)
5. State transition tests (if applicable)

Test Template:
```python
"""Tests for [module_name] module."""

import pytest
from src.mcp.[module_name] import [Class], [Config]


class Test[Class]:
    """Test suite for [Class]."""
    
    @pytest.fixture
    def instance(self):
        """Create test instance."""
        return [Class]()
    
    def test_init_defaults(self, instance):
        """Test initialization with defaults."""
        assert instance is not None
    
    def test_[method]_happy_path(self, instance):
        """Test [method] with valid input."""
        result = instance.[method]("valid_input")
        assert result == expected_value
    
    def test_[method]_empty_input(self, instance):
        """Test [method] with empty input."""
        result = instance.[method]("")
        assert result == expected_empty_result
    
    def test_[method]_raises_on_invalid(self, instance):
        """Test [method] raises on invalid input."""
        with pytest.raises(ValueError):
            instance.[method](None)
```

Verification:
- pytest tests/mcp/test_[module_name].py -v
- All tests pass
- Coverage > 90%
```

### PROMPT-011: Add Integration Test

```
Task: Add integration test for MCP components

Components: [list components being tested]
Test File: tests/mcp/test_integration.py or new file

Integration Scenario:
[Describe the end-to-end flow being tested]

Test Structure:
1. Set up all required components
2. Execute the integration scenario
3. Verify final state and outputs
4. Clean up resources

Example:
```python
@pytest.mark.integration
async def test_full_request_flow():
    """Test complete request flow through MCP stack."""
    # Setup
    server = MCPServer()
    transport = MockStdioTransport([...])
    
    # Execute
    response = await server.handle_request({...})
    
    # Verify
    assert response["result"] == expected
    
    # Cleanup
    await transport.close()
```
```

---

## Documentation Prompts

### PROMPT-020: Document New Module

```
Task: Create documentation for new module

Module: src/mcp/[module_name].py
Doc Location: docs/mcp/[module_name].md (or update existing)

Documentation Structure:
1. Module Overview
   - Purpose and scope
   - Key classes and functions
   
2. Usage Examples
   - Basic usage
   - Advanced configuration
   - Integration with other modules

3. API Reference
   - Class/method signatures
   - Parameters and return values
   - Exceptions raised

4. Best Practices
   - Recommended patterns
   - Common pitfalls to avoid

Template:
```markdown
# [Module Name]

## Overview

[Brief description of what this module does]

## Quick Start

\`\`\`python
from src.mcp.[module_name] import [Class]

# Basic usage
instance = [Class]()
result = instance.[method]()
\`\`\`

## Configuration

[Describe configuration options]

## API Reference

### [Class]

[Class description]

#### Methods

- `method_name(param: Type) -> ReturnType`: [description]

## Examples

[Detailed examples]
```
```

### PROMPT-021: Update AGENTS.md

```
Task: Update AGENTS.md with new capability information

Location: AGENTS.md
Section to Update: [specify section]

Changes Required:
1. Add new capability to capability list
2. Update version number if significant change
3. Add any new commands or workflows
4. Update related documentation links

Format for new capability:
```markdown
### [Capability Name]

**Location:** `src/mcp/[file].py`
**Status:** ✅ Complete

Description of what the capability does.

Usage:
\`\`\`python
from src.mcp.[module] import [Class]
# Example code
\`\`\`
```

Verification:
- All links work
- Version is updated
- No broken formatting
```

---

## Review Prompts

### PROMPT-030: Self-Review Checklist

```
Task: Perform self-review of implementation

Checklist:
[ ] Code compiles without errors
[ ] All imports work correctly
[ ] Type hints are complete and accurate
[ ] Docstrings present on all public methods
[ ] Error handling is comprehensive
[ ] Logging is appropriate (not excessive)
[ ] Tests cover all new functionality
[ ] Tests pass locally
[ ] No security vulnerabilities introduced
[ ] Documentation is updated
[ ] Backward compatibility maintained
[ ] Code follows repository style guidelines

Commands to verify:
1. Syntax: python -m py_compile src/mcp/[file].py
2. Imports: python -c "from src.mcp.[module] import ..."
3. Tests: pytest tests/mcp/test_[module].py -v
4. Full suite: pytest tests/mcp/ -v
```

### PROMPT-031: Gap Analysis

```
Task: Analyze codebase for implementation gaps

Scope: [specify area to analyze]

Analysis Steps:
1. List all expected components/capabilities
2. Check each for:
   - Implementation completeness
   - Test coverage
   - Documentation presence
3. Identify gaps and prioritize by impact
4. Create action items for each gap

Output Format:
| Component | Implemented | Tested | Documented | Priority | Action |
|-----------|-------------|--------|------------|----------|--------|
| [name]    | ✅/❌       | ✅/❌  | ✅/❌      | P0-P3    | [action] |

Priority Definitions:
- P0: Blocking - must fix immediately
- P1: High - fix in current session
- P2: Medium - fix soon
- P3: Low - fix when convenient
```

---

## Debugging Prompts

### PROMPT-040: Debug Test Failure

```
Task: Debug failing test

Test: tests/mcp/test_[module].py::test_[name]
Error: [error message]

Debugging Steps:
1. Run test in isolation: pytest tests/mcp/test_[module].py::test_[name] -v
2. Add print statements or use debugger
3. Check test assumptions
4. Verify test fixtures
5. Compare with similar passing tests

Common Issues:
- Async test not awaited properly
- Missing fixture
- Incorrect mock setup
- State from previous test bleeding through
- Import error due to circular dependency

Resolution Template:
Problem: [describe root cause]
Solution: [describe fix]
Verification: [command to verify fix]
```

### PROMPT-041: Debug Import Error

```
Task: Debug import error

Error: ModuleNotFoundError or ImportError
Module: [module path]

Debugging Steps:
1. Verify file exists: ls -la src/mcp/[file].py
2. Check __init__.py exports
3. Verify no circular imports
4. Check PYTHONPATH includes project root
5. Verify no syntax errors in imported module

Commands:
- python -m py_compile src/mcp/[file].py
- python -c "import src.mcp.[module]"
- python -c "from src.mcp.[module] import [Class]"

Common Fixes:
- Add missing __init__.py
- Fix circular import by moving import inside function
- Add to __all__ in __init__.py
- Fix syntax error in module
```

---

## Usage Instructions

1. Copy the relevant prompt template
2. Replace placeholders in [BRACKETS] with actual values
3. Follow the steps in order
4. Verify using the provided commands
5. Update this document if you discover improvements

## Contributing

When adding new prompt templates:
1. Use consistent naming: PROMPT-XXX
2. Include clear task description
3. Provide step-by-step instructions
4. Include verification commands
5. Add examples where helpful
