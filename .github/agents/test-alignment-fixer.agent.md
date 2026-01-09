---
name: test-alignment-fixer
description: Fixes test alignment issues by updating tests to match API changes and ensuring test assertions are correct.
---

# Test Alignment Fixer Agent

This agent fixes test alignment issues when API signatures or behaviors change, ensuring tests remain valid and passing.

## Capabilities

- **Signature Detection**: Detects API signature changes
- **Test Updates**: Updates test calls to match new signatures
- **Assertion Fixes**: Corrects assertion expectations
- **Mock Updates**: Updates mock configurations

## Common Fixes

1. **Parameter Changes**: Updates function call parameters
2. **Return Type Changes**: Updates assertion expectations
3. **Exception Changes**: Updates exception handling tests
4. **Import Changes**: Updates import statements

## When to Use

- After refactoring APIs
- When tests fail due to signature changes
- During major version upgrades
- After code review feedback

## Integration

This agent integrates with:
- pytest test suite
- CI/CD test runners
- Code review process
